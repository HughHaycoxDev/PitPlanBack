import sqlite3

DB_PATH = "iracing.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS cache(
        key TEXT PRIMARY KEY,
        VALUE TEXT,
        expires_at TEXT
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        display_name TEXT,
        iracing_access_token TEXT,
        iracing_refresh_token TEXT,
        token_expires INTEGER
    );
    """)
    db.commit()
