import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "project.db"
DUMP_PATH = ROOT / "Module_B" / "sql" / "project_dump.sql"

TRIGGERS = """
CREATE TRIGGER prevent_booking_overlap
BEFORE INSERT ON Booking
FOR EACH ROW
BEGIN
  SELECT 
    CASE 
      WHEN EXISTS (
        SELECT 1 FROM Booking
        WHERE Facility_ID = NEW.Facility_ID
          AND (
            NEW.Time_In < IFNULL(Time_Out, '9999-12-31 23:59:59')
            AND IFNULL(NEW.Time_Out, '9999-12-31 23:59:59') > Time_In
          )
      )
      THEN RAISE(ABORT, 'Booking time conflict')
    END;
END;

CREATE TRIGGER check_equipment_availability
BEFORE INSERT ON Equipment_Loan
FOR EACH ROW
BEGIN
  SELECT 
    CASE 
      WHEN (
        (SELECT IFNULL(SUM(Quantity), 0)
         FROM Equipment_Loan
         WHERE Equipment_ID = NEW.Equipment_ID
           AND Return_Time IS NULL)
        + NEW.Quantity
      ) > (
        SELECT Total_Qty 
        FROM Equipment 
        WHERE Equipment_ID = NEW.Equipment_ID
      )
      THEN RAISE(ABORT, 'Not enough equipment available')
    END;
END;

CREATE TRIGGER prevent_player_multi_role
BEFORE INSERT ON Player
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Coach WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Administrator WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;

CREATE TRIGGER prevent_coach_multi_role
BEFORE INSERT ON Coach
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Player WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Administrator WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;

CREATE TRIGGER prevent_admin_multi_role
BEFORE INSERT ON Administrator
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN EXISTS (SELECT 1 FROM Player WHERE Member_ID = NEW.Member_ID)
      OR EXISTS (SELECT 1 FROM Coach WHERE Member_ID = NEW.Member_ID)
    THEN RAISE(ABORT, 'Member already assigned another role')
  END;
END;
"""

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = OFF;")

statement_lines = []
statements = []

with DUMP_PATH.open("r", encoding="utf-8") as dump_file:
    for raw_line in dump_file:
        line = raw_line.strip()
        if not line:
            continue
        statement_lines.append(raw_line)
        if line.endswith(";"):
            statement = "".join(statement_lines).strip()
            statement_lines = []
            upper_statement = statement.upper()
            if upper_statement.startswith("INSERT INTO") or statement.startswith('DELETE FROM "sqlite_sequence"'):
                statements.append(statement)

cursor.executescript("\n".join(statements))
cursor.executescript(TRIGGERS)
cursor.execute("PRAGMA foreign_keys = ON;")
violations = cursor.execute("PRAGMA foreign_key_check;").fetchall()

if violations:
    raise RuntimeError(f"Foreign key check failed: {violations}")

conn.commit()
conn.close()

print("Data synced successfully")
