"""
Simple MCP Client for testing the MCP server
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, List, Optional, Any
import uuid

class MCPClient:
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process = None
        self.tools = []
    
    async def start(self):
        """Start the MCP server process"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the connection
        await self.initialize()
        
        # Get available tools
        await self.list_tools()
    
    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
    
    async def send_message(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Send a message to the MCP server"""
        if not self.process:
            raise RuntimeError("MCP server not started")
        
        message = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {}
        }
        
        # Send message
        message_json = json.dumps(message) + "\n"
        self.process.stdin.write(message_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response_json = response_line.decode().strip()
        
        if not response_json:
            raise RuntimeError("No response from MCP server")
        
        return json.loads(response_json)
    
    async def initialize(self):
        """Initialize the MCP connection"""
        response = await self.send_message("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        
        if "error" in response:
            raise RuntimeError(f"Initialization failed: {response['error']}")
        
        print("✅ MCP server initialized successfully")
        return response
    
    async def list_tools(self):
        """Get list of available tools"""
        response = await self.send_message("tools/list")
        
        if "error" in response:
            raise RuntimeError(f"Failed to list tools: {response['error']}")
        
        self.tools = response["result"]["tools"]
        print(f"📋 Available tools: {len(self.tools)}")
        for tool in self.tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        return self.tools
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Call a specific tool"""
        response = await self.send_message("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        # Extract text content from response
        content = response["result"]["content"]
        if content and len(content) > 0:
            return content[0]["text"]
        
        return "No response content"

async def test_mcp_server():
    """Test the MCP server with various tool calls"""
    print("🚀 Starting MCP Server Test")
    print("=" * 50)
    
    # Start MCP client
    client = MCPClient([sys.executable, "mcp_server.py"])
    
    try:
        await client.start()
        
        # Test 1: Calculator
        print("\n🧮 Testing Calculator:")
        result = await client.call_tool("calculator", {"expression": "2 + 3 * 4"})
        print(f"2 + 3 * 4 = {result}")
        
        result = await client.call_tool("calculator", {"expression": "sqrt(16) + pi"})
        print(f"sqrt(16) + pi = {result}")
        
        # Test 2: System Info
        print("\n🖥️  Testing System Info:")
        result = await client.call_tool("system_info", {"info_type": "time"})
        print(result)
        
        result = await client.call_tool("system_info", {"info_type": "cwd"})
        print(result)
        
        # Test 3: File Operations
        print("\n📁 Testing File Operations:")
        
        # Write a test file
        test_content = "Hello from MCP!\nThis is a test file.\nLine 3 here."
        result = await client.call_tool("file_writer", {
            "file_path": "test_output.txt",
            "content": test_content
        })
        print(result)
        
        # Read the file back
        result = await client.call_tool("file_reader", {"file_path": "test_output.txt"})
        print(result)
        
        # List files in current directory
        result = await client.call_tool("list_files", {"directory": "."})
        print(result)
        
        # Test 4: Error handling
        print("\n❌ Testing Error Handling:")
        try:
            result = await client.call_tool("calculator", {"expression": "invalid + syntax"})
        except RuntimeError as e:
            print(f"Expected error caught: {e}")
        
        try:
            result = await client.call_tool("file_reader", {"file_path": "nonexistent.txt"})
        except RuntimeError as e:
            print(f"Expected error caught: {e}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        await client.stop()
        print("\n🛑 MCP server stopped")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())