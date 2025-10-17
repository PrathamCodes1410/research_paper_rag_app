import google.generativeai as genai
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from app.config import GEMINI_API_KEY, CHROMA_DB_PATH

genai.configure(api_key=GEMINI_API_KEY)

# Use LangChain for retrieval, Gemini for reasoning
def init_vector_db():
    return Chroma(
        collection_name="papers",
        embedding_function=OpenAIEmbeddings(),  # or switch to a Gemini embed model once public
        persist_directory=CHROMA_DB_PATH
    )

def add_chunks_to_db(vector_db, text_chunks):
    docs = [Document(page_content=c['text'], metadata={"page": c['page']}) for c in text_chunks]
    vector_db.add_documents(docs)

def ask_gemini(question, retrieved_docs, figures=None):
    context_text = "\n\n".join([d.page_content for d in retrieved_docs])
    input_parts = [
        {"role": "system", "parts": "You are a research assistant that cites figures and text."},
        {"role": "user", "parts": [
            {"text": f"Question: {question}\n\nContext:\n{context_text}"}
        ]}
    ]
    if figures:
        for fig in figures:
            input_parts[1]["parts"].append({"inline_data": {"mime_type": "image/png", "data": open(fig, "rb").read()}})

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(input_parts)
    return response.text
