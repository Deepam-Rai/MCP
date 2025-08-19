# QuickStart
A very basic quick start code to get started with MCP.

# Setting Up Environment
```shell
# Create new python environment
conda create -n mcp python=3.11
# Activate the environment
conda activate mcp

# Install dependencies
uv pip install -r requirements.txt
```

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
- Introduction: https://modelcontextprotocol.io/introduction
- MCP vs API: https://medium.com/@tahirbalarabe2/model-context-protocol-mcp-vs-apis-the-new-standard-for-ai-integration-d6b9a7665ea7
- Quickstart: https://github.com/modelcontextprotocol/python-sdk
- Basic tutorial: https://youtu.be/-WogqfxWBbM?si=sfnFFZUdqyPjBsKg
- Python SDK official examples: https://github.com/modelcontextprotocol/python-sdk