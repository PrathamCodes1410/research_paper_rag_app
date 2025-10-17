import os
from pathlib import Path
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import fitz 
import shutil

TEMP_DIR = Path("temp")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2" 
LLM_MODEL = "ggml-gpt4all-j-v1.3-groovy.bin"  

def extract_text_and_figures(pdf_path: str, out_dir: str):
    """Extract text + figure paths from PDF."""
    doc = fitz.open(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    text_chunks = []
    figure_paths = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        text_chunks.append({"page": page_num, "text": text})

        images = page.get_images(full=True)
        for i, img in enumerate(images):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n > 4:  
                pix = fitz.Pixmap(fitz.csRGB, pix)
            fig_path = out_dir / f"fig_page{page_num}_{i}.png"
            pix.save(str(fig_path))
            figure_paths.append(str(fig_path))

    return text_chunks, figure_paths


def init_vector_db(session_id: str):
    session_path = TEMP_DIR / session_id / "db"
    session_path.mkdir(parents=True, exist_ok=True)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return Chroma(persist_directory=session_path, embedding_function=embeddings)


def add_chunks_to_db(vector_db, text_chunks):
    docs = [Document(page_content=c["text"], metadata={"page": c["page"]}) for c in text_chunks]
    vector_db.add_documents(docs)


def ask_local_llm(vector_db, question, figures=None):
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name=LLM_MODEL, temperature=0),
        chain_type="stuff",
        retriever=retriever
    )

    context = qa.run(question)

    if figures:
        fig_refs = "\nFigures:\n" + "\n".join(figures[:2])
        context += fig_refs

    return context


# --- Cleanup ---
def cleanup_session(session_id: str):
    session_path = TEMP_DIR / session_id
    if session_path.exists():
        shutil.rmtree(session_path)
