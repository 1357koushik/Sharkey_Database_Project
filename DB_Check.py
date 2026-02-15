import sqlite3

# Connect to database
conn = sqlite3.connect("project.db")
cursor = conn.cursor()

# Get all table names (excluding sqlite internal tables)
cursor.execute("""
SELECT name FROM sqlite_master 
WHERE type='table' AND name NOT LIKE 'sqlite_%';
""")

tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print("\n" + "="*60)
    print(f"TABLE: {table_name}")
    print("="*60)

    # Fetch first 5 rows
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    # Print column names
    column_names = [description[0] for description in cursor.description]
    print("Columns:", column_names)

    # Print rows
    for row in rows:
        print(row)

conn.close()