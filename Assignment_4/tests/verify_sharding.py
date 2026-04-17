import os, sys, sqlite3

# Make output robust on Windows when captured via pipes (e.g., Jupyter subprocess).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "router"))

from shard_config import get_shard_id, get_shard_conn, all_shard_conns, NUM_SHARDS
from query_router import (
    get_member, get_member_bookings, get_player_stats,
    insert_member, insert_booking,
    range_members_by_age, range_bookings_by_date,
    range_attendance_by_date, list_all_members
)

def _resolve_source_db() -> str:
    here = os.path.dirname(__file__)
    candidates = [
        os.path.abspath(os.path.join(here, "sports_club.db")),
        os.path.abspath(os.path.join(here, "..", "sports_club.db")),
    ]

    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    for p in candidates:
        if os.path.exists(p):
            return p

    # Last resort (will fail later with a clear sqlite/file error)
    return candidates[-1]


SOURCE_DB = _resolve_source_db()

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

results = []


def check(name: str, condition: bool, evidence: str = ""):
    status = PASS if condition else FAIL
    print(f"  {status}  {name}")
    if evidence:
        print(f"         {evidence}")
    results.append((name, condition))


# A.  ROW COUNTS — source vs shards
def verify_row_counts():
    print("\n══ A. Data Integrity — Row Counts ══════════════════════════")
    src = sqlite3.connect(f"file:{SOURCE_DB}?mode=ro", uri=True)
    src.row_factory = sqlite3.Row

    member_tables = [
        ("Member", "member", "Member_ID"),
        ("Booking", "booking", "Member_ID"),
        ("Attendance", "attendance", "Member_ID"),
        ("Equipment_Loan", "equipment_loan", "Member_ID"),
        ("Complaint", "complaint", "Raised_By"),
        ("Player", "player", "Member_ID"),
        ("Coach", "coach", "Member_ID"),
        ("Administrator", "administrator", "Member_ID"),
        ("Team_Roster", "team_roster", None),
    ]

    for src_table, shard_table, _ in member_tables:
        try:
            src_count = src.execute(f"SELECT COUNT(*) FROM {src_table}").fetchone()[0]
        except Exception:
            continue

        shard_total = 0
        for conn, sid in all_shard_conns():
            try:
                n = conn.execute(
                    f"SELECT COUNT(*) FROM shard_{sid}_{shard_table}"
                ).fetchone()[0]
                shard_total += n
            except Exception:
                pass
            conn.close()

        check(
            f"{src_table}: source={src_count} == shards_total={shard_total}",
            src_count == shard_total,
            f"(source: {src_count}, across {NUM_SHARDS} shards: {shard_total})"
        )

    src.close()


# B.  NO DUPLICATES ACROSS SHARDS

def verify_no_duplicates():
    print("\n══ B. No Cross-Shard Duplicates ════════════════════════════")

    # Collect all Member_IDs across all shards and check for duplication
    all_ids = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(f"SELECT Member_ID FROM shard_{sid}_member").fetchall()
        all_ids.extend([r[0] for r in rows])
        conn.close()

    total = len(all_ids)
    unique = len(set(all_ids))
    check(
        f"Member: {total} total rows, {unique} unique IDs (no duplicates)",
        total == unique,
        f"Duplicate IDs: {[x for x in all_ids if all_ids.count(x) > 1]}"
    )

    # Complaint_IDs
    all_cids = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(f"SELECT Complaint_ID FROM shard_{sid}_complaint").fetchall()
        all_cids.extend([r[0] for r in rows])
        conn.close()
    c_total = len(all_cids)
    c_unique = len(set(all_cids))
    check(
        f"Complaint: {c_total} total, {c_unique} unique (no duplicates)",
        c_total == c_unique
    )



# C.  EVERY RECORD IS IN THE CORRECT SHARD


