"""
database.py — Module B shared database instance
Uses Assignment 2 sports-club relations for Assignment 3 ACID demos.
"""
import os
import sys
from collections import Counter
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MODULE_A_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Module_A"))
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
WAL_PATH = os.path.join(LOGS_DIR, "wal.log")
DB_NAME = "assignment3"

if MODULE_A_PATH not in sys.path:
    sys.path.insert(0, MODULE_A_PATH)

from db_manager import DatabaseManager
from transaction import _get_lock, recover 


class WebTransactionManager:
    def __init__(self, db_manager: DatabaseManager, db_name: str):
        self.db = db_manager
        self.db_name = db_name
        self.wal = db_manager.wal

    def begin(self):
        txn = self.db.begin_transaction()
        txn.begin()
        return txn

    def commit(self, txn):
        txn.commit()

    def rollback(self, txn):
        txn.rollback()

    def insert(self, txn, table_name: str, record: dict):
        txn.insert(self.db_name, table_name, record)

    def update(self, txn, table_name: str, key, record: dict):
        txn.update(self.db_name, table_name, key, record)

    def delete(self, txn, table_name: str, key):
        txn.delete(self.db_name, table_name, key)

    def _acquire(self, *table_names):
        for name in sorted(set(table_names)):
            _get_lock(self.db_name, name).acquire()

    def _release(self, *table_names):
        for name in sorted(set(table_names), reverse=True):
            try:
                _get_lock(self.db_name, name).release()
            except RuntimeError:
                pass

    def recover(self):
        return self.db.recover()

    def wal_summary(self):
        entries = self.wal.read_all()
        counts = Counter(entry.get("op") for entry in entries)
        recent = []
        for idx, entry in enumerate(entries[-50:], start=max(1, len(entries) - 49)):
            recent.append({
                "lsn": idx,
                "txn_id": entry.get("txn_id"),
                "op": entry.get("op"),
                "table": entry.get("table"),
                "key": entry.get("key"),
                "before": entry.get("old_value"),
                "after": entry.get("new_value", entry.get("value")),
            })
        return {"total": len(entries), "counts": dict(counts), "recent": recent}


os.makedirs(LOGS_DIR, exist_ok=True)

dbm = DatabaseManager()
dbm.wal.filepath = WAL_PATH
recover(dbm)
dbm.create_database(DB_NAME)
dbm.create_table(
    DB_NAME,
    "Member",
    {
        "Member_ID": "str",
        "Name": "str",
        "Gender": "str",
        "Email": "str",
        "Phone_Number": "str",
        "Age": "int",
        "DOB": "str",
        "Image": "str",
    },
    search_key="Member_ID",
)
dbm.create_table(
    DB_NAME,
    "Facility",
    {
        "Facility_ID": "int",
        "Facility_Name": "str",
        "Facility_Description": "str",
        "Status": "str",
    },
    search_key="Facility_ID",
)
dbm.create_table(
    DB_NAME,
    "Booking",
    {
        "Booking_ID": "int",
        "Facility_ID": "int",
        "Member_ID": "str",
        "Time_In": "str",
        "Time_Out": "str",
    },
    search_key="Booking_ID",
)
dbm.create_table(
    DB_NAME,
    "Complaint",
    {
        "Complaint_ID": "str",
        "Member_ID": "str",
        "Description": "str",
        "Status": "str",
        "Date": "str",
        "Resolved_By": "str",
    },
    search_key="Complaint_ID",
)

members_table = dbm.get_table(DB_NAME, "Member")
facilities_table = dbm.get_table(DB_NAME, "Facility")
bookings_table = dbm.get_table(DB_NAME, "Booking")
complaints_table = dbm.get_table(DB_NAME, "Complaint")

# Backward-compatible aliases inside Module_B code while the rest of the UI is updated.
users_table = members_table
products_table = facilities_table
orders_table = bookings_table
tm = WebTransactionManager(dbm, DB_NAME)
TABLES = {
    "Member": members_table,
    "Facility": facilities_table,
    "Booking": bookings_table,
    "Complaint": complaints_table,
}


def next_booking_id():
    rows = bookings_table.get_all()
    table_max = max((key for key, _ in rows), default=0) if rows else 0
    wal_max = 0
    for entry in tm.wal.read_all():
        if entry.get("table") == "Booking":
            try:
                wal_max = max(wal_max, int(entry.get("key", 0)))
            except Exception:
                pass
    return max(table_max, wal_max) + 1


def next_complaint_id():
    rows = complaints_table.get_all()
    nums = []
    for key, _ in rows:
        try:
            nums.append(int(str(key).replace("C", "")))
        except Exception:
            pass
    return f"C{(max(nums, default=0) + 1):02d}"


def today_str():
    return datetime.now().strftime("%Y-%m-%d")

# Seed data
for member_id, name, gender, email, phone, age in [
    ("M01", "Rahul Sharma", "M", "user1@iitgn.ac.in", "900000001", 18),
    ("M02", "Neha Singh", "F", "user2@iitgn.ac.in", "900000002", 19),
    ("M03", "Aman Verma", "M", "user3@iitgn.ac.in", "900000003", 20),
    ("M04", "Priya Mehta", "F", "user4@iitgn.ac.in", "900000004", 21),
    ("M05", "Rohan Das", "M", "user5@iitgn.ac.in", "900000005", 22),
    ("M31", "Admin Rakesh", "M", "user31@iitgn.ac.in", "900000031", 28),
    ("M32", "Admin Pooja", "F", "user32@iitgn.ac.in", "900000032", 29),
]:
    members_table.insert({
        "Member_ID": member_id,
        "Name": name,
        "Gender": gender,
        "Email": email,
        "Phone_Number": phone,
        "Age": age,
        "DOB": "",
        "Image": "",
    })

for facility_id, name, desc, status in [
    (1, "Football Ground", "105m x 68m FIFA standard grass field", "Available"),
    (2, "Basketball Court", "FIBA indoor wooden court with scoreboard", "Available"),
    (3, "Cricket Stadium", "Turf pitch with 70m boundary", "Available"),
    (4, "Badminton Hall", "BWF synthetic indoor courts", "Available"),
    (5, "Swimming Pool", "50m Olympic size pool", "Available"),
]:
    facilities_table.insert({
        "Facility_ID": facility_id,
        "Facility_Name": name,
        "Facility_Description": desc,
        "Status": status,
    })

for booking_id, facility_id, member_id, time_in, time_out in [
    (1, 1, "M01", "2026-02-01 13:30:00", ""),
    (2, 2, "M02", "2026-02-02 14:30:00", "2026-02-02 17:30:00"),
    (3, 3, "M03", "2026-02-03 15:30:00", "2026-02-03 17:30:00"),
]:
    bookings_table.insert({
        "Booking_ID": booking_id,
        "Facility_ID": facility_id,
        "Member_ID": member_id,
        "Time_In": time_in,
        "Time_Out": time_out,
    })

for complaint_id, member_id, desc, status, resolved_by in [
    ("C01", "M01", "Football goal net torn", "Resolved", "M31"),
    ("C02", "M02", "Basketball scoreboard not working", "Resolved", "M32"),
    ("C03", "M03", "Cricket pitch crack detected", "Open", ""),
]:
    complaints_table.insert({
        "Complaint_ID": complaint_id,
        "Member_ID": member_id,
        "Description": desc,
        "Status": status,
        "Date": "2026-02-01",
        "Resolved_By": resolved_by,
    })
