from langchain_community.tools import tool

_FAQ = {
    "redeploy kubernetes": "Run: kubectl rollout restart deployment <name>",
    "rotate iam key": (
        "1. aws iam create-access-key --user ...\n"
        "2. Update secrets in GitHub.\n"
        "3. aws iam delete-access-key --access-key-id OLD..."
    ),
    "rollback terraform": "Use `terraform state rm` then re-apply desired version tags."
}

def _lookup(query: str) -> str:
    q = query.lower()
    for k, v in _FAQ.items():
        if k in q:
            return v
    return "RUNBOOK_NOT_FOUND"

@tool(
    "RunbookSearch",
    description="Search internal DevOps FAQ / runbooks and return a short answer."
)
def runbook_search(query: str) -> str:
    return _lookup(query)
