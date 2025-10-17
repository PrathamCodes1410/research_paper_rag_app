import streamlit as st
from app.parsers import extract_text_and_figures
from app.rag import init_vector_db, add_chunks_to_db, ask_gemini
from app.feedback import init_db, add_feedback

st.set_page_config(page_title="Multimodal RAG - Gemini", layout="wide")
st.title("Multimodal RAG System for Scientific Papers")

init_db()
vector_db = init_vector_db()

uploaded_file = st.file_uploader("Upload a scientific PDF", type=["pdf"])
if uploaded_file:
    with open(f"data/papers/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.read())
    text_chunks, figs = extract_text_and_figures(f"data/papers/{uploaded_file.name}", "data/figures")
    add_chunks_to_db(vector_db, text_chunks)
    st.success("Paper processed and indexed ✅")

question = st.text_input("Ask a question about the paper")
if question:
    results = vector_db.similarity_search(question, k=5)
    answer = ask_gemini(question, results, figures=figs[:2])  # demo with top 2 figures
    st.markdown(f"### 🧠 Gemini Answer:\n{answer}")

    st.markdown("Feedback:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Good answer"):
            for r in results:
                add_feedback(str(r.metadata.get("page")), question, 1)
    with col2:
        if st.button("👎 Bad answer"):
            for r in results:
                add_feedback(str(r.metadata.get("page")), question, -1)
