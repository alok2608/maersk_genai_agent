import sqlite3
import re

DB_PATH = "./ecommerce.db"

def run_select(db_path: str, query: str):
    """Execute a SELECT query and return results as dict."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchall()
        result = {
            "columns": [desc[0] for desc in cur.description],
            "rows": [dict(row) for row in rows],
        }
        return result
    finally:
        conn.close()

def validate_select_sql(query: str) -> str:
    """Ensure query is a SELECT statement (basic SQL injection protection)."""
    q = query.strip().lower()
    if not q.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    forbidden = ["insert", "update", "delete", "drop", "alter", "create", "attach", "pragma"]
    for word in forbidden:
        if re.search(rf"\b{word}\b", q):
            raise ValueError(f"Forbidden keyword detected in SQL: {word}")
    return query

def append_message(db_path, conversation_id, sender, content):
    """Store a message in the conversation memory table."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Ensure messages table exists with the correct schema
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            sender TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute(
        "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)",
        (conversation_id, sender, content)
    )
    conn.commit()
    conn.close()

def get_recent_messages(db_path, conversation_id, limit=8):
    """Retrieve recent messages for conversation memory."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT sender, content FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (conversation_id, limit))
    rows = cur.fetchall()
    conn.close()
    # Reverse to chronological order
    return [{"sender": r[0], "content": r[1]} for r in reversed(rows)]
