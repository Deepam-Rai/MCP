import streamlit as st
import requests
import json
import asyncio
from typing import Dict, List, Optional
from mcp import ClientSession
from mcp.client.sse import sse_client


class OllamaClient:
    """Simple Client for communicating with local Ollama Instance"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_models(self):
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except requests.exceptions.RequestException:
            pass
        return []
    
    def chat(self, model: str, messages: List[Dict], stream: bool = True):
        """Send chat request to Ollama"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=stream,
                timeout=60
            )
            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json().get("message", {}).get("content", "No response")
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"
    
    def _handle_stream_response(self, response):
        """Handle streaming response from Ollama"""
        full_response = ""
        try:
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if chunk.get("message", {}).get("content"):
                        content = chunk["message"]["content"]
                        full_response += content
                        yield content
                    if chunk.get("done", False):
                        break
        except json.JSONDecodeError:
            yield "Error parsing response from Ollama"
        
        return full_response


class MCPClient:
    """Client for communicating with MCP Server"""
    
    def __init__(self, mcp_url: str = "http://localhost:8000/sse"):
        self.mcp_url = mcp_url
        self.available_tools = []
        self._session = None
    
    def is_available(self) -> bool:
        """Check if MCP server is available"""
        try:
            import asyncio
            return asyncio.run(self._check_availability())
        except Exception:
            return False
    
    async def _check_availability(self) -> bool:
        """Async helper to check availability"""
        try:
            async with sse_client(url=self.mcp_url) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    return True
        except Exception:
            return False
    
    def get_tools(self) -> List[Dict]:
        """Get available tools from MCP server"""
        try:
            import asyncio
            return asyncio.run(self._get_tools())
        except Exception:
            return []
    
    async def _get_tools(self) -> List[Dict]:
        """Async helper to get tools"""
        try:
            async with sse_client(url=self.mcp_url) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    self.available_tools = tools.tools
                    return [{"name": tool.name, "description": tool.description} for tool in tools.tools]
        except Exception:
            return []
    
    def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Call a tool on the MCP server"""
        try:
            import asyncio
            return asyncio.run(self._call_tool(tool_name, arguments))
        except Exception as e:
            return f"Error calling tool: {str(e)}"
    
    async def _call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Async helper to call tool"""
        try:
            async with sse_client(url=self.mcp_url) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=arguments)
                    return result.content[0].text if result.content else "No result"
        except Exception as e:
            return f"Error calling tool: {str(e)}"


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ollama_client" not in st.session_state:
        st.session_state.ollama_client = OllamaClient()
    if "mcp_client" not in st.session_state:
        st.session_state.mcp_client = MCPClient()
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    if "mcp_tools" not in st.session_state:
        st.session_state.mcp_tools = []
    if "mcp_enabled" not in st.session_state:
        st.session_state.mcp_enabled = False


def display_chat_messages():
    """Display chat messages in the main area"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def parse_tool_calls(text: str) -> List[Dict]:
    """Parse tool calls from LLM response"""
    tool_calls = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('TOOL_CALL:'):
            try:
                tool_data = line[10:].strip()  # Remove 'TOOL_CALL:' prefix
                tool_call = json.loads(tool_data)
                tool_calls.append(tool_call)
            except json.JSONDecodeError:
                continue
    
    return tool_calls


def execute_tool_calls(tool_calls: List[Dict], mcp_client: MCPClient) -> str:
    """Execute tool calls and return results"""
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get('name')
        arguments = tool_call.get('arguments', {})
        
        if tool_name:
            result = mcp_client.call_tool(tool_name, arguments)
            results.append(f"**{tool_name}** result: {result}")
    
    return "\n\n".join(results) if results else ""


def create_system_prompt(available_tools: List[Dict]) -> str:
    """Create system prompt with tool information"""
    if not available_tools:
        return ""
    
    tools_info = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in available_tools])
    
    return f"""You have access to the following tools:

{tools_info}

To use a tool, include a line in your response with the format:
TOOL_CALL: {{"name": "tool_name", "arguments": {{"arg1": "value1", "arg2": "value2"}}}}

You can use multiple tools in a single response. The tool results will be shown to the user after your response.

Example:
I'll calculate that for you.
TOOL_CALL: {{"name": "calculator", "arguments": {{"expression": "2 + 3 * 4"}}}}

Always provide context around tool usage and explain what you're doing."""


