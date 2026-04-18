"""
shard_config.py — Assignment 4 sharding config on top of Assignment 3 engine.
Runtime storage uses Assignment 3 B+Tree + WAL engine instances.
"""

import os
import sys
from copy import deepcopy

NUM_SHARDS = 3

MODULE_A_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Assignment_3", "Module_A")
)
if MODULE_A_PATH not in sys.path:
    sys.path.insert(0, MODULE_A_PATH)

from db_manager import DatabaseManager

LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOGS_DIR, exist_ok=True)

SHARD_DATABASES = {sid: f"shard_db_{sid}" for sid in range(NUM_SHARDS)}
SHARD_ENDPOINTS = {
    sid: {
        "backend": "assignment3-engine",
        "database": SHARD_DATABASES[sid],
        "shard_index": sid,
        "shard_id": sid + 1,
    }
    for sid in range(NUM_SHARDS)
}
SHARD_PATHS = {sid: f"assignment3-engine://{SHARD_DATABASES[sid]}" for sid in range(NUM_SHARDS)}

TABLE_SCHEMAS = {
    "Member": {
        "Member_ID": "str",
        "Name": "str",
        "Gender": "str",
        "Email": "str",
        "Phone_Number": "str",
        "Age": "int",
        "DOB": "str",
        "Image": "str",
    },
    "Facility": {
        "Facility_ID": "int",
        "Facility_Name": "str",
        "Facility_Description": "str",
        "Status": "str",
    },
    "Booking": {
        "Booking_ID": "int",
        "Facility_ID": "int",
        "Member_ID": "str",
        "Time_In": "str",
        "Time_Out": "str",
    },
    "Complaint": {
        "Complaint_ID": "str",
        "Member_ID": "str",
        "Description": "str",
        "Status": "str",
        "Date": "str",
        "Resolved_By": "str",
    },
    "Attendance": {
        "Attendance_Key": "str",
        "Member_ID": "str",
        "Session": "str",
        "Date": "str",
        "Status": "str",
    },
    "Player_Stat": {
        "Player_Stat_Key": "str",
        "Member_ID": "str",
        "Event_ID": "str",
        "Metric_Name": "str",
        "Metric_Value": "str",
        "Recorded_Date": "str",
    },
}

SEARCH_KEYS = {
    "Member": "Member_ID",
    "Facility": "Facility_ID",
    "Booking": "Booking_ID",
    "Complaint": "Complaint_ID",
    "Attendance": "Attendance_Key",
    "Player_Stat": "Player_Stat_Key",
}

SEED_MEMBERS = [
    ("M01", "Rahul Sharma", "M", "user1@iitgn.ac.in", "900000001", 18),
    ("M02", "Neha Singh", "F", "user2@iitgn.ac.in", "900000002", 19),
    ("M03", "Aman Verma", "M", "user3@iitgn.ac.in", "900000003", 20),
    ("M04", "Priya Mehta", "F", "user4@iitgn.ac.in", "900000004", 21),
    ("M05", "Rohan Das", "M", "user5@iitgn.ac.in", "900000005", 22),
    ("M31", "Admin Rakesh", "M", "user31@iitgn.ac.in", "900000031", 28),
    ("M32", "Admin Pooja", "F", "user32@iitgn.ac.in", "900000032", 29),
]

SEED_FACILITIES = [
    (1, "Football Ground", "105m x 68m FIFA standard grass field", "Available"),
    (2, "Basketball Court", "FIBA indoor wooden court with scoreboard", "Available"),
    (3, "Cricket Stadium", "Turf pitch with 70m boundary", "Available"),
    (4, "Badminton Hall", "BWF synthetic indoor courts", "Available"),
    (5, "Swimming Pool", "50m Olympic size pool", "Available"),
]

SEED_BOOKINGS = [
    (1, 1, "M01", "2026-02-01 13:30:00", ""),
    (2, 2, "M02", "2026-02-02 14:30:00", "2026-02-02 17:30:00"),
    (3, 3, "M03", "2026-02-03 15:30:00", "2026-02-03 17:30:00"),
]

SEED_COMPLAINTS = [
    ("C01", "M01", "Football goal net torn", "Resolved", "2026-02-01", "M31"),
    ("C02", "M02", "Basketball scoreboard not working", "Resolved", "2026-02-01", "M32"),
    ("C03", "M03", "Cricket pitch crack detected", "Open", "2026-02-01", ""),
]

SEED_ATTENDANCE = [
    ("M01|2026-02-01|Morning", "M01", "Morning", "2026-02-01", "Present"),
    ("M02|2026-02-02|Evening", "M02", "Evening", "2026-02-02", "Present"),
]

SEED_PLAYER_STATS = [
    ("M01|E01|Speed", "M01", "E01", "Speed", "28", "2026-02-01"),
    ("M02|E02|Stamina", "M02", "E02", "Stamina", "31", "2026-02-02"),
]


