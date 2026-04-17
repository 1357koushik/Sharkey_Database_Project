"""
init_shards.py  —  Create shard table schemas in all three shard databases
===========================================================================
Each shard database contains prefixed copies of every member-centric table:
    shard_0_member, shard_0_player, shard_0_booking, ...
    shard_1_member, ...
    shard_2_member, ...

Reference tables (Sport, Facility, Equipment, Team, Event) are NOT sharded —
they are replicated to each shard so foreign-key-like joins remain local.
"""

import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from shard_config import get_shard_conn, NUM_SHARDS

# ------------------------------------------------------------------ #
# DDL for the reference (replicated) tables                           #
# ------------------------------------------------------------------ #
REFERENCE_TABLES_DDL = """
CREATE TABLE IF NOT EXISTS Sport (
    Sport_ID   TEXT PRIMARY KEY,
    Sport_Name TEXT NOT NULL UNIQUE,
    Category   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Facility (
    Facility_ID          INTEGER PRIMARY KEY,
    Facility_Name        TEXT NOT NULL UNIQUE,
    Facility_Description TEXT NOT NULL,
    Status               TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Equipment (
    Equipment_ID   TEXT PRIMARY KEY,
    Equipment_Name TEXT NOT NULL,
    Total_Qty      INTEGER NOT NULL,
    Status         TEXT NOT NULL,
    Sport_ID       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Team (
    Team_ID   TEXT PRIMARY KEY,
    Team_Name TEXT NOT NULL UNIQUE,
    Category  TEXT NOT NULL,
    Sport_ID  TEXT NOT NULL,
    Coach_ID  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Event (
    Event_ID          TEXT PRIMARY KEY,
    Event_Name        TEXT NOT NULL,
    Facility_ID       INTEGER NOT NULL,
    Description       TEXT NOT NULL,
    Start_Time        TEXT NOT NULL,
    End_Time          TEXT NOT NULL,
    Attendance_Status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Event_Team (
    Event_ID TEXT NOT NULL,
    Team_ID  TEXT NOT NULL,
    PRIMARY KEY (Event_ID, Team_ID)
);
"""

# ------------------------------------------------------------------ #
# DDL for member-centric (sharded) tables — prefixed with shard_N_   #
# ------------------------------------------------------------------ #
def member_shard_ddl(shard_id: int) -> str:
    p = f"shard_{shard_id}_"
    return f"""
-- ── Member ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}member (
    Member_ID    TEXT PRIMARY KEY,
    Name         TEXT NOT NULL,
    Gender       TEXT NOT NULL CHECK(Gender IN ('M','F')),
    Email        TEXT NOT NULL UNIQUE,
    Phone_Number TEXT UNIQUE,
    Age          INTEGER NOT NULL CHECK(Age > 0),
    DOB          TEXT,
    Image        BLOB,
    _shard_id    INTEGER NOT NULL DEFAULT {shard_id}
);

-- ── Player ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}player (
    Member_ID    TEXT PRIMARY KEY,
    Roll_No      TEXT NOT NULL UNIQUE,
    Height       REAL,
    Weight       REAL,
    Blood_Group  TEXT,
    FOREIGN KEY(Member_ID) REFERENCES {p}member(Member_ID) ON DELETE CASCADE
);

-- ── Coach ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}coach (
    Member_ID        TEXT PRIMARY KEY,
    Coach_ID         INTEGER NOT NULL UNIQUE,
    Sport_ID         TEXT NOT NULL,
    Years_Experience INTEGER DEFAULT 0,
    Salary           REAL    DEFAULT 0.0,
    Joining_Date     TEXT,
    FOREIGN KEY(Member_ID) REFERENCES {p}member(Member_ID) ON DELETE CASCADE
);

-- ── Administrator ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}administrator (
    Member_ID        TEXT PRIMARY KEY,
    Administrator_ID INTEGER NOT NULL UNIQUE,
    Admin_Level      INTEGER,
    Department       TEXT,
    Office_Location  TEXT,
    FOREIGN KEY(Member_ID) REFERENCES {p}member(Member_ID) ON DELETE CASCADE
);

-- ── Booking ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}booking (
    Booking_ID  INTEGER PRIMARY KEY AUTOINCREMENT,
    Facility_ID INTEGER NOT NULL,
    Member_ID   TEXT NOT NULL,
    Time_In     TEXT NOT NULL,
    Time_Out    TEXT,
    FOREIGN KEY(Member_ID) REFERENCES {p}member(Member_ID) ON DELETE CASCADE
);

-- ── Attendance ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}attendance (
    Member_ID TEXT NOT NULL,
    Session   TEXT NOT NULL,
    Date      TEXT NOT NULL,
    Status    TEXT NOT NULL CHECK(Status IN ('Present','Absent')),
    FOREIGN KEY(Member_ID) REFERENCES {p}member(Member_ID) ON DELETE CASCADE
);

-- ── Equipment_Loan ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}equipment_loan (
    Member_ID    TEXT NOT NULL,
    Equipment_ID TEXT NOT NULL,
    Quantity     INTEGER NOT NULL,
    Issue_Time   TEXT NOT NULL,
    Return_Time  TEXT,
    PRIMARY KEY(Member_ID, Equipment_ID, Issue_Time),
    FOREIGN KEY(Member_ID) REFERENCES {p}member(Member_ID) ON DELETE CASCADE
);

-- ── Complaint ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}complaint (
    Complaint_ID TEXT PRIMARY KEY,
    Raised_By    TEXT NOT NULL,
    Description  TEXT NOT NULL,
    Status       TEXT NOT NULL CHECK(Status IN ('Open','Resolved')),
    Date_Filed   TEXT NOT NULL,
    Resolved_By  TEXT,
    FOREIGN KEY(Raised_By) REFERENCES {p}member(Member_ID) ON DELETE CASCADE
);

-- ── Player_Stat ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}player_stat (
    Member_ID     TEXT NOT NULL,
    Event_ID      TEXT,
    Metric_Name   TEXT NOT NULL,
    Metric_Value  TEXT NOT NULL,
    Recorded_Date TEXT NOT NULL,
    PRIMARY KEY(Member_ID, Metric_Name, Recorded_Date),
    FOREIGN KEY(Member_ID) REFERENCES {p}player(Member_ID) ON DELETE CASCADE
);

-- ── Team_Roster ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS {p}team_roster (
    Team_ID TEXT NOT NULL,
    Roll_No TEXT NOT NULL,
    PRIMARY KEY(Team_ID, Roll_No)
);
"""


def init_all_shards():
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "shards"), exist_ok=True)
    for sid in range(NUM_SHARDS):
        conn = get_shard_conn(sid)
        conn.executescript(REFERENCE_TABLES_DDL)
        conn.executescript(member_shard_ddl(sid))
        conn.commit()
        conn.close()
        print(f"  [OK] Shard {sid} schema initialised")
    print(f"All {NUM_SHARDS} shard schemas ready.")


if __name__ == "__main__":
    init_all_shards()
