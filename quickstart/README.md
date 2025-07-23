# QuickStart
A very basic quick start code to get started with MCP.

# Running
Install the server on Claude Desktop and use directly:
```
uv run mcp install server.py
# Restart the Claude Desktop
```
Or, test with mcp inspector:
```
# Start the mcp server
mcp dev server.py

# Inside mcp inspector (in browser dashboard)
# Command: uv
# Arguments: run --with mcp mcp run server.py
```

Or, start the server with `sse` transport by:
```
python server.py

# then run quickstart example client.py
# or test with Postman, etc.
```

Run MCP client:
```
python client.py
```

# References
- https://github.com/modelcontextprotocol/python-sdk