import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.ingest import ingest_pdfs
from app.agent import create_agent, run_agent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_FOLDER = os.path.join(BASE_DIR, "pdfs")
VECTORSTORE_PATH = os.path.join(BASE_DIR, "vectorstore")

st.set_page_config(
    page_title="Multi-Tool AI Assistant",
    page_icon="🤖",        # ← Change this to any emoji you want
)

st.title("Multi-Tool AI Assistant")
st.caption("Upload PDFs → Ask anything. LLM decides: RAG or Web Search.")

# ── Pick your icons here ──────────────────────────────────
USER_ICON    = "👤"   # shown next to user questions
AI_ICON      = "🤖"   # shown next to AI answers
# ─────────────────────────────────────────────────────────

# Sidebar
with st.sidebar:
    st.header("📄 Upload PDFs")
    uploaded_files = st.file_uploader(
        "Upload one or more PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        os.makedirs(PDF_FOLDER, exist_ok=True)
        for f in uploaded_files:
            with open(os.path.join(PDF_FOLDER, f.name), "wb") as out:
                out.write(f.read())
        st.success(f"{len(uploaded_files)} PDF(s) saved.")

    if st.button("🔄 Ingest PDFs"):
        if not os.path.exists(PDF_FOLDER) or not any(f.endswith(".pdf") for f in os.listdir(PDF_FOLDER)):
            st.error("No PDFs found. Please upload at least one PDF first.")
        else:
            with st.spinner("Processing PDFs..."):
                ingest_pdfs(PDF_FOLDER)
            st.success("PDFs ingested! Reloading agent...")
            st.session_state.client = create_agent()

    st.divider()
    st.caption("Vectorstore exists: " + str(os.path.exists(VECTORSTORE_PATH)))
    if os.path.exists(PDF_FOLDER):
        pdfs = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
        st.caption(f"PDFs: {pdfs}")

# Auto-load agent on startup
if "client" not in st.session_state:
    if os.path.exists(VECTORSTORE_PATH):
        with st.spinner("Loading agent..."):
            st.session_state.client = create_agent()
    else:
        st.session_state.client = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show status
if st.session_state.client is None:
    st.warning("⚠️ No vector store found. Please upload and ingest a PDF first.")
else:
    st.success("✅ Agent ready!")

# Display chat history
for msg in st.session_state.messages:
    icon = USER_ICON if msg["role"] == "user" else AI_ICON
    with st.chat_message(msg["role"], avatar=icon):
        if msg.get("tool"):
            st.caption(f"Tool used: {msg['tool']}")
        st.write(msg["content"])

# Handle new input
if prompt := st.chat_input("Ask anything..."):
    if st.session_state.client is None:
        st.warning("Please ingest a PDF first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_ICON):
            st.write(prompt)

        with st.chat_message("assistant", avatar=AI_ICON):
            with st.spinner("Thinking..."):
                try:
                    answer, tool_used = run_agent(st.session_state.client, prompt)
                except Exception as e:
                    answer = f"⚠️ Error: {str(e)}"
                    tool_used = "error"
            st.caption(f"Tool used: {tool_used}")
            st.write(answer)
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "tool": tool_used
            })