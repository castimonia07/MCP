from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import sys

from dotenv import load_dotenv
import os

import asyncio


load_dotenv()

async def main():
    # client= MultiServerMCPClient(
    #     {
    #         "math":{
    #             "command":"python",  # Use the current Python interpreter
    #             "args":["2-MCP/mathserver.py"],  # absolute path
    #             "transport": "stdio"
    #         },
    #         # "weather":{
    #         #     "url":"http://localhost:8000",
    #         #     "transport": "streamable-http",
    #         # }
    #     }
    # )

    client = MultiServerMCPClient(
        {
            "math": {
                "command": sys.executable,
                "args": [
                    r"mathserver.py"
                ],
                "transport": "stdio"
            }
        }
    )

    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

    tools=await client.get_tools()

    model=ChatGroq(
        model="openai/gpt-oss-120b",)

    agent=create_react_agent(
        model,tools
    )

    math_response=await agent.ainvoke(
        {"messages":[{"role":"user","content":"What is the 2*9*12?"}]}
    )
    print("Math resposnse",math_response['messages'][-1].content)

asyncio.run(main())


