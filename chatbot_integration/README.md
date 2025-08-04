# Setup Ollama
```shell
# Pull a model
ollama pull llama3.2

# Check locally available models
ollama list

# Start Ollama service
ollama serve 
```

# Run the app
Install dependencies:
```shell
pip install -r requirements.txt
```
Run streamlit app, with dynamic reload:
```shell
streamlit run app.py --server.runOnSave=true
```