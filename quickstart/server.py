"""
FastMCP quickstart example.
"""

from mcp.server.fastmcp import FastMCP


# Create an MCP Server
mcp = FastMCP(name="Demo", host="localhost", port=8000, timeout=30)


# ---------- TOOLS ------------


# Addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two Integers"""
    return a + b


# ---------- RESOURCES ------------


# Static resource
@mcp.resource("resource://static_resource")
def get_static_resource() -> str:
    """Static resource data"""
    return f"Some static data"


# Dynamic resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f'Hello, {name}!'


# ---------- PROMPTS ------------


# Greeting prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f'{styles.get(style, styles["friendly"])} for someone named {name}.'


# ---------- END ------------


if __name__ == "__main__":
    print(f'Starting MCP Server from main script...')
    mcp.run(transport="sse")
