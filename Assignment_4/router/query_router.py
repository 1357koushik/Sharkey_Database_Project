"""
query_router.py  —  Shard-aware query router for Sports Club DB
================================================================
Implements three query routing patterns required by the assignment:

  1. Lookup   — single-key fetch → routed to exactly one shard
  2. Insert   — new record       → routed to the correct shard on insertion
  3. Range    — date/age range   → scatter to all shards, merge + sort results

All public functions return plain Python lists/dicts so they work
both from the Flask API layer and from direct test calls.
"""

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from shard_config import get_shard_id, get_shard_conn, all_shard_conns, NUM_SHARDS


# ================================================================== #
# 1.  LOOKUP QUERIES  (single Member_ID → one shard)                 #
# ================================================================== #

def get_member(member_id: str) -> dict | None:
    """
    Route: shard_id = int(member_id[1:]) % 3
    Returns the member dict or None if not found.
    """
    sid = get_shard_id(member_id)
    conn = get_shard_conn(sid)
    row = conn.execute(
        f"SELECT * FROM shard_{sid}_member WHERE Member_ID = ?",
        (member_id,)
    ).fetchone()
    conn.close()
    if row:
        return {**dict(row), "_routed_to_shard": sid}
    return None


def get_member_bookings(member_id: str) -> list[dict]:
    """Fetch all bookings for a member — single-shard lookup."""
    sid = get_shard_id(member_id)
    conn = get_shard_conn(sid)
    rows = conn.execute(
        f"""SELECT b.Booking_ID, b.Facility_ID, b.Member_ID, b.Time_In, b.Time_Out
            FROM shard_{sid}_booking b
            WHERE b.Member_ID = ?
            ORDER BY b.Time_In""",
        (member_id,)
    ).fetchall()
    conn.close()
    return [{**dict(r), "_shard": sid} for r in rows]


def get_player_stats(member_id: str) -> list[dict]:
    """Fetch player stats — single-shard lookup."""
    sid = get_shard_id(member_id)
    conn = get_shard_conn(sid)
    rows = conn.execute(
        f"""SELECT * FROM shard_{sid}_player_stat
            WHERE Member_ID = ?
            ORDER BY Recorded_Date DESC""",
        (member_id,)
    ).fetchall()
    conn.close()
    return [{**dict(r), "_shard": sid} for r in rows]


def get_member_complaints(member_id: str) -> list[dict]:
    """Fetch complaints raised by a member — single-shard lookup."""
    sid = get_shard_id(member_id)
    conn = get_shard_conn(sid)
    rows = conn.execute(
        f"""SELECT * FROM shard_{sid}_complaint
            WHERE Raised_By = ?""",
        (member_id,)
    ).fetchall()
    conn.close()
    return [{**dict(r), "_shard": sid} for r in rows]


# ================================================================== #
# 2.  INSERT OPERATIONS  (routed to correct shard)                   #
# ================================================================== #

