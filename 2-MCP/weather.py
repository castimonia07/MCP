from mcp.server.fastmcp import FastMCP

mcp= FastMCP("Weather")

@mcp.tool()
async def get_weather(city:str)->str:
    "_summary_: Gets the current weather for a given city"
    # Here you would implement the logic to get the weather for the city

if __name__=="__main__":
    mcp.run(transport="streamable-http")