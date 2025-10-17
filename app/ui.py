import streamlit as st
from pathlib import Path
from app.rag import extract_text_and_figures, init_vector_db, add_chunks_to_db, ask_local_llm, cleanup_session
import uuid
import os

st.set_page_config(page_title="Multimodal Local RAG", layout="wide")
st.title("Multimodal RAG System (Local GPT4All-J)")


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

SESSION_ID = st.session_state.session_id
SESSION_DIR = Path("temp") / SESSION_ID
PDF_DIR = SESSION_DIR / "pdfs"
FIG_DIR = SESSION_DIR / "figures"

PDF_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

vector_db = init_vector_db(SESSION_ID)


uploaded_file = st.file_uploader("Upload a scientific PDF", type=["pdf"])
if uploaded_file:
    pdf_path = PDF_DIR / uploaded_file.name
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    text_chunks, figs = extract_text_and_figures(str(pdf_path), str(FIG_DIR))
    add_chunks_to_db(vector_db, text_chunks)
    st.success("Paper processed and indexed ✅")


question = st.text_input("Ask a question about the paper")
if question and vector_db:
    answer = ask_local_llm(vector_db, question, figures=figs[:2] if uploaded_file else None)
    st.markdown(f"### Local LLM Answer:\n{answer}")


if st.button("End Session & Clean Up"):
    cleanup_session(SESSION_ID)
    st.success("Session cleaned . Restart the app to start a new session.")
