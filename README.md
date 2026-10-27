# 🌐 Model Context Protocol (MCP) & AI Agent Guardrails

A comprehensive hands-on implementation and guide to **Model Context Protocol (MCP)** with **Python**, **LangChain**, **LangGraph**, **FastMCP**, and **Streamlit**.

This repository covers everything from MCP fundamentals, connecting third-party tool servers (Playwright, Airbnb, DuckDuckGo), authoring custom FastMCP servers, to building autonomous ReAct agents with guardrails and modern user interfaces.

---

## 📑 Table of Contents

- [What is Model Context Protocol (MCP)?](#-what-is-model-context-protocol-mcp)
  - [The Core Problem MCP Solves](#the-core-problem-mcp-solves)
  - [Architecture: Host, Client, and Server](#architecture-host-client-and-server)
  - [MCP Transports (stdio vs. HTTP/SSE)](#mcp-transports-stdio-vs-httpsse)
- [Repository Structure](#-repository-structure)
- [Module Breakdown](#-module-breakdown)
  - [1. 1-MCP: Streamlit Multi-Server AI Assistant](#1-1-mcp-streamlit-multi-server-ai-assistant)
  - [2. 2-MCP: Custom FastMCP Servers & LangGraph ReAct Agent](#2-2-mcp-custom-fastmcp-servers--langgraph-react-agent)
  - [3. Configuration & VS Code MCP Setup](#3-configuration--vs-code-mcp-setup)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Virtual Environment](#installation--virtual-environment)
  - [Environment Variables](#environment-variables)
- [Running the Applications](#-running-the-applications)
  - [Running the Streamlit UI (1-MCP)](#running-the-streamlit-ui-1-mcp)
  - [Running Custom FastMCP & LangGraph Agent (2-MCP)](#running-custom-fastmcp--langgraph-agent-2-mcp)
- [MCP Servers in this Project](#-mcp-servers-in-this-project)
- [Troubleshooting & Windows Tips](#-troubleshooting--windows-tips)

---

## 🧠 What is Model Context Protocol (MCP)?

The **Model Context Protocol (MCP)** is an open-source standard designed by Anthropic that enables AI applications and LLMs to securely and seamlessly communicate with external tools, APIs, data repositories, and execution environments.

### The Core Problem MCP Solves

Before MCP, integrating tools with LLMs meant writing bespoke client code for every API, dealing with inconsistent schemas, and maintaining custom connectors across different agent frameworks:

```
[ Traditional Approach: O(M × N) Fragmentation ]
LLM App 1 ───► Custom Airbnb API client
LLM App 2 ───► Custom Browser script
LLM App 3 ───► Custom Database connector

[ MCP Standard: O(M + N) Clean Interoperability ]
LLM App / Client ───► [ Standardized MCP Protocol ] ───► Any MCP Server
```

With MCP:
- **Write Once, Use Anywhere**: A single MCP server (e.g., Playwright, DuckDuckGo, Database) can be consumed by LangChain, LangGraph, Claude Desktop, Cursor, VS Code, or custom clients.
- **Dynamic Tool Discovery**: Clients query the MCP server at runtime to inspect available tools, parameters, descriptions, and required arguments.
- **Security Boundaries**: The server controls tool execution and resource exposure; clients only interact via agreed protocols.

### Architecture: Host, Client, and Server

```
┌────────────────────────────────────────────────────────┐
│                      MCP HOST                          │
│  (e.g., Streamlit App, LangGraph, VS Code, Claude)     │
│                                                        │
│   ┌────────────────────────────────────────────────┐   │
│   │               MCP CLIENT                       │   │
│   │      (MultiServerMCPClient / Adapters)         │   │
│   └──────────────────────┬─────────────────────────┘   │
└──────────────────────────┼─────────────────────────────┘
                           │ Protocol Messages (JSON-RPC)
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  MCP Server  │    │  MCP Server  │    │  MCP Server  │
│ (Playwright) │    │   (Airbnb)   │    │ (Custom Math)│
└──────────────┘    └──────────────┘    └──────────────┘
```

1. **Host**: The orchestrating runtime (Streamlit, CLI, LangChain agent).
2. **Client**: Connects to one or more MCP servers, translates JSON-RPC protocols, and surfaces tools to the LLM.
3. **Server**: A lightweight service providing **Tools** (executable functions), **Resources** (structured data), and **Prompts** (pre-templated instructions).

### MCP Transports (stdio vs. HTTP/SSE)

- **`stdio` (Standard Input/Output)**:
  - The MCP client spawns the server as a local child process.
  - JSON-RPC requests/responses are exchanged over `stdin` and `stdout`.
  - Fast, secure, runs locally without opening network ports.
- **`streamable-http` / `sse` (Server-Sent Events / HTTP Streaming)**:
  - Remote or microservice setup where the server runs as an independent HTTP service.
  - Ideal for multi-user deployments or cloud-hosted tool backends.

---

## 📂 Repository Structure

```text
MCP/
├── 1-MCP/                         # Streamlit Multi-Server Web Application
│   ├── app.py                     # Streamlit web app with dynamic MCP tool invocation
│   ├── browser_mcp.json           # Multi-server MCP configuration file
│   └── client/
│       ├── __init__.py
│       └── mcp_client.py          # MultiServerMCPClient wrapper & tool discovery
│
├── 2-MCP/                         # Custom FastMCP Servers & LangGraph ReAct Client
│   ├── mathserver.py              # Custom Python MCP server using FastMCP (stdio transport)
│   ├── weather.py                 # Custom Weather MCP server (streamable-http transport)
│   └── client.py                  # LangGraph ReAct agent consuming local FastMCP servers
│
├── src/
│   └── mcp_gaurdrails/            # Core package entry point for guardrails & packaging
│       └── __init__.py
│
├── .vscode/
│   └── mcp.json                   # VS Code MCP server integrations
│
├── .env                           # Environment configuration (API keys)
├── pyproject.toml                 # Modern Python packaging & dependencies (uv/pip)
├── requirements.txt               # Pinned pip requirements
└── README.md                      # Project documentation
```

---

## 🔍 Module Breakdown

### 1. `1-MCP`: Streamlit Multi-Server AI Assistant

`1-MCP` is an end-to-end full-stack agent assistant built with **Streamlit** and **LangChain**:

- **Key Files**:
  - `1-MCP/browser_mcp.json`: Declares three external MCP servers:
    1. **Playwright** (`npx.cmd -y @playwright/mcp@latest`): Full browser automation, web navigation, screenshots, DOM inspection.
    2. **Airbnb** (`npx.cmd -y @openbnb/mcp-server-airbnb`): Search listings, query prices, and check accommodation details.
    3. **DuckDuckGo** (`uvx.exe duckduckgo-mcp-server`): Safe web search capabilities.
  - `1-MCP/client/mcp_client.py`: Uses `langchain_mcp_adapters.client.MultiServerMCPClient` to connect to all configured servers concurrently and convert their tools into LangChain-compatible tools.
  - `1-MCP/app.py`:
    - Manages an isolated `AsyncRunner` thread to execute asynchronous agent workflows inside Streamlit's synchronous event loop.
    - Connects to Groq (`openai/gpt-oss-120b` via `ChatOpenAI`).
    - Exposes a chat interface with live tool call introspection in an expandable inspector (`st.expander("🔧 MCP Tool Calls")`).

### 2. `2-MCP`: Custom FastMCP Servers & LangGraph ReAct Agent

`2-MCP` demonstrates how to write your own MCP server from scratch in Python and connect it to a **LangGraph ReAct agent**:

- **`mathserver.py`**:
  - Built with official Python `mcp.server.fastmcp.FastMCP`.
  - Exposes tools:
    - `add(a: int, b: int) -> int`
    - `muply(a: int, b: int) -> int`
  - Uses `transport="stdio"`.
- **`weather.py`**:
  - Demonstrates HTTP transport: `mcp.run(transport="streamable-http")` for serving tools over web endpoints.
- **`2-MCP/client.py`**:
  - Starts the Python math server as a subprocess via `sys.executable`.
  - Dynamically fetches tools using `client.get_tools()`.
  - Binds the tools into `langgraph.prebuilt.create_react_agent` powered by Groq (`ChatGroq`).
  - LLM autonomously decides when to invoke `muply` or `add` to solve mathematical word problems.

### 3. Configuration & VS Code MCP Setup

The `.vscode/mcp.json` file configures VS Code's native MCP integration so your editor's AI assistants can directly use the exact same servers:
- Allows your IDE to run Playwright, query Airbnb, and search DuckDuckGo directly within editing workflows.

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+** (Python 3.12 / 3.14 supported).
2. **Node.js & npm** (required to run `npx` for Playwright and Airbnb MCP servers).
3. **uv** (recommended fast package manager, optional but supported via `pyproject.toml`).
4. **Groq API Key**: Needed to power the fast open-weights LLMs (`openai/gpt-oss-120b`).

### Installation & Virtual Environment

You can install dependencies using either `uv` or standard `pip`:

#### Option A: Using `uv` (Recommended)
```bash
# Sync environment with uv
uv sync
```

#### Option B: Using standard Python `venv` & `pip`
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create or update your `.env` file in the workspace root:

```env
GROQ_API_KEY="your-groq-api-key-here"
```

---

## 💻 Running the Applications

### Running the Streamlit UI (`1-MCP`)

Launch the web interface:

```bash
streamlit run 1-MCP/app.py
```

1. Open your browser at `http://localhost:8501`.
2. Inspect the sidebar to view active MCP servers (`playwright`, `airbnb`, `ddg-search`) and dynamically discovered tools.
3. Ask prompts such as:
   - *"Search for cozy apartments in Paris under $150 on Airbnb."*
   - *"Search DuckDuckGo for the latest advancements in Model Context Protocol."*
   - *"Navigate to https://example.com using Playwright and report the page title."*
4. Click on **"🔧 MCP Tool Calls"** at the bottom of the chat to inspect the raw tool payloads and results!

---

### Running Custom FastMCP & LangGraph Agent (`2-MCP`)

Run the custom LangGraph ReAct agent which connects to `mathserver.py`:

```bash
python 2-MCP/client.py
```

**How it executes:**
1. The client launches `2-MCP/mathserver.py` as an MCP sub-process over `stdio`.
2. Client queries the server for tools and discovers `add` and `muply`.
3. The ReAct agent receives the prompt `"What is 2*9*12?"`.
4. The LLM invokes the MCP `muply` tool through JSON-RPC and produces the final answer: `216`.

To test the `weather.py` server independently over HTTP streaming:
```bash
python 2-MCP/weather.py
```

---

## 🛠️ MCP Servers in this Project

| Server Name | Transport | Runtime / Command | Purpose |
| :--- | :--- | :--- | :--- |
| **`playwright`** | `stdio` | `npx -y @playwright/mcp@latest` | Headless browser execution, navigation, screenshots, scraping |
| **`airbnb`** | `stdio` | `npx -y @openbnb/mcp-server-airbnb` | Querying real-time accommodation, pricing, and amenities |
| **`ddg-search`**| `stdio` | `uvx duckduckgo-mcp-server` | Web search querying via DuckDuckGo |
| **`Math`** | `stdio` | `python 2-MCP/mathserver.py` | Custom FastMCP math calculation server (`add`, `muply`) |
| **`Weather`** | `streamable-http` | `python 2-MCP/weather.py` | Custom FastMCP server over HTTP streamable transport |

---

## 🛡️ Guardrails & Best Practices

1. **Tool Execution Boundaries**:
   - MCP servers isolate execution. When running tools like Playwright or shell commands, execution happens within explicit commands rather than arbitrary code execution on the host machine.
2. **Safe Search & Regional Configs**:
   - DuckDuckGo MCP server accepts explicit environment variables (`DDG_SAFE_SEARCH: STRICT`) to enforce content safety at the protocol boundary.
3. **Structured Schemas**:
   - FastMCP uses Python type hints (`int`, `str`, `float`) to auto-generate valid JSON-Schema specifications, preventing malformed tool inputs before reaching python execution.
4. **Asynchronous Concurrency**:
   - The custom `AsyncRunner` ensures that long-running network tools (scraping, browser automation) never freeze the UI thread or cause event-loop deadlocks.

---

## 🔧 Troubleshooting & Windows Tips

- **`npx.cmd` vs `npx` on Windows**:
  - In `1-MCP/browser_mcp.json` and `.vscode/mcp.json`, Windows requires `npx.cmd` rather than `npx` when invoking Node binaries from Python subprocesses.
- **`uvx.exe` on Windows**:
  - Ensure `uv` is installed and added to your system `PATH`. On Windows, referencing `uvx.exe` or `uvx` ensures the DuckDuckGo server runs without shell errors.
- **Missing `GROQ_API_KEY`**:
  - If the agent fails to initialize, ensure `.env` is located in the working directory from which you execute `streamlit` or `python`.

---

## 📜 License & Credits

Built with ❤️ using:
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [LangChain](https://python.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Streamlit](https://streamlit.io/)
- [Groq](https://groq.com/)