def verify_shard_correctness():
    print("\n══ C. Shard Assignment Correctness ═════════════════════════")

    misplaced = []
    for conn, sid in all_shard_conns():
        rows = conn.execute(f"SELECT Member_ID FROM shard_{sid}_member").fetchall()
        for row in rows:
            mid = row[0]
            expected = get_shard_id(mid)
            if expected != sid:
                misplaced.append((mid, f"found in shard {sid}, expected {expected}"))
        conn.close()

    check(
        f"All Member rows are in their correct shard (hash verified)",
        len(misplaced) == 0,
        f"Misplaced: {misplaced}" if misplaced else "No misplacements found"
    )

    # Sample spot-checks
    samples = [("M01", 1), ("M03", 0), ("M02", 2), ("M40", 1), ("M30", 0)]
    for mid, expected_shard in samples:
        actual = get_shard_id(mid)
        check(
            f"  Hash check: {mid} → shard {actual} (expected {expected_shard})",
            actual == expected_shard
        )



# D.  LOOKUP ROUTING

def verify_lookup_routing():
    print("\n══ D. Lookup Query Routing ══════════════════════════════════")

    # Lookup M01 → should be in shard 1
    m = get_member("M01")
    check(
        "get_member('M01') returns record from shard 1",
        m is not None and m["_routed_to_shard"] == 1 and m["Name"] == "Rahul Sharma",
        f"Result: {m}"
    )

    # Lookup M03 → should be in shard 0
    m = get_member("M03")
    check(
        "get_member('M03') returns record from shard 0",
        m is not None and m["_routed_to_shard"] == 0 and m["Name"] == "Aman Verma",
        f"Result: {m}"
    )

    # Lookup M02 → should be in shard 2
    m = get_member("M02")
    check(
        "get_member('M02') returns record from shard 2",
        m is not None and m["_routed_to_shard"] == 2 and m["Name"] == "Neha Singh",
        f"Result: {m}"
    )

    # Verify bookings lookup hits only one shard
    bookings = get_member_bookings("M01")
    shard_ids_used = set(b["_shard"] for b in bookings)
    check(
        "get_member_bookings('M01') touches exactly 1 shard",
        len(shard_ids_used) == 1 and shard_ids_used == {1},
        f"Shards touched: {shard_ids_used}, bookings found: {len(bookings)}"
    )

    # Non-existent member
    m_miss = get_member("M99")
    check(
        "get_member('M99') returns None for non-existent member",
        m_miss is None
    )



# E.  INSERT ROUTING


def verify_insert_routing():
    print("\n══ E. Insert Routing ════════════════════════════════════════")

    # Insert a new member M41 → 41 % 3 = 2 → shard 2
    res = insert_member({
        "Member_ID": "M41",
        "Name": "Test Member Forty-One",
        "Gender": "M",
        "Email": "test_m41@iitgn.ac.in",
        "Age": 22
    })
    check(
        "insert_member('M41') routed to shard 2 (41 % 3 = 2)",
        res["ok"] and res["shard"] == 2,
        f"Result: {res}"
    )

    # Verify it is in shard 2 and not in shards 0 or 1
    conn2 = get_shard_conn(2)
    found = conn2.execute(
        "SELECT Member_ID FROM shard_2_member WHERE Member_ID='M41'"
    ).fetchone()
    conn2.close()
    check("M41 exists in shard 2 after insert", found is not None)

    conn0 = get_shard_conn(0)
    not_in_0 = conn0.execute(
        "SELECT Member_ID FROM shard_0_member WHERE Member_ID='M41'"
    ).fetchone()
    conn0.close()
    check("M41 does NOT exist in shard 0", not_in_0 is None)

    conn1 = get_shard_conn(1)
    not_in_1 = conn1.execute(
        "SELECT Member_ID FROM shard_1_member WHERE Member_ID='M41'"
    ).fetchone()
    conn1.close()
    check("M41 does NOT exist in shard 1", not_in_1 is None)

    # Insert a booking for M41 → should go to shard 2
    b_res = insert_booking({
        "Member_ID": "M41",
        "Facility_ID": 1,
        "Time_In": "2026-04-18 10:00:00"
    })
    check(
        "insert_booking for M41 routed to shard 2",
        b_res["ok"] and b_res["shard"] == 2,
        f"Result: {b_res}"
    )

    # Insert M42 → 42 % 3 = 0 → shard 0
    res42 = insert_member({
        "Member_ID": "M42",
        "Name": "Test Member Forty-Two",
        "Gender": "F",
        "Email": "test_m42@iitgn.ac.in",
        "Age": 20
    })
    check(
        "insert_member('M42') routed to shard 0 (42 % 3 = 0)",
        res42["ok"] and res42["shard"] == 0,
        f"Result: {res42}"
    )

    # Cleanup — remove test records so subsequent tests aren't affected
    for sid, mid in [(2, "M41"), (0, "M42")]:
        conn = get_shard_conn(sid)
        conn.execute(f"DELETE FROM shard_{sid}_booking WHERE Member_ID=?", (mid,))
        conn.execute(f"DELETE FROM shard_{sid}_member WHERE Member_ID=?", (mid,))
        conn.commit()
        conn.close()



