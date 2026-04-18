"""
migrate_data.py — repartition demo data across MySQL shards.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shard_config import NUM_SHARDS, get_shard_table, seed_demo_data

PARTITIONED_TABLES = ("Member", "Booking", "Complaint", "Attendance", "Player_Stat")
REPLICATED_TABLES = ("Facility",)


def run_migration():
    seed_demo_data(reset=True)
    print("\n-- Partitioning summary ------------------------------------")

    for table_name in PARTITIONED_TABLES:
        counts = []
        for sid in range(NUM_SHARDS):
            counts.append(len(get_shard_table(sid, table_name).get_all()))
        print(
            f"  [PART] {table_name}: {sum(counts)} rows  ->  "
            + "  ".join(f"shard_{sid}:{counts[sid]}" for sid in range(NUM_SHARDS))
        )

    for table_name in REPLICATED_TABLES:
        rows = len(get_shard_table(0, table_name).get_all())
        print(f"  [REF] {table_name}: {rows} rows replicated to all {NUM_SHARDS} shards")

    print("Migration complete.")


if __name__ == "__main__":
    run_migration()
