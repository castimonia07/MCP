import json
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPClient:

    def __init__(self, config_file="browser_mcp.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.client = MultiServerMCPClient(self.config["mcpServers"])
        self.tools = []

    def _load_config(self):
        with open(self.config_file, "r", encoding="utf-8") as file:
            return json.load(file)

    async def discover_tools(self):
        self.tools = await self.client.get_tools()
        return self.tools