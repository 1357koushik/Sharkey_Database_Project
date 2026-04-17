import sqlite3
import os

DB_PATH    = os.path.join(os.path.dirname(__file__), "sports_club.db")
DUMP_PATH  = os.path.join(os.path.dirname(__file__), "..", "sql", "project_dump.sql")
SCHEMA_PATH= os.path.join(os.path.dirname(__file__), "..", "sql", "core_tables.sql")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "indexes.sql")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # FK off during initial bulk load — dump has tables in alphabetical order
    conn.execute("PRAGMA foreign_keys = OFF")

    existing = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='Member'"
    ).fetchone()

    if not existing and os.path.exists(DUMP_PATH):
        with open(DUMP_PATH, "r") as f:
            sql = f.read()
        try:
            conn.executescript(sql)
            print("[DB] Project dump loaded.")
        except Exception as e:
            print(f"[DB] Dump error: {e}")

    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r") as f:
            sql = f.read()
        try:
            conn.executescript(sql)
        except Exception as e:
            print(f"[DB] Core tables error: {e}")

    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, "r") as f:
            sql = f.read()
        try:
            conn.executescript(sql)
        except Exception as e:
            print(f"[DB] Index error: {e}")

    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")

def ensure_revoked_token_table():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS RevokedToken (
            Token      TEXT PRIMARY KEY,
            Revoked_At TEXT DEFAULT (datetime('now')),
            Expires_At TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
