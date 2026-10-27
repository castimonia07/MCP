from mcp.server.fastmcp import FastMCP

mcp= FastMCP("Math")

@mcp.tool()
def add(a:int,b:int)->int:
    "_summary_: Adds two numbers"
    return a+b

@mcp.tool()
def muply(a:int,b:int)->int:
    "_summary_: Multiplies two numbers"
    return a*b

## The transport="stdio" tells the server to:
## 1. Read requests from standard input (stdin)
## 2. Write responses to standard output (stdout)
if __name__ == "__main__":
    print("Starting MCP server...", file=__import__("sys").stderr)
    mcp.run(transport="stdio")