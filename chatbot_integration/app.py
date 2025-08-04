import streamlit as st
import requests
import json
from typing import Dict, List, Optional


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


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ollama_client" not in st.session_state:
        st.session_state.ollama_client = OllamaClient()
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None


def display_chat_messages():
    """Display chat messages in the main area"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


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
                # Get response from Ollama
                try:
                    response_stream = st.session_state.ollama_client.chat(
                        model=st.session_state.selected_model,
                        messages=st.session_state.messages
                    )
                    # Stream the response
                    for chunk in response_stream:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    # Final response without cursor
                    message_placeholder.markdown(full_response)
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
        st.title("Ollama Chatbot")
        # Check Ollama availability
        if st.session_state.ollama_client.is_available():
            st.success("Ollama is running.")
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
                st.warning("No models available. Pull a model first using: `ollama pull llama2`")
        else:
            st.error("Ollama not available.")
            st.markdown("""
            **To start Ollama:**
            1. Install Ollama from https://ollama.ai
            2. Run `ollama serve` in terminal
            3. Pull a model: `ollama pull llama2`
            """)
        st.divider()

        # Chat controls
        st.subheader("Chat Controls")
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Chat statistics
        if st.session_state.messages:
            st.subheader("Chat Stats")
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            st.metric("Messages", f"{user_messages + assistant_messages}")
            st.metric("User", user_messages)
            st.metric("Assistant", assistant_messages)


def main():
    """Main application function"""
    st.set_page_config(
        page_title="Ollama Chatbot",
        page_icon="🤖",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Setup sidebar
    setup_sidebar()

    # Main chat area
    st.title("Chat with Ollama")

    # Display existing messages
    display_chat_messages()

    # Handle user input
    handle_user_input()


if __name__ == "__main__":
    main()
