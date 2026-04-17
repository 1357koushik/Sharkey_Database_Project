"""
sharded_app.py  —  Minimal Flask API demonstrating shard-aware routing
=======================================================================
Extends the Assignment 2 members API.  Every endpoint uses the
query_router module to direct requests to the correct shard.

Run:  python3 sharded_app.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "router"))

from flask import Flask, jsonify, request
from query_router import (
    get_member, get_member_bookings, get_member_complaints,
    get_player_stats, insert_member, insert_booking, insert_attendance,
    range_members_by_age, range_bookings_by_date,
    range_attendance_by_date, list_all_members
)
from shard_config import get_shard_id, NUM_SHARDS

app = Flask(__name__)


# ── Utility ─────────────────────────────────────────────────────────

def shard_meta(member_id: str) -> dict:
    sid = get_shard_id(member_id)
    return {"shard_id": sid, "shard_db": f"shard_{sid}.db",
            "routing_formula": f"int('{member_id[1:]}') % {NUM_SHARDS} = {sid}"}


# ── Lookup endpoints ─────────────────────────────────────────────────

@app.route("/shards/members/<member_id>", methods=["GET"])
def api_get_member(member_id):
    """Lookup: routed to a single shard."""
    m = get_member(member_id)
    if not m:
        return jsonify({"error": "Member not found",
                        **shard_meta(member_id)}), 404
    return jsonify({**m, "_routing": shard_meta(member_id)}), 200


@app.route("/shards/members/<member_id>/bookings", methods=["GET"])
def api_get_member_bookings(member_id):
    bookings = get_member_bookings(member_id)
    return jsonify({"member_id": member_id,
                    "bookings": bookings,
                    "_routing": shard_meta(member_id)}), 200


@app.route("/shards/members/<member_id>/complaints", methods=["GET"])
def api_get_member_complaints(member_id):
    complaints = get_member_complaints(member_id)
    return jsonify({"member_id": member_id,
                    "complaints": complaints,
                    "_routing": shard_meta(member_id)}), 200


@app.route("/shards/members/<member_id>/stats", methods=["GET"])
def api_get_player_stats(member_id):
    stats = get_player_stats(member_id)
    return jsonify({"member_id": member_id,
                    "stats": stats,
                    "_routing": shard_meta(member_id)}), 200


# ── Insert endpoints ─────────────────────────────────────────────────

@app.route("/shards/members", methods=["POST"])
def api_insert_member():
    """Insert: routed to the correct shard based on Member_ID."""
    data = request.get_json(silent=True) or {}
    result = insert_member(data)
    if not result["ok"]:
        return jsonify(result), 400
    return jsonify({**result,
                    "_routing": shard_meta(data["Member_ID"])}), 201


@app.route("/shards/bookings", methods=["POST"])
def api_insert_booking():
    data = request.get_json(silent=True) or {}
    result = insert_booking(data)
    if not result["ok"]:
        return jsonify(result), 400
    return jsonify({**result,
                    "_routing": shard_meta(data["Member_ID"])}), 201


@app.route("/shards/attendance", methods=["POST"])
def api_insert_attendance():
    data = request.get_json(silent=True) or {}
    result = insert_attendance(data)
    if not result["ok"]:
        return jsonify(result), 400
    return jsonify({**result,
                    "_routing": shard_meta(data["Member_ID"])}), 201


# ── Range / scatter-gather endpoints ─────────────────────────────────

@app.route("/shards/members", methods=["GET"])
def api_list_members():
    """Range query: scatter to all shards, gather results."""
    age_min = request.args.get("age_min", type=int)
    age_max = request.args.get("age_max", type=int)
    if age_min is not None and age_max is not None:
        members = range_members_by_age(age_min, age_max)
    else:
        members = list_all_members()
    return jsonify({"count": len(members),
                    "shards_queried": NUM_SHARDS,
                    "members": members}), 200


@app.route("/shards/bookings", methods=["GET"])
def api_range_bookings():
    date_start = request.args.get("date_start", "2026-01-01")
    date_end   = request.args.get("date_end",   "2026-12-31")
    bookings = range_bookings_by_date(date_start, date_end)
    return jsonify({"count": len(bookings),
                    "shards_queried": NUM_SHARDS,
                    "date_range": f"{date_start} → {date_end}",
                    "bookings": bookings}), 200


@app.route("/shards/attendance", methods=["GET"])
def api_range_attendance():
    date_start = request.args.get("date_start", "2026-01-01")
    date_end   = request.args.get("date_end",   "2026-12-31")
    att = range_attendance_by_date(date_start, date_end)
    return jsonify({"count": len(att),
                    "shards_queried": NUM_SHARDS,
                    "attendance": att}), 200


# ── Diagnostics ───────────────────────────────────────────────────────

@app.route("/shards/info", methods=["GET"])
def api_shard_info():
    """Returns shard topology metadata."""
    from shard_config import SHARD_PATHS, expected_distribution
    all_ids = [f"M{i:02d}" for i in range(1, 41)]
    dist = expected_distribution(all_ids)
    return jsonify({
        "num_shards": NUM_SHARDS,
        "strategy": "hash-based",
        "shard_key": "Member_ID",
        "routing_formula": "int(member_id[1:]) % num_shards",
        "shard_paths": SHARD_PATHS,
        "distribution": {f"shard_{k}": v for k, v in dist.items()}
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
