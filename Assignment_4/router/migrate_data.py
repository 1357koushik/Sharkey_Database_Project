import os, sys, sqlite3
sys.path.insert(0, os.path.dirname(__file__))

from shard_config import (
    NUM_SHARDS, get_shard_id, get_shard_conn, all_shard_conns
)

SOURCE_DB = os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 "../sports_club.db")
)


def open_source() -> sqlite3.Connection:
    conn = sqlite3.connect(SOURCE_DB)
    conn.row_factory = sqlite3.Row
    return conn



# Replicate reference tables to every shard

def replicate_reference_tables(src: sqlite3.Connection):
    ref_tables = ["Sport", "Facility", "Equipment", "Team", "Event"]
    shard_conns = [get_shard_conn(i) for i in range(NUM_SHARDS)]

    for tbl in ref_tables:
        rows = src.execute(f"SELECT * FROM {tbl}").fetchall()
        if not rows:
            print(f"  [SKIP] {tbl}: no rows in source")
            continue

        cols = rows[0].keys()
        placeholders = ", ".join("?" for _ in cols)
        col_list = ", ".join(cols)

        for sid, conn in enumerate(shard_conns):
            conn.execute(f"DELETE FROM {tbl}")
            for row in rows:
                conn.execute(
                    f"INSERT OR IGNORE INTO {tbl} ({col_list}) VALUES ({placeholders})",
                    tuple(row)
                )
            conn.commit()
        print(f"  [REF] {tbl}: {len(rows)} rows replicated to all {NUM_SHARDS} shards")

    for conn in shard_conns:
        conn.close()



# Partition member-centric tables

MEMBER_TABLES = [
    # (source_table, member_id_column)
    ("Member",         "Member_ID"),
    ("Player",         "Member_ID"),
    ("Coach",          "Member_ID"),
    ("Administrator",  "Member_ID"),
    ("Booking",        "Member_ID"),
    ("Attendance",     "Member_ID"),
    ("Equipment_Loan", "Member_ID"),
    ("Complaint",      "Raised_By"),
    ("Player_Stat",    "Member_ID"),
    ("Team_Roster",    None),   # keyed by Roll_No — handled separately
]


def migrate_member_table(src: sqlite3.Connection,
                         table: str,
                         member_col: str,
                         shard_conns: dict):
    rows = src.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        print(f"  [SKIP] {table}: no rows")
        return 0

    cols = rows[0].keys()
    col_list = ", ".join(cols)
    placeholders = ", ".join("?" for _ in cols)
    dest_table = table.lower()

    counts = {i: 0 for i in range(NUM_SHARDS)}
    for row in rows:
        mid = row[member_col]
        sid = get_shard_id(mid)
        shard_conns[sid].execute(
            f"INSERT OR IGNORE INTO shard_{sid}_{dest_table} ({col_list}) VALUES ({placeholders})",
            tuple(row)
        )
        counts[sid] += 1

    for conn in shard_conns.values():
        conn.commit()

    dist_str = "  ".join(f"shard_{i}:{counts[i]}" for i in range(NUM_SHARDS))
    print(f"  [PART] {table}: {len(rows)} rows  →  {dist_str}")
    return len(rows)


def migrate_team_roster(src: sqlite3.Connection, shard_conns: dict):
    """
    Team_Roster has no direct Member_ID; it uses Roll_No.
    We look up the Member_ID for each Roll_No via the Player table,
    then route accordingly.  If a Roll_No maps to no Member, skip.
    """
    # Build Roll_No → Member_ID map from source
    roll_map = {}
    for row in src.execute("SELECT Member_ID, Roll_No FROM Player").fetchall():
        roll_map[row["Roll_No"]] = row["Member_ID"]

    rows = src.execute("SELECT * FROM Team_Roster").fetchall()
    if not rows:
        print("  [SKIP] Team_Roster: no rows")
        return

    counts = {i: 0 for i in range(NUM_SHARDS)}
    unmapped = 0
    for row in rows:
        roll = row["Roll_No"]
        mid = roll_map.get(roll)
        if mid is None:
            unmapped += 1
            continue
        sid = get_shard_id(mid)
        shard_conns[sid].execute(
            f"INSERT OR IGNORE INTO shard_{sid}_team_roster (Team_ID, Roll_No) VALUES (?, ?)",
            (row["Team_ID"], row["Roll_No"])
        )
        counts[sid] += 1

    for conn in shard_conns.values():
        conn.commit()

    dist_str = "  ".join(f"shard_{i}:{counts[i]}" for i in range(NUM_SHARDS))
    print(f"  [PART] Team_Roster: {sum(counts.values())} rows  →  {dist_str}  (unmapped: {unmapped})")



# Player_Stat – uses Member_ID directly

def migrate_player_stat(src: sqlite3.Connection, shard_conns: dict):
    try:
        rows = src.execute("SELECT * FROM Player_Stat").fetchall()
    except Exception:
        print("  [SKIP] Player_Stat: not present in source")
        return
    if not rows:
        print("  [SKIP] Player_Stat: no rows")
        return

    counts = {i: 0 for i in range(NUM_SHARDS)}
    for row in rows:
        mid = row["Member_ID"]
        sid = get_shard_id(mid)
        shard_conns[sid].execute(
            f"""INSERT OR IGNORE INTO shard_{sid}_player_stat
                (Member_ID, Event_ID, Metric_Name, Metric_Value, Recorded_Date)
                VALUES (?, ?, ?, ?, ?)""",
            (row["Member_ID"], row["Event_ID"], row["Metric_Name"],
             row["Metric_Value"], row["Recorded_Date"])
        )
        counts[sid] += 1

    for conn in shard_conns.values():
        conn.commit()

    dist_str = "  ".join(f"shard_{i}:{counts[i]}" for i in range(NUM_SHARDS))
    print(f"  [PART] Player_Stat: {len(rows)} rows  →  {dist_str}")



# Main migration

def run_migration():
    if not os.path.exists(SOURCE_DB):
        raise FileNotFoundError(f"Source DB not found: {SOURCE_DB}")

    print(f"Source DB : {SOURCE_DB}")
    src = open_source()

    # Open shard connections once and reuse
    shard_conns = {i: get_shard_conn(i) for i in range(NUM_SHARDS)}

    print("\n── Replicating reference tables ────────────────────────────")
    replicate_reference_tables(src)

    print("\n── Partitioning member-centric tables ──────────────────────")
    for table, member_col in MEMBER_TABLES:
        if table in ("Player_Stat", "Team_Roster"):
            continue   # handled separately below
        migrate_member_table(src, table, member_col, shard_conns)

    migrate_player_stat(src, shard_conns)
    migrate_team_roster(src, shard_conns)

    for conn in shard_conns.values():
        conn.close()
    src.close()
    print("\nMigration complete.")


if __name__ == "__main__":
    run_migration()
