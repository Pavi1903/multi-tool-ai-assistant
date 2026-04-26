# Multi-Tool AI Assistant

An AI assistant that automatically routes queries between uploaded PDF documents (RAG) and live web search.

## Features
- Upload PDFs and ask questions from them using RAG
- Automatically falls back to web search when answer is not in documents
- Built with LangChain, FAISS, Groq (Llama 3.3 70B), and Streamlit

## Tech Stack
- **LLM**: Groq (Llama 3.3 70B) — fast inference
- **RAG**: LangChain + FAISS + HuggingFace Embeddings
- **Web Search**: DDGS (DuckDuckGo Search)
- **UI**: Streamlit

## Setup

### 1. Clone the repository
git clone https://github.com/yourusername/multi-tool-ai-assistant.git
cd multi-tool-ai-assistant

### 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up API key
Create a .env file in the root folder:
GROQ_API_KEY=your_groq_api_key_here

Get your free API key at: https://console.groq.com

### 5. Add PDFs and ingest
- Place your PDF files in the pdfs/ folder
- Run: python -m app.ingest

### 6. Run the app
streamlit run app/main.py

## Project Structure
multi-tool-ai-assistant/
├── app/
│   ├── __init__.py
│   ├── ingest.py        # PDF loading, chunking, FAISS indexing
│   ├── rag_tool.py      # RAG retrieval
│   ├── web_tool.py      # DuckDuckGo web search
│   ├── agent.py         # Routing logic + answer generation
│   └── main.py          # Streamlit UI
├── pdfs/                # Place your PDFs here (not tracked by git)
├── vectorstore/         # Auto-generated FAISS index (not tracked by git)
├── .env                 # Your API key (not tracked by git)
├── requirements.txt
└── README.md
