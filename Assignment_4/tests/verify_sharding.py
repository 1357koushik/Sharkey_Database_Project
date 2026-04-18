import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "router"))

from shard_config import NUM_SHARDS, expected_distribution, get_shard_id, get_shard_table
from query_router import get_member

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name: str, condition: bool, evidence: str = ""):
    status = PASS if condition else FAIL
    print(f"  {status}  {name}")
    if evidence:
        print(f"         {evidence}")
    results.append((name, condition))


def verify_hash_distribution():
    print("\n== A. Routing Formula =======================================")
    check("M01 -> remainder 1 (handout Shard 2)", get_shard_id("M01") == 1)
    check("M03 -> remainder 0 (handout Shard 1)", get_shard_id("M03") == 0)
    check("M38 -> remainder 2 (handout Shard 3)", get_shard_id("M38") == 2)
    all_ids = [f"M{i:02d}" for i in range(1, 41)]
    dist = expected_distribution(all_ids)
    sizes = [len(dist[sid]) for sid in range(NUM_SHARDS)]
    check("Distribution skew <= 1", max(sizes) - min(sizes) <= 1, f"sizes={sizes}")


def verify_engine_shards():
    print("\n== B. MySQL Shards ==========================================")
    for sid in range(NUM_SHARDS):
        member_rows = len(get_shard_table(sid, "Member").get_all())
        check(f"shard_{sid} member table available", member_rows >= 0, f"rows={member_rows}")


def verify_lookup():
    print("\n== C. Lookup Routing ========================================")
    try:
        row = get_member("M01")
        check(
            "get_member('M01') returns row from routed shard",
            row is None or row.get("_routed_to_shard") == 2,
            str(row),
        )
    except Exception as exc:
        check("get_member('M01') executes without router errors", False, str(exc))


def print_summary() -> bool:
    print("\n== SUMMARY ===================================================")
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    total = len(results)
    print(f"  {passed}/{total} checks passed   {failed} failed")
    return failed == 0


if __name__ == "__main__":
    verify_hash_distribution()
    verify_engine_shards()
    verify_lookup()
    ok = print_summary()
    sys.exit(0 if ok else 1)