def handle_user_input():
    """Handle user input and generate response"""
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            if st.session_state.selected_model:
                # Create message container for streaming
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    # Prepare messages with system prompt if MCP is enabled
                    messages = st.session_state.messages.copy()
                    if st.session_state.mcp_enabled and st.session_state.mcp_tools:
                        system_prompt = create_system_prompt(st.session_state.mcp_tools)
                        if system_prompt:
                            messages = [{"role": "system", "content": system_prompt}] + messages
                    
                    # Get response from Ollama
                    response_stream = st.session_state.ollama_client.chat(
                        model=st.session_state.selected_model,
                        messages=messages
                    )
                    
                    # Stream the response
                    for chunk in response_stream:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    # Final response without cursor
                    message_placeholder.markdown(full_response)
                    
                    # Check for tool calls if MCP is enabled
                    if st.session_state.mcp_enabled:
                        tool_calls = parse_tool_calls(full_response)
                        if tool_calls:
                            with st.spinner("Executing tools..."):
                                tool_results = execute_tool_calls(tool_calls, st.session_state.mcp_client)
                                if tool_results:
                                    st.markdown("---")
                                    st.markdown("**Tool Results:**")
                                    st.markdown(tool_results)
                                    full_response += f"\n\n---\n**Tool Results:**\n{tool_results}"
                
                except Exception as e:
                    full_response = f"Error: {str(e)}"
                    message_placeholder.markdown(full_response)
            else:
                full_response = "Please select a model in the sidebar first"
                st.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


def setup_sidebar():
    """Setup sidebar with model selection and controls"""
    with st.sidebar:
        st.title("Ollama + MCP Chatbot")
        
        # Ollama Section
        st.subheader("🦙 Ollama")
        if st.session_state.ollama_client.is_available():
            st.success("Ollama is running")
            # Model selection
            models = st.session_state.ollama_client.get_models()
            if models:
                selected_model = st.selectbox(
                    "Select Model",
                    models,
                    index=0 if st.session_state.selected_model is None else models.index(st.session_state.selected_model) if st.session_state.selected_model in models else 0
                )
                st.session_state.selected_model = selected_model
                st.info(f"Using: {selected_model}")
            else:
                st.warning("No models available. Pull a model first using: `ollama pull qwen2.5`")
        else:
            st.error("Ollama not available")
            st.markdown("""
            **To start Ollama:**
            1. Install Ollama from https://ollama.ai
            2. Run `ollama serve` in terminal
            3. Pull a model: `ollama pull qwen2.5`
            """)
        
        st.divider()
        
        # MCP Section
        st.subheader("🔧 MCP Tools")
        
        # Check MCP availability
        if st.button("Check MCP Server", use_container_width=True):
            with st.spinner("Checking MCP server..."):
                mcp_available = st.session_state.mcp_client.is_available()
                if mcp_available:
                    st.session_state.mcp_tools = st.session_state.mcp_client.get_tools()
                    st.success("MCP server is available")
                else:
                    st.error("MCP server not available")
                    st.session_state.mcp_tools = []
        
        # MCP Enable/Disable
        st.session_state.mcp_enabled = st.checkbox("Enable MCP Tools", value=st.session_state.mcp_enabled)
        
        # Display available tools
        if st.session_state.mcp_tools:
            st.success(f"{len(st.session_state.mcp_tools)} tools available")
            with st.expander("Available Tools"):
                for tool in st.session_state.mcp_tools:
                    st.write(f"**{tool['name']}**: {tool['description']}")
        else:
            st.info("No MCP tools available")
            st.markdown("""
            **To start MCP server:**
            1. Run `python mcp_server_sse.py`
            2. Click "Check MCP Server" above
            """)
        
        st.divider()

        # Chat controls
        st.subheader("💬 Chat Controls")
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Chat statistics
        if st.session_state.messages:
            st.subheader("📊 Chat Stats")
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            st.metric("Messages", f"{user_messages + assistant_messages}")
            st.metric("User", user_messages)
            st.metric("Assistant", assistant_messages)


def main():
    """Main application function"""
    st.set_page_config(
        page_title="Ollama + MCP Chatbot",
        page_icon="🤖",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Setup sidebar
    setup_sidebar()

    # Main chat area
    st.title("Chat with Ollama + MCP Tools")
    
    if st.session_state.mcp_enabled and st.session_state.mcp_tools:
        st.info(f"🔧 MCP Tools enabled ({len(st.session_state.mcp_tools)} available)")
    
    # Display existing messages
    display_chat_messages()

    # Handle user input
    handle_user_input()


if __name__ == "__main__":
    main()
    