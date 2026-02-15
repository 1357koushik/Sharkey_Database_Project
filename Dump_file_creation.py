# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 17:10:09 2026

@author: koushik
"""

import sqlite3

conn = sqlite3.connect("project.db")

with open("project_dump.sql", "w", encoding="utf-8") as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")

conn.close()

print("✅ SQL dump file created: project_dump.sql")
