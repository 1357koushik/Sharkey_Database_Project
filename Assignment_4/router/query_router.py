"""
query_router.py — shard-aware queries using MySQL shards.
"""

import os
import sys
from copy import deepcopy

sys.path.insert(0, os.path.dirname(__file__))

from shard_config import NUM_SHARDS, get_shard_id, get_shard_table, get_table_columns


def _clone(row: dict) -> dict:
    return deepcopy(row)


def _all_rows(shard_id: int, table_name: str) -> list[dict]:
    table = get_shard_table(shard_id, table_name)
    return [_clone(row) for _, row in table.get_all()]


def _next_booking_id() -> int:
    max_id = 0
    for sid in range(NUM_SHARDS):
        table = get_shard_table(sid, "Booking")
        for key, _ in table.get_all():
            max_id = max(max_id, int(key))
    return max_id + 1


def get_member(member_id: str) -> dict | None:
    sid = get_shard_id(member_id)
    row = get_shard_table(sid, "Member").get(member_id)
    if row is None:
        return None
    return {**_clone(row), "_routed_to_shard_index": sid, "_routed_to_shard": sid + 1}


def get_member_bookings(member_id: str) -> list[dict]:
    sid = get_shard_id(member_id)
    rows = [r for r in _all_rows(sid, "Booking") if r["Member_ID"] == member_id]
    rows.sort(key=lambda r: r["Time_In"])
    return [{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows]


def get_player_stats(member_id: str) -> list[dict]:
    sid = get_shard_id(member_id)
    rows = [r for r in _all_rows(sid, "Player_Stat") if r["Member_ID"] == member_id]
    rows.sort(key=lambda r: r["Recorded_Date"], reverse=True)
    return [{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows]


def get_member_complaints(member_id: str) -> list[dict]:
    sid = get_shard_id(member_id)
    member_col = "Member_ID"
    if "Member_ID" not in get_table_columns(sid, "Complaint"):
        member_col = "Raised_By"
    rows = [r for r in _all_rows(sid, "Complaint") if r.get(member_col) == member_id]
    return [{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows]


def insert_member(data: dict) -> dict:
    required = ["Member_ID", "Name", "Gender", "Email", "Age"]
    for field in required:
        if field not in data:
            return {"ok": False, "error": f"Missing field: {field}"}

    member_id = str(data["Member_ID"])
    sid = get_shard_id(member_id)
    record = {
        "Member_ID": member_id,
        "Name": str(data["Name"]),
        "Gender": str(data["Gender"]),
        "Email": str(data["Email"]),
        "Phone_Number": str(data.get("Phone_Number", "")),
        "Age": int(data["Age"]),
        "DOB": str(data.get("DOB", "")),
        "Image": str(data.get("Image", "")),
    }
    try:
        get_shard_table(sid, "Member").insert(record)
        return {"ok": True, "shard_index": sid, "shard": sid + 1, "Member_ID": member_id}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "shard_index": sid, "shard": sid + 1}


def insert_booking(data: dict) -> dict:
    member_id = data.get("Member_ID")
    if not member_id:
        return {"ok": False, "error": "Missing Member_ID"}

    sid = get_shard_id(str(member_id))
    next_id = _next_booking_id()
    record = {
        "Booking_ID": int(next_id),
        "Facility_ID": int(data["Facility_ID"]),
        "Member_ID": str(member_id),
        "Time_In": str(data["Time_In"]),
        "Time_Out": str(data.get("Time_Out", "")),
    }
    try:
        get_shard_table(sid, "Booking").insert(record)
        return {"ok": True, "shard_index": sid, "shard": sid + 1, "Booking_ID": next_id}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "shard_index": sid, "shard": sid + 1}


def insert_attendance(data: dict) -> dict:
    member_id = data.get("Member_ID")
    if not member_id:
        return {"ok": False, "error": "Missing Member_ID"}

    sid = get_shard_id(str(member_id))
    key = f"{member_id}|{data['Date']}|{data['Session']}"
    record = {
        "Attendance_Key": key,
        "Member_ID": str(member_id),
        "Session": str(data["Session"]),
        "Date": str(data["Date"]),
        "Status": str(data["Status"]),
    }
    try:
        get_shard_table(sid, "Attendance").insert(record)
        return {"ok": True, "shard_index": sid, "shard": sid + 1}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "shard_index": sid, "shard": sid + 1}


def range_members_by_age(age_min: int, age_max: int) -> list[dict]:
    results = []
    for sid in range(NUM_SHARDS):
        rows = [r for r in _all_rows(sid, "Member") if int(age_min) <= int(r["Age"]) <= int(age_max)]
        results.extend([{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows])
    results.sort(key=lambda r: int(r["Member_ID"][1:]))
    return results


def range_bookings_by_date(date_start: str, date_end: str) -> list[dict]:
    results = []
    for sid in range(NUM_SHARDS):
        rows = [
            r
            for r in _all_rows(sid, "Booking")
            if date_start <= str(r["Time_In"])[:10] <= date_end
        ]
        results.extend([{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows])
    results.sort(key=lambda r: r["Time_In"])
    return results


def range_attendance_by_date(date_start: str, date_end: str) -> list[dict]:
    results = []
    for sid in range(NUM_SHARDS):
        rows = [r for r in _all_rows(sid, "Attendance") if date_start <= str(r["Date"]) <= date_end]
        results.extend([{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows])
    results.sort(key=lambda r: (r["Date"], r["Member_ID"]))
    return results


def range_complaints_by_date(date_start: str, date_end: str) -> list[dict]:
    results = []
    for sid in range(NUM_SHARDS):
        cols = get_table_columns(sid, "Complaint")
        date_col = "Date_Filed" if "Date_Filed" in cols else "Date"
        rows = [r for r in _all_rows(sid, "Complaint") if date_start <= str(r.get(date_col, "")) <= date_end]
        results.extend([{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows])
    results.sort(key=lambda r: str(r.get("Date_Filed", r.get("Date", ""))))
    return results


def list_all_members() -> list[dict]:
    results = []
    for sid in range(NUM_SHARDS):
        rows = _all_rows(sid, "Member")
        results.extend([{**r, "_shard_index": sid, "_shard": sid + 1} for r in rows])
    results.sort(key=lambda r: int(r["Member_ID"][1:]))
    return results
