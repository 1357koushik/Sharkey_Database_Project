"""
init_shards.py — initialize MySQL shard instances.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shard_config import NUM_SHARDS, ensure_all_shards_ready, seed_demo_data, shard_label, shard_hostname


def init_all_shards():
    ensure_all_shards_ready()
    seed_demo_data(reset=True)
    for sid in range(NUM_SHARDS):
        print(f"  [OK] {shard_label(sid)} initialised on {shard_hostname(sid)}")
    print(f"All {NUM_SHARDS} MySQL shards ready.")


if __name__ == "__main__":
    init_all_shards()
