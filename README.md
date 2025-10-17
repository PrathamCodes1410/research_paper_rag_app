# Multimodal RAG System with Continual Learning for Scientific Paper Understanding

Summary
- A research-focused Retrieval-Augmented Generation (RAG) system for scientific papers that handles text, equations, figures and tables, and improves over time from user feedback.
- Upload PDFs, ask natural-language questions, receive answers with citations to specific figures/equations/sections, and provide corrective feedback to refine retrieval and answers.

Core idea
- Ingest full scientific PDFs (text + LaTeX equations + figures/diagrams + tables).
- Build multimodal embeddings and a retrieval layer so answers cite exact paper artifacts.
- Add a lightweight continual-learning loop: user feedback influences retrieval weighting and answer selection over time.

Key features
- PDF upload and parsing (text, structure, equations, images, captions).
- Multimodal Q&A: answers reference exact pages, figures, equations, and table cells.
- Source citation UI (which passages/figures were used).
- Feedback capture: mark answers correct/incorrect and provide corrections.
- RLHF-lite: feedback updates retrieval weights and context scoring to improve future answers.

Technical highlights
- Multimodal parsing: Nougat (or similar) to extract document structure and equations.
- Vision understanding: Gemini Multimodel for figure/diagram interpretation.
- Orchestration & RAG: LangChain to manage document chunking, prompt templates, and retrieval flow.
- Vector DBs: Chroma or FAISS for embeddings and semantic search (text + image embeddings).
- Simple feedback DB: SQLite/Postgres to persist user feedback and corrected contexts.
- Lightweight weighting mechanism: increment retrieval weights for contexts that lead to correct answers; decay for incorrect ones.

System architecture (high level)
- PDF Ingest → Parser (text, LaTeX eqns, images) → Chunker + Multimodal embeddings → Vector DB
- User Query → Retriever (text + image contexts, weighted) → RAG prompt → Multimodal LLM → Answer + citations
- User Feedback → Feedback DB → Weight updater → Retriever weights adjusted

Quickstart (dev mode)
1. Requirements
	- Python 3.10+
	- API keys for chosen LLMs
	- Optional GPU for local multi-modal models
2. Install
	- pip install -r requirements.txt
	- Set env vars: OPENAI_API_KEY, OTHER_MODEL_KEYS, VECTOR_DB_PATH
3. Run
	- Start vector DB (if using local FAISS/Chroma)
	- python ingest.py --pdfs ./papers
	- streamlit run app.py
4. Minimal usage
	- Upload a PDF in the UI
	- Ask a question in natural language
	- Inspect the answer and cited sources (page, figure number, equation)
	- Mark answer correct/incorrect and optionally submit corrected context

Implementation notes
- Parsing: use a PDF pipeline that extracts text blocks with page/coordinates, LaTeX equations (or images of equations decoded), figure crops and captions.
- Chunking: keep multimodal context aligned (text chunk + proximate figure/image).
- Embeddings: use a joint embedding scheme (text embeddings + image embeddings with compatible dims) or concat modality-specific embeddings and store with metadata.
- Retrieval weighting: store a weight per context doc_id. On positive feedback, increment weight (e.g., w <- w + alpha); on negative, decrement or mark for re-evaluation. Use weights in similarity score: score = sim * (1 + beta * normalized_weight).
- Safety: sanitize and limit context length per prompt. Avoid hallucination by including source snippets and explicit citation instructions in the prompt.

Continual learning detail
- Feedback lifecycle:
  1. Capture user rating (correct/incorrect) + optional corrected answer or highlighted passage.
  2. Persist feedback linked to query, retrieved context IDs, and timestamp.
  3. Update context weights immediately (online) and log for batch re-ranking or fine-tuning.
  4. Optionally run periodic offline re-training or tuning of retrieval model (if using trainable retriever).
- Metrics to track:
  - Retrieval precision@k before/after feedback
  - Answer accuracy (human-labeled)
  - Citation fidelity (percent of answers that correctly cite supporting artifacts)


Contributing
- Open issues for parsers (equations, tables), retriever improvements, and UI features.
- Keep model keys out of the repo; use env vars and a secrets manager for demo.

License
- Pick an appropriate OSS license (MIT recommended for starters).

Contact / Next steps
- Prepare curated demo papers, finalize model choices (proprietary vs open), and decide if local GPU inference is required for vision components.
