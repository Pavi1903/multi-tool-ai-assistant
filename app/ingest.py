from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

VECTORSTORE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vectorstore")
PDF_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pdfs")

def ingest_pdfs(pdf_folder: str = None):
    if pdf_folder is None:
        pdf_folder = PDF_FOLDER

    all_docs = []

    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_folder, filename)
            loader = PyPDFLoader(path)
            docs = loader.load()
            all_docs.extend(docs)
            print(f"Loaded: {filename} ({len(docs)} pages)")

    if not all_docs:
        raise ValueError("No PDFs found in the pdfs/ folder.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(all_docs)
    print(f"Total chunks: {len(chunks)}")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"Vector store saved to '{VECTORSTORE_PATH}'")

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

if __name__ == "__main__":
    ingest_pdfs()