def get_shard_id(member_id: str) -> int:
    if not isinstance(member_id, str) or len(member_id) < 2 or member_id[0] != "M":
        raise ValueError("Member_ID must be in format like 'M01'.")
    return int(member_id[1:]) % NUM_SHARDS


def shard_label(shard_id: int) -> str:
    return f"Shard {shard_id + 1}"


def shard_hostname(shard_id: int) -> str:
    return f"assignment3-engine-shard-{shard_id + 1}"


def get_table_columns(shard_id: int, table_name: str) -> set[str]:
    _ = shard_id
    return set(TABLE_SCHEMAS[table_name].keys())


def _build_shard_manager(shard_id: int) -> DatabaseManager:
    dbm = DatabaseManager()
    dbm.wal.filepath = os.path.join(LOGS_DIR, f"shard_{shard_id}.wal.log")
    dbm.recover()
    db_name = SHARD_DATABASES[shard_id]
    dbm.create_database(db_name)
    for table_name, schema in TABLE_SCHEMAS.items():
        dbm.create_table(
            db_name,
            table_name,
            schema,
            search_key=SEARCH_KEYS[table_name],
        )
    return dbm


_SHARD_ENGINES = {sid: _build_shard_manager(sid) for sid in range(NUM_SHARDS)}


def get_shard_manager(shard_id: int) -> DatabaseManager:
    return _SHARD_ENGINES[shard_id]


def get_shard_table(shard_id: int, table_name: str):
    dbm = get_shard_manager(shard_id)
    return dbm.get_table(SHARD_DATABASES[shard_id], table_name)


def clear_all_shards():
    for sid in range(NUM_SHARDS):
        for table_name in TABLE_SCHEMAS:
            table = get_shard_table(sid, table_name)
            for key, _ in list(table.get_all()):
                table.delete(key)


def _insert_rows(shard_id: int, table_name: str, rows: list[dict]):
    table = get_shard_table(shard_id, table_name)
    for row in rows:
        table.insert(deepcopy(row))


def seed_demo_data(reset: bool = False):
    if reset:
        clear_all_shards()

    facility_rows = [
        {
            "Facility_ID": fid,
            "Facility_Name": name,
            "Facility_Description": desc,
            "Status": status,
        }
        for fid, name, desc, status in SEED_FACILITIES
    ]
    for sid in range(NUM_SHARDS):
        _insert_rows(sid, "Facility", facility_rows)

    for member_id, name, gender, email, phone, age in SEED_MEMBERS:
        sid = get_shard_id(member_id)
        _insert_rows(
            sid,
            "Member",
            [
                {
                    "Member_ID": member_id,
                    "Name": name,
                    "Gender": gender,
                    "Email": email,
                    "Phone_Number": phone,
                    "Age": int(age),
                    "DOB": "",
                    "Image": "",
                }
            ],
        )

    for booking_id, facility_id, member_id, time_in, time_out in SEED_BOOKINGS:
        sid = get_shard_id(member_id)
        _insert_rows(
            sid,
            "Booking",
            [
                {
                    "Booking_ID": int(booking_id),
                    "Facility_ID": int(facility_id),
                    "Member_ID": member_id,
                    "Time_In": time_in,
                    "Time_Out": time_out,
                }
            ],
        )

    for complaint_id, member_id, desc, status, date, resolved_by in SEED_COMPLAINTS:
        sid = get_shard_id(member_id)
        _insert_rows(
            sid,
            "Complaint",
            [
                {
                    "Complaint_ID": complaint_id,
                    "Member_ID": member_id,
                    "Description": desc,
                    "Status": status,
                    "Date": date,
                    "Resolved_By": resolved_by,
                }
            ],
        )

    for key, member_id, session, date, status in SEED_ATTENDANCE:
        sid = get_shard_id(member_id)
        _insert_rows(
            sid,
            "Attendance",
            [
                {
                    "Attendance_Key": key,
                    "Member_ID": member_id,
                    "Session": session,
                    "Date": date,
                    "Status": status,
                }
            ],
        )

    for key, member_id, event_id, metric_name, metric_value, recorded_date in SEED_PLAYER_STATS:
        sid = get_shard_id(member_id)
        _insert_rows(
            sid,
            "Player_Stat",
            [
                {
                    "Player_Stat_Key": key,
                    "Member_ID": member_id,
                    "Event_ID": event_id,
                    "Metric_Name": metric_name,
                    "Metric_Value": metric_value,
                    "Recorded_Date": recorded_date,
                }
            ],
        )


def expected_distribution(member_ids: list[str]) -> dict[int, list[str]]:
    dist = {i: [] for i in range(NUM_SHARDS)}
    for member_id in member_ids:
        dist[get_shard_id(member_id)].append(member_id)
    return dist


# Always start this process with clean shard state.
seed_demo_data(reset=True)
