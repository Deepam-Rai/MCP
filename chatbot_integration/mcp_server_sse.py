from typing import Any, Dict, List, Optional
from datetime import datetime
import os
import math
from mcp.server.fastmcp import FastMCP


# Create an MCP Server
mcp = FastMCP(name="Demo", host="localhost", port=8000, timeout=30)


# ---------- TOOLS ------------


@mcp.tool()
def calculator(expression: str) -> str:
    """Perform basic mathematical calculations.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., '2 + 3 * 4')
    """
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


@mcp.tool()
def file_reader(file_path: str) -> str:
    """Read contents of a text file.
    
    Args:
        file_path: Path to the file to read.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return f"File contents of '{file_path}':\n\n{content}"
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")


@mcp.tool()
def file_writer(file_path: str, content: str) -> str:
    """Write text content to a file.
    
    Args:
        file_path: Path where to write the file.
        content: Content to write to the file.
    """
    try:
        directory = os.path.dirname(file_path)
        if directory:  # Only create directory if path contains one
            os.makedirs(directory, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return f"Successfully wrote {len(content)} characters to '{file_path}'"
    except Exception as e:
        raise ValueError(f"Error writing file: {str(e)}")


@mcp.tool()
def system_time() -> str:
    """ Get system time."""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@mcp.tool()
def list_files(directory: Optional[str] = None) -> str:
    """List files in a directory.

    Args:
        directory: Directory path to list files from (default: current directory)
    """
    directory = directory or "."
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
    

if __name__ == "__main__":
    print(f'Starting MCP Server...')
    mcp.run(transport="sse")
