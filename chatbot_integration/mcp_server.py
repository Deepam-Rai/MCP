"""
Basic MCP Server with simple tools for learning
Implements file operations, calculator, and system info tools
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import os
import math

# MCP Protocol classes (simplified implementation)
class MCPMessage:
    def __init__(self, id: str, method: str, params: Optional[Dict] = None):
        self.id = id
        self.method = method
        self.params = params or {}

class MCPResponse:
    def __init__(self, id: str, result: Optional[Dict] = None, error: Optional[Dict] = None):
        self.id = id
        self.result = result
        self.error = error

class BasicMCPServer:
    def __init__(self):
        self.tools = {}
        self.setup_tools()
    
    def setup_tools(self):
        """Register available tools"""
        self.tools = {
            "calculator": {
                "name": "calculator",
                "description": "Perform basic mathematical calculations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                        }
                    },
                    "required": ["expression"]
                }
            },
            "file_reader": {
                "name": "file_reader",
                "description": "Read contents of a text file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            "file_writer": {
                "name": "file_writer",
                "description": "Write text content to a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path where to write the file"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            },
            "system_info": {
                "name": "system_info",
                "description": "Get basic system information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "info_type": {
                            "type": "string",
                            "enum": ["time", "cwd", "env"],
                            "description": "Type of system info: time, cwd (current directory), or env (environment variables)"
                        }
                    },
                    "required": ["info_type"]
                }
            },
            "list_files": {
                "name": "list_files",
                "description": "List files in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list files from (default: current directory)"
                        }
                    }
                }
            }
        }
    
    async def handle_message(self, message_data: Dict) -> Dict:
        """Handle incoming MCP messages"""
        try:
            method = message_data.get("method")
            msg_id = message_data.get("id", "unknown")
            params = message_data.get("params", {})
            
            if method == "initialize":
                return await self.handle_initialize(msg_id, params)
            elif method == "tools/list":
                return await self.handle_list_tools(msg_id)
            elif method == "tools/call":
                return await self.handle_tool_call(msg_id, params)
            else:
                return {
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "id": message_data.get("id", "unknown"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_initialize(self, msg_id: str, params: Dict) -> Dict:
        """Handle MCP initialization"""
        return {
            "id": msg_id,
            "result": {
                "protocolVersion": "0.1.0",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "basic-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def handle_list_tools(self, msg_id: str) -> Dict:
        """Return list of available tools"""
        return {
            "id": msg_id,
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    async def handle_tool_call(self, msg_id: str, params: Dict) -> Dict:
        """Execute a tool call"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        try:
            result = await self.execute_tool(tool_name, arguments)
            return {
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Execute the specified tool with given arguments"""
        if tool_name == "calculator":
            return await self.tool_calculator(arguments)
        elif tool_name == "file_reader":
            return await self.tool_file_reader(arguments)
        elif tool_name == "file_writer":
            return await self.tool_file_writer(arguments)
        elif tool_name == "system_info":
            return await self.tool_system_info(arguments)
        elif tool_name == "list_files":
            return await self.tool_list_files(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def tool_calculator(self, args: Dict) -> str:
        """Basic calculator tool"""
        expression = args.get("expression", "")
        if not expression:
            raise ValueError("Expression is required")
                
        try:
            # Use eval with limited globals for safety (basic implementation)
            safe_dict = {
                "__builtins__": {},
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "sqrt": math.sqrt,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "pi": math.pi, "e": math.e
            }
            result = eval(expression, safe_dict)
            return f"Result: {result}"
        except Exception as e:
            raise ValueError(f"Calculation failed: {str(e)}")
    
    async def tool_file_reader(self, args: Dict) -> str:
        """Read file contents"""
        file_path = args.get("file_path", "")
        if not file_path:
            raise ValueError("File path is required")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return f"File contents of '{file_path}':\n\n{content}"
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    async def tool_file_writer(self, args: Dict) -> str:
        """Write content to file"""
        file_path = args.get("file_path", "")
        content = args.get("content", "")
        
        if not file_path:
            raise ValueError("File path is required")
        
        try:
            directory = os.path.dirname(file_path)
            if directory:  # Only create directory if path contains one
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            return f"Successfully wrote {len(content)} characters to '{file_path}'"
        except Exception as e:
            raise ValueError(f"Error writing file: {str(e)}")
    
    async def tool_system_info(self, args: Dict) -> str:
        """Get system information"""
        info_type = args.get("info_type", "time")
        
        if info_type == "time":
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif info_type == "cwd":
            return f"Current directory: {os.getcwd()}"
        elif info_type == "env":
            # Return a few common environment variables
            env_vars = ["PATH", "HOME", "USER", "PYTHON_VERSION"]
            result = "Environment variables:\n"
            for var in env_vars:
                value = os.environ.get(var, "Not set")
                result += f"  {var}: {value}\n"
            return result
        else:
            raise ValueError(f"Unknown info type: {info_type}")
    
    async def tool_list_files(self, args: Dict) -> str:
        """List files in directory"""
        directory = args.get("directory", ".")
        
        try:
            files = os.listdir(directory)
            if not files:
                return f"Directory '{directory}' is empty"
            
            result = f"Files in '{directory}':\n"
            for file in sorted(files):
                file_path = os.path.join(directory, file)
                if os.path.isdir(file_path):
                    result += f"  📁 {file}/\n"
                else:
                    result += f"  📄 {file}\n"
            
            return result
        except FileNotFoundError:
            raise ValueError(f"Directory not found: {directory}")
        except Exception as e:
            raise ValueError(f"Error listing files: {str(e)}")

class StdioTransport:
    """Handle stdin/stdout communication for MCP"""
    
    def __init__(self, server: BasicMCPServer):
        self.server = server
    
    async def run(self):
        """Main loop for handling MCP messages via stdio"""
        print("MCP Server started. Listening for messages...", file=sys.stderr)
        
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse JSON message
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as e:
                    error_response = {
                        "id": "unknown",
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    continue
                
                # Handle message
                response = await self.server.handle_message(message)
                
                # Send response
                print(json.dumps(response), flush=True)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Transport error: {e}", file=sys.stderr)
                break
        
        print("MCP Server stopped.", file=sys.stderr)

async def main():
    """Main entry point"""
    server = BasicMCPServer()
    transport = StdioTransport(server)
    
    try:
        await transport.run()
    except KeyboardInterrupt:
        print("\nShutting down MCP server...", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())