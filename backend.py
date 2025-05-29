from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from tools.runbook_search import runbook_search
from tools.pipeline_status import pipeline_status
from dotenv import load_dotenv
load_dotenv()

# 1. LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. Functions-agent prompt
prompt = hub.pull("hwchase17/openai-functions-agent")

# 3. Create agent & executor
agent = create_openai_functions_agent(
    llm=llm,
    tools=[runbook_search, pipeline_status],
    prompt=prompt,
)

research_assistant = AgentExecutor(
    agent=agent,
    tools=[runbook_search, pipeline_status],
    max_iterations=3,
    memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
    verbose=False,
)

# 4. Context-prep (short follow-up fix)
def prepend_last_topic(payload):
    history = payload.get("chat_history", [])
    if len(payload["input"].split()) <= 6 and len(history) >= 2:
        last = history[-2].content
        payload["input"] = f"{last} -> {payload['input']}"
    return payload

contextual_assistant = RunnablePassthrough() | prepend_last_topic | research_assistant
