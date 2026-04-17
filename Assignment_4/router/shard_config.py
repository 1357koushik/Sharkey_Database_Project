"""
shard_config.py  —  Central shard configuration for IIT Gandhinagar Sports Club DB
===================================================================================
Shard Key  : Member_ID  (e.g. 'M01' … 'M40')
Strategy   : Hash-based  →  shard_id = int(member_id[1:]) % NUM_SHARDS
Num Shards : 3           →  shard_0, shard_1, shard_2 (separate SQLite databases)
Simulation : Multiple SQLite database files on the same host (simulating separate nodes)

Why Member_ID?
  • High Cardinality  : 40 distinct IDs today; grows with every new registration.
  • Query-Aligned     : Every API route that fetches or mutates a member's data uses
                        Member_ID in the WHERE clause (members, bookings, attendance,
                        equipment loans, complaints, player stats, coach, player).
  • Stable            : Member_ID is assigned at registration and never changes.

Why Hash-Based?
  • Deterministic: shard_id = numeric_suffix(member_id) % 3 gives a clean, repeatable map.
  • Even spread  : IDs M01–M40 give 40 values; 40 mod 3 produces counts 14, 13, 13 —
                   maximum skew of ±1 row (< 4%), well within acceptable limits.
  • No lookup table required; routing is O(1).
"""

import os
import sqlite3

NUM_SHARDS = 3

# Each shard lives in its own SQLite file (simulates a separate database node)
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "shards")

SHARD_PATHS = {
    i: os.path.abspath(os.path.join(BASE_DIR, f"shard_{i}.db"))
    for i in range(NUM_SHARDS)
}


def get_shard_id(member_id: str) -> int:
    """
    Derive shard index from Member_ID.
    e.g. 'M01' -> 1 % 3 = 1
         'M03' -> 3 % 3 = 0
         'M40' -> 40 % 3 = 1
    """
    numeric = int(member_id[1:])   # strip leading 'M'
    return numeric % NUM_SHARDS


def get_shard_conn(shard_id: int) -> sqlite3.Connection:
    """Open and return a connection to a specific shard database."""
    conn = sqlite3.connect(SHARD_PATHS[shard_id])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_conn_for_member(member_id: str) -> tuple[sqlite3.Connection, int]:
    """Return (connection, shard_id) for a given Member_ID."""
    sid = get_shard_id(member_id)
    return get_shard_conn(sid), sid


def all_shard_conns() -> list[tuple[sqlite3.Connection, int]]:
    """Open connections to ALL shards (needed for range/scatter queries)."""
    return [(get_shard_conn(i), i) for i in range(NUM_SHARDS)]


# -------------------------------------------------------------------
# Shard distribution preview (for documentation / verification)
# -------------------------------------------------------------------
def expected_distribution(member_ids: list[str]) -> dict:
    dist: dict[int, list[str]] = {i: [] for i in range(NUM_SHARDS)}
    for mid in member_ids:
        dist[get_shard_id(mid)].append(mid)
    return dist


if __name__ == "__main__":
    all_ids = [f"M{i:02d}" for i in range(1, 41)]
    dist = expected_distribution(all_ids)
    for sid, ids in dist.items():
        print(f"Shard {sid} ({len(ids)} members): {ids}")
