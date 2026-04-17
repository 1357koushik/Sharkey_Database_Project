import os
import datetime
from db import get_db

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "audit.log")

def log_action(username, member_id, role, action, table_name, record_id,
               details, ip_address, status):
    """Write audit entry to both DB table and audit.log file."""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Write to DB
    try:
        db = get_db()
        db.execute(
            """INSERT INTO AuditLog
               (Timestamp, Username, Member_ID, Role, Action, Table_Name, Record_ID, Details, IP_Address, Status)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (timestamp, username, member_id, role, action, table_name,
             record_id, details, ip_address, status)
        )
        db.commit()
        db.close()
    except Exception as e:
        print(f"[AUDIT DB ERROR] {e}")

    # Write to log file
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        line = (f"[{timestamp}] [{status}] user={username or 'anonymous'} "
                f"member={member_id or '-'} role={role or '-'} "
                f"action={action} table={table_name or '-'} "
                f"record={record_id or '-'} ip={ip_address or '-'} "
                f"details={details or '-'}\n")
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except Exception as e:
        print(f"[AUDIT FILE ERROR] {e}")
