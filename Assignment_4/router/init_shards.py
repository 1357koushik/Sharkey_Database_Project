"""
init_shards.py — initialize Assignment 3 engine shard instances.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shard_config import NUM_SHARDS, seed_demo_data, shard_label, shard_hostname


def init_all_shards():
    seed_demo_data(reset=True)
    for sid in range(NUM_SHARDS):
        print(f"  [OK] {shard_label(sid)} initialised on {shard_hostname(sid)}")
    print(f"All {NUM_SHARDS} Assignment 3 engine shards ready.")


if __name__ == "__main__":
    init_all_shards()
