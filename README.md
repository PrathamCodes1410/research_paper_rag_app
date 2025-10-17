# Multimodal RAG System with Continual Learning for Scientific Paper Understanding

Short description
- Local research-focused Retrieval-Augmented Generation (RAG) that ingests scientific PDFs (text, equations, figures, tables), builds multimodal embeddings, and answers questions with artifact-level citations. Feedback is stored to improve retrieval over time.

Key features
- PDF parsing (text + images) via [`app.parsers.extract_text_and_figures`](app/parsers.py) and an alternate extractor in [`app.rag.extract_text_and_figures`](app/rag.py).
- Local vector DB (Chroma) initialization in [`app.rag.init_vector_db`](app/rag.py) and document indexing via [`app.rag.add_chunks_to_db`](app/rag.py).
- Local retrieval + QA with [`app.rag.ask_local_llm`](app/rag.py).
- Session lifecycle management and cleanup via [`app.rag.cleanup_session`](app/rag.py).
- Web UI built with Streamlit in [app/ui.py](app/ui.py) that wires upload → ingest → query → feedback.
- Simple feedback persistence in [app/feedback.py](app/feedback.py).

Repository layout
- [app/](app)
  - [app/rag.py](app/rag.py) — vector DB helpers, extractors, LLM/RAG pipeline functions
  - [app/parsers.py](app/parsers.py) — PDF parsing / figure extraction helper
  - [app/ui.py](app/ui.py) — Streamlit frontend (session, upload, QA, feedback)
  - [app/feedback.py](app/feedback.py) — lightweight SQLite feedback store
  - [app/config.py](app/config.py) — env-based configuration
- data/ — papers, extracted figures and persistent DBs (e.g. [data/vector_db/chroma.sqlite3](data/vector_db/chroma.sqlite3))
- db/ — local databases (feedback, etc.)
- requirements.txt — Python deps
- LICENSE — MIT license

Quickstart (development)
1. Prepare
   - Python 3.10+
   - Create a virtualenv and install deps:
     ```sh
     pip install -r requirements.txt
     ```
2. Environment
   - Set keys and paths in env or a .env file consumed by [app/config.py](app/config.py)
     - Example: GEMINI_API_KEY, CHROMA_DB_PATH (defaults to ./data/vector_db)
3. Run
   - Start the UI:
     ```sh
     streamlit run app/ui.py
     ```
   - In the UI: upload a PDF, wait for parsing & indexing, then ask questions.

Core flows & important symbols
- Ingest/parse:
  - [`app.parsers.extract_text_and_figures`](app/parsers.py) — low-level PDF page text + image extraction.
  - [`app.rag.extract_text_and_figures`](app/rag.py) — session-aware extractor that writes figures to session temp dirs.
- Indexing:
  - [`app.rag.init_vector_db`](app/rag.py) — creates a session-scoped Chroma DB.
  - [`app.rag.add_chunks_to_db`](app/rag.py) — converts chunks to `langchain.schema.Document` and indexes.
- Query:
  - [`app.rag.ask_local_llm`](app/rag.py) — runs retrieval + local LLM QA and appends figure references.
- Session:
  - [`app.rag.cleanup_session`](app/rag.py) — removes per-session temp files and DBs.
- UI:
  - [app/ui.py](app/ui.py) — session creation, file upload, and feedback buttons wired to the above functions.

Design notes
- Multimodal alignment: text chunks should be stored together with nearby figure metadata so answers can cite page/figure.
- Feedback loop: feedback entries in [app/feedback.py](app/feedback.py) should be tied to chunk IDs so retrieval weights can be updated.
- Safety: the prompt should include explicit citation instructions and context-length limits to reduce hallucinations.

Extending the project
- Replace or augment embeddings in [`app.rag.init_vector_db`](app/rag.py) with joint text+image embeddings.
- Add a weighting mechanism using feedback from [app/feedback.py](app/feedback.py) to bias retrieval scores.
- Improve parsing in [app/parsers.py](app/parsers.py) to recover LaTeX equations and table structure.

Troubleshooting
- If images fail to extract, check that `PyMuPDF` (`fitz`) is installed and that `app/parsers.py` has permission to write to the temp session directory.
- If Chroma fails to persist, verify CHROMA_DB_PATH in [app/config.py](app/config.py) and file permissions.

Contributing
- Open issues/PRs for parser improvements, retrieval weighting, UI polish, and tests.
- Keep secrets out of the repo; use env vars or a secrets manager.

License
- MIT — see [LICENSE](LICENSE).

References
- Code entry points: [app/rag.py](app/rag.py), [app/parsers.py](app/parsers.py), [app/ui.py](app/ui.py), [app/feedback.py](app/feedback.py), [app/config.py](app/config.py).
- Requirements: [requirements.txt](requirements.txt)