# F.  RANGE QUERIES


def verify_range_queries():
    print("\n══ F. Range Query Routing (Scatter-Gather) ══════════════════")

    # Age range 18–22 — members span all 3 shards
    members = range_members_by_age(18, 22)
    shards_touched = set(m["_shard"] for m in members)
    check(
        f"range_members_by_age(18, 22) spans {len(shards_touched)} shards",
        len(shards_touched) >= 2,
        f"Members found: {len(members)}  Shards touched: {sorted(shards_touched)}"
    )
    check(
        "range_members_by_age result is sorted by Member_ID",
        members == sorted(members, key=lambda r: int(r["Member_ID"][1:])),
    )

    # Booking date range spanning all Feb 2026 — should cover all shards
    bookings = range_bookings_by_date("2026-02-01", "2026-02-20")
    b_shards = set(b["_shard"] for b in bookings)
    check(
        f"range_bookings_by_date('2026-02-01','2026-02-20') spans {len(b_shards)} shards",
        len(b_shards) >= 2,
        f"Bookings found: {len(bookings)}  Shards touched: {sorted(b_shards)}"
    )
    check(
        "range_bookings_by_date result is sorted by Time_In",
        bookings == sorted(bookings, key=lambda r: r["Time_In"])
    )

    # Attendance date range
    att = range_attendance_by_date("2026-02-01", "2026-02-20")
    a_shards = set(a["_shard"] for a in att)
    check(
        f"range_attendance_by_date spans {len(a_shards)} shards (all expected)",
        len(a_shards) >= 2,
        f"Records found: {len(att)}  Shards: {sorted(a_shards)}"
    )

    # list_all_members — scatter from all 3 shards
    all_m = list_all_members()
    all_m_shards = set(m["_shard"] for m in all_m)
    check(
        f"list_all_members() pulls from all {NUM_SHARDS} shards",
        len(all_m_shards) == NUM_SHARDS,
        f"Total members across shards: {len(all_m)}  Shards: {sorted(all_m_shards)}"
    )

    # Narrow range — age=18 covers M01 (shard 1) and M21 (shard 0) — spans 2 shards
    narrow = range_members_by_age(18, 18)
    narrow_shards = set(m["_shard"] for m in narrow)
    narrow_ids = [m["Member_ID"] for m in narrow]
    check(
        f"range_members_by_age(18, 18) returns exactly M01 and M21 (spans 2 shards)",
        set(narrow_ids) == {"M01", "M21"} and len(narrow_shards) == 2,
        f"IDs: {narrow_ids}  Shards: {sorted(narrow_shards)}"
    )



# Summary

def print_summary():
    print("\n══ SUMMARY ═════════════════════════════════════════════════")
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    total  = len(results)
    print(f"  {passed}/{total} checks passed   {failed} failed")
    if failed:
        print("\n  Failed checks:")
        for name, ok in results:
            if not ok:
                print(f"    False {name}")
    return failed == 0


if __name__ == "__main__":
    verify_row_counts()
    verify_no_duplicates()
    verify_shard_correctness()
    verify_lookup_routing()
    verify_insert_routing()
    verify_range_queries()
    ok = print_summary()
    sys.exit(0 if ok else 1)
