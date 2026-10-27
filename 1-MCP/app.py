import asyncio
import os
import threading

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from client.mcp_client import MCPClient


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing from .env")
    st.stop()


llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    temperature=0
)


st.set_page_config(
    page_title="MCP AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 MCP AI Assistant")
st.caption("LangChain + Groq + MCP + Playwright + Airbnb + DuckDuckGo")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "tool_logs" not in st.session_state:
    st.session_state.tool_logs = []

if "tools" not in st.session_state:
    st.session_state.tools = []


class AsyncRunner:

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coroutine):
        future = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.loop
        )
        return future.result()


@st.cache_resource
def get_runner():
    return AsyncRunner()


@st.cache_resource
def get_mcp_client():
    return MCPClient("browser_mcp.json")


runner = get_runner()
mcp_client = get_mcp_client()


async def run_agent(user_message):

    tools = await mcp_client.discover_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are an AI assistant with access to external tools "
            "through MCP. Use MCP tools whenever they are useful. "
            "For browser requests, use Playwright. "
            "For Airbnb requests, use Airbnb tools. "
            "For web searches, use DuckDuckGo tools."
        )
    )

    return await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    })


with st.sidebar:

    st.header("🔌 MCP Servers")

    for server_name in mcp_client.config["mcpServers"]:
        st.success(server_name)

    st.divider()

    st.subheader("Available Tools")

    for tool in st.session_state.tools:
        st.write(f"🔧 `{tool.name}`")


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_message = st.chat_input("Ask me anything...")


if user_message:

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                result = runner.run(
                    run_agent(user_message)
                )

                st.session_state.tools = mcp_client.tools

                final_message = result["messages"][-1]
                final_answer = final_message.content

                st.markdown(final_answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer
                })

                for message in result["messages"]:

                    if message.type == "tool":

                        st.session_state.tool_logs.append({
                            "tool": getattr(
                                message,
                                "name",
                                "Unknown"
                            ),
                            "content": str(message.content)
                        })

            except Exception as error:

                st.error(f"Error: {error}")


if st.session_state.tool_logs:

    with st.expander("🔧 MCP Tool Calls"):

        for log in st.session_state.tool_logs:

            st.write(f"**Tool:** `{log['tool']}`")
            st.write(f"**Result:** {log['content']}")
            st.divider()
