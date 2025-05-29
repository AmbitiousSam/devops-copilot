import streamlit as st
from backend import contextual_assistant
from langchain_community.callbacks import get_openai_callback

st.set_page_config(page_title="DevOps Copilot", page_icon="🛠️")
st.title("🛠️ DevOps Copilot")

# Init session state
for key, default in [("history", []), ("tokens", 0), ("cost", 0.0)]:
    if key not in st.session_state:
        st.session_state[key] = default

# Chat input
query = st.chat_input("Ask a DevOps question…")
if query:
    with st.spinner("Thinking…"):
        with get_openai_callback() as cb:
            answer = contextual_assistant.invoke({"input": query})["output"]

    st.session_state.tokens += cb.total_tokens
    st.session_state.cost   += cb.total_cost
    st.session_state.history.append((query, answer))

# Render chat history
for user, bot in st.session_state.history:
    st.chat_message("user").write(user)
    st.chat_message("assistant").write(bot)

# Sidebar: usage
with st.sidebar:
    st.header("📊 Usage")
    st.write(f"Tokens: {st.session_state.tokens:,}")
    st.write(f"Cost  : ${st.session_state.cost:,.4f}")
