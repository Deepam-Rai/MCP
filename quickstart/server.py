"""
FastMCP quickstart example.
"""

from mcp.server.fastmcp import FastMCP


# Create an MCP Server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two Integers"""
    return a + b


# Add dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f'Hello, {name}!'


# Add a prompt
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f'styles.get(style, styles["friendly"]) for someone named {name}.'
