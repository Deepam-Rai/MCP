# MCP Chatbot Integration
A Streamlit-powered chatbot UI that connects to [Ollama](https://ollama.ai) for local LLM inference and an MCP server for tool calling (calculator, file operations, system time, etc).


---

## 🦙 Ollama Setup

1. **Install Ollama:**  
   [Download Ollama](https://ollama.ai) and follow installation instructions for your OS.

2. **Pull a model:**  
   Example:
   ```shell
   ollama pull qwen2.5
   ```

3. **List available models:**
   ```shell
   ollama list
   ```

4. **Start Ollama service:**
   ```shell
   ollama serve
   ```

---


## 🛠️ MCP Server Setup

The MCP server exposes tools for the chatbot to call.

1. **Start the MCP server:**
   ```shell
   python mcp_server_sse.py
   ```

   Tools available:
   - `calculator`: Evaluate math expressions
   - `file_reader`: Read text files
   - `file_writer`: Write text to files
   - `system_time`: Get current system time
   - `list_files`: List files in a directory

---

## 🚀 Run the Chatbot App

1. **Install dependencies:**
   ```shell
   pip install -r requirements.txt
   ```

2. **Start the Streamlit app:**
   ```shell
   streamlit run app.py --server.runOnSave=true
   ```

---

## 📁 Project Structure

- `app.py` — Streamlit chatbot UI
- `mcp_server_sse.py` — MCP server with tool definitions
- `requirements.txt` — Python dependencies

---

## 📝 Notes

- Ollama must be running locally with at least one model pulled.
- MCP server must be running for tool calling.
- Tool calls are parsed from LLM responses and executed automatically.