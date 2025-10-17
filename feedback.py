import sqlite3
from pathlib import Path

DB_PATH = Path("./db/feedback.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT,
                question TEXT,
                feedback INTEGER
            )
        """)

def add_feedback(chunk_id, question, feedback):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO feedback (chunk_id, question, feedback) VALUES (?, ?, ?)",
                     (chunk_id, question, feedback))

def get_feedback_scores():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT chunk_id, AVG(feedback) as score
            FROM feedback
            GROUP BY chunk_id
        """).fetchall()
    return {r[0]: r[1] for r in rows}
