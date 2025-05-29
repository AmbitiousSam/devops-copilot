# tools/pipeline_status.py
import os, requests, datetime
from typing import List
from langchain_community.tools import tool

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
API_URL     = "https://api.github.com"
HEADERS     = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github+json",
}

def _fetch_runs(repo: str, branch: str, per_page: int = 100) -> List[dict]:
    url = f"{API_URL}/repos/{repo}/actions/runs"
    params = {"branch": branch, "per_page": per_page}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("workflow_runs", [])

@tool(
    "PipelineStatus",
    description=(
        "Fetch workflow runs for a repo. "
        "Args:\n"
        "  repo: owner/name\n"
        "  branches: comma-separated names (e.g. main,qa,dev)\n"
        "  days: how many days back to look (default 7)\n"
        "  status: success, failure, or all (default failure)\n"
        "Returns a per-branch list of matching runs with name, time, status, URL."
    )
)
def pipeline_status(
    repo: str,
    branches: str = "main",
    days: int = 7,
    status: str = "failure",
) -> str:
    if not GITHUB_TOKEN:
        return "PIPELINE_ERROR: missing GITHUB_TOKEN"

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    branches_list = [b.strip() for b in branches.split(",") if b.strip()]

    report_lines = []
    statuses = ["success", "failure"] if status.lower() == "all" else [status.lower()]

    for branch in branches_list:
        runs = []
        try:
            all_runs = _fetch_runs(repo, branch, per_page=100)
        except requests.HTTPError as e:
            report_lines.append(f"❌ {branch}: ERROR {e.response.status_code}")
            continue
        # Filter by date & status
        for run in runs:
            concl = (run.get("conclusion") or run.get("status") or "").lower()
            # parse ISO timestamp, drop timezone if present
            run_time = datetime.datetime.fromisoformat(
                run["created_at"].rstrip("Z"))
            if run_time >= cutoff and run.get("conclusion", "").lower() == status.lower():
                runs.append({
                    "name": run["name"],
                    "time": run_time.strftime("%Y-%m-%d %H:%M"),
                    "status": concl,
                    "url":  run["html_url"]
                })

        if not runs:
            report_lines.append(f"✅ {branch}: no {status} runs in last {days} days")
        else:
            report_lines.append(f"❌ {branch}: {len(runs)} {status} run(s):")
            for fr in runs:
                report_lines.append(
                    f"  • {fr['name']} at {fr['time']} UTC → {fr['url']}"
                )

    return "\n".join(report_lines)