def insert_member(data: dict) -> dict:
    """
    Insert a new member.
    Routes to shard  get_shard_id(data['Member_ID']).
    Returns {'ok': True, 'shard': sid} or {'ok': False, 'error': ...}
    """
    required = ["Member_ID", "Name", "Gender", "Email", "Age"]
    for f in required:
        if f not in data:
            return {"ok": False, "error": f"Missing field: {f}"}

    member_id = data["Member_ID"]
    sid = get_shard_id(member_id)
    conn = get_shard_conn(sid)
    try:
        conn.execute(
            f"""INSERT INTO shard_{sid}_member
                (Member_ID, Name, Gender, Email, Phone_Number, Age, DOB)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                member_id,
                data["Name"],
                data["Gender"],
                data["Email"],
                data.get("Phone_Number"),
                data["Age"],
                data.get("DOB"),
            )
        )
        conn.commit()
        return {"ok": True, "shard": sid, "Member_ID": member_id}
    except Exception as e:
        return {"ok": False, "error": str(e), "shard": sid}
    finally:
        conn.close()


def insert_booking(data: dict) -> dict:
    """
    Insert a booking — routed by Member_ID.
    data keys: Member_ID, Facility_ID, Time_In, Time_Out (optional)
    """
    member_id = data.get("Member_ID")
    if not member_id:
        return {"ok": False, "error": "Missing Member_ID"}

    sid = get_shard_id(member_id)
    conn = get_shard_conn(sid)
    try:
        cur = conn.execute(
            f"""INSERT INTO shard_{sid}_booking
                (Facility_ID, Member_ID, Time_In, Time_Out)
                VALUES (?, ?, ?, ?)""",
            (data["Facility_ID"], member_id, data["Time_In"], data.get("Time_Out"))
        )
        conn.commit()
        return {"ok": True, "shard": sid, "Booking_ID": cur.lastrowid}
    except Exception as e:
        return {"ok": False, "error": str(e), "shard": sid}
    finally:
        conn.close()


def insert_attendance(data: dict) -> dict:
    """Insert an attendance record — routed by Member_ID."""
    member_id = data.get("Member_ID")
    if not member_id:
        return {"ok": False, "error": "Missing Member_ID"}

    sid = get_shard_id(member_id)
    conn = get_shard_conn(sid)
    try:
        conn.execute(
            f"""INSERT INTO shard_{sid}_attendance
                (Member_ID, Session, Date, Status) VALUES (?, ?, ?, ?)""",
            (member_id, data["Session"], data["Date"], data["Status"])
        )
        conn.commit()
        return {"ok": True, "shard": sid}
    except Exception as e:
        return {"ok": False, "error": str(e), "shard": sid}
    finally:
        conn.close()


# ================================================================== #
# 3.  RANGE QUERIES  (scatter → all shards, gather → merge)          #
# ================================================================== #

def range_members_by_age(age_min: int, age_max: int) -> list[dict]:
    """
    Scatter-gather: query all shards for members in the age range,
    then merge and sort by Member_ID.
    """
    results = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(
            f"""SELECT Member_ID, Name, Age, Gender, Email, _shard_id
                FROM shard_{sid}_member
                WHERE Age BETWEEN ? AND ?
                ORDER BY Member_ID""",
            (age_min, age_max)
        ).fetchall()
        results.extend([{**dict(r), "_shard": sid} for r in rows])
        conn.close()

    # Sort merged result by Member_ID
    results.sort(key=lambda r: int(r["Member_ID"][1:]))
    return results


def range_bookings_by_date(date_start: str, date_end: str) -> list[dict]:
    """
    Scatter-gather: fetch all bookings within a date range across all shards.
    date_start / date_end format: 'YYYY-MM-DD'
    """
    results = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(
            f"""SELECT Booking_ID, Facility_ID, Member_ID, Time_In, Time_Out
                FROM shard_{sid}_booking
                WHERE DATE(Time_In) BETWEEN ? AND ?
                ORDER BY Time_In""",
            (date_start, date_end)
        ).fetchall()
        results.extend([{**dict(r), "_shard": sid} for r in rows])
        conn.close()

    results.sort(key=lambda r: r["Time_In"])
    return results


def range_attendance_by_date(date_start: str, date_end: str) -> list[dict]:
    """
    Scatter-gather: attendance records in a date range across all shards.
    """
    results = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(
            f"""SELECT Member_ID, Session, Date, Status
                FROM shard_{sid}_attendance
                WHERE Date BETWEEN ? AND ?
                ORDER BY Date, Member_ID""",
            (date_start, date_end)
        ).fetchall()
        results.extend([{**dict(r), "_shard": sid} for r in rows])
        conn.close()

    results.sort(key=lambda r: (r["Date"], r["Member_ID"]))
    return results


def range_complaints_by_date(date_start: str, date_end: str) -> list[dict]:
    """Scatter-gather: complaints filed within a date range."""
    results = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(
            f"""SELECT Complaint_ID, Raised_By, Description, Status, Date_Filed
                FROM shard_{sid}_complaint
                WHERE Date_Filed BETWEEN ? AND ?
                ORDER BY Date_Filed""",
            (date_start, date_end)
        ).fetchall()
        results.extend([{**dict(r), "_shard": sid} for r in rows])
        conn.close()

    results.sort(key=lambda r: r["Date_Filed"])
    return results


def list_all_members() -> list[dict]:
    """Scatter-gather: fetch ALL members from all shards (for admin list view)."""
    results = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(
            f"SELECT Member_ID, Name, Age, Gender, Email FROM shard_{sid}_member"
        ).fetchall()
        results.extend([{**dict(r), "_shard": sid} for r in rows])
        conn.close()
    results.sort(key=lambda r: int(r["Member_ID"][1:]))
    return results
