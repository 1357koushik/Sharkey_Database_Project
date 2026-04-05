import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "project.db"
DUMP_PATH = ROOT / "project_dump.sql"

conn = sqlite3.connect(DB_PATH)

with DUMP_PATH.open("w", encoding="utf-8") as dump_file:
    for line in conn.iterdump():
        dump_file.write(f"{line}\n")

conn.close()

print("SQL dump file created successfully")
