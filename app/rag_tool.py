import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.ingest import load_vectorstore

def rag_search(query: str) -> str:
    try:
        vectorstore = load_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant information found in the uploaded documents."
        return "\n\n".join([
            f"[Page {d.metadata.get('page', '?')}]\n{d.page_content}"
            for d in docs
        ])
    except Exception as e:
        return f"Document search failed: {str(e)}"