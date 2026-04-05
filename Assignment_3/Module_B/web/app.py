"""
app.py — Assignment 3, Module B  —  Web Server
================================================
Flask API + UI demonstrating ACID transactions on the B+ Tree engine.

Run from Module_B/web/:
    pip install flask
    python app.py
    open http://localhost:5001

Uses the replacement Module_A implementation wired through web/database.py.
"""
import sys, os
# Allow importing from Module_A/engine
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, _root)
_mod_a = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Module_A"))
sys.path.insert(0, _mod_a)

import threading, time, uuid
from waitress import serve
from flask import Flask, jsonify, request, render_template
from database import (
    tm,
    TABLES,
    members_table,
    facilities_table,
    bookings_table,
    complaints_table,
    next_booking_id,
    next_complaint_id,
    today_str,
)
from bplustree import BPlusTree

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── helpers ───────────────────────────────────────────────────────────────────
def table_snapshot():
    return {name: [v for _, v in table.get_all()] for name, table in TABLES.items()}
def err(msg, code=400): return jsonify({"ok": False, "error": msg}), code
def ok_r(data):          return jsonify({"ok": True, **data})

VALID_FACILITY_STATUSES = {"Available", "Maintenance", "Closed"}
VALID_COMPLAINT_STATUSES = {"Open", "Resolved"}


def _member(member_id):
    return members_table.get(member_id)


def _facility(facility_id):
    return facilities_table.get(facility_id)


def _booking_overlap(facility_id, time_in, time_out, exclude_booking_id=None):
    for booking_id, booking in bookings_table.get_all():
        if exclude_booking_id is not None and booking_id == exclude_booking_id:
            continue
        if booking["Facility_ID"] != facility_id:
            continue
        existing_start = booking["Time_In"]
        existing_end = booking["Time_Out"] or booking["Time_In"]
        candidate_end = time_out or time_in
        if not (candidate_end < existing_start or time_in > existing_end):
            return booking
    return None


def _validate_facility_status(status):
    if status not in VALID_FACILITY_STATUSES:
        raise ValueError(f"Consistency violation: facility status must be one of {sorted(VALID_FACILITY_STATUSES)}")


def _validate_complaint_status(status):
    if status not in VALID_COMPLAINT_STATUSES:
        raise ValueError(f"Consistency violation: complaint status must be one of {sorted(VALID_COMPLAINT_STATUSES)}")


def _validate_booking_window(time_in, time_out):
    if time_out and time_out < time_in:
        raise ValueError("Consistency violation: Time_Out cannot be earlier than Time_In")


def _coerce_key(table_name, key):
    table = TABLES.get(table_name)
    if table is None:
        return key
    dtype = table.schema.get(table.search_key)
    if dtype == "int":
        return int(key)
    return key

def _cleanup_stress_artifacts(facility_id: int, member_ids: list[str], booking_ids: list[int]):
    tm._acquire("Booking", "Facility", "Member")
    try:
        for booking_id in booking_ids:
            if bookings_table.get(booking_id):
                bookings_table._raw_delete(booking_id)
        if facilities_table.get(facility_id):
            facilities_table._raw_delete(facility_id)
        for member_id in member_ids:
            if members_table.get(member_id):
                members_table._raw_delete(member_id)
    finally:
        tm._release("Booking", "Facility", "Member")

def _book_facility_slot(member_id: str, facility_id: int, booking_id: int, time_in: str, time_out: str, delay_ms: int = 40):
    txn = tm.begin()
    started = time.perf_counter()
    tm._acquire("Booking", "Facility", "Member")
    try:
        member = members_table.get(member_id)
        facility = facilities_table.get(facility_id)
        if member is None:
            raise ValueError(f"Member {member_id} not found")
        if facility is None:
            raise ValueError(f"Facility {facility_id} not found")
        _validate_facility_status(facility["Status"])
        if facility["Status"] != "Available":
            raise ValueError("Facility is not available")
        _validate_booking_window(time_in, time_out)
        if _booking_overlap(facility_id, time_in, time_out):
            raise ValueError("Booking conflict: slot already reserved")

        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)

        tm.insert(txn, "Booking", {
            "Booking_ID": booking_id,
            "Facility_ID": facility_id,
            "Member_ID": member_id,
            "Time_In": time_in,
            "Time_Out": time_out,
        })
        tm.commit(txn)
        return {
            "ok": True,
            "member_id": member_id,
            "booking_id": booking_id,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except Exception as e:
        if getattr(txn, "active", False):
            tm.rollback(txn)
        return {
            "ok": False,
            "member_id": member_id,
            "booking_id": booking_id,
            "error": str(e),
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    finally:
        tm._release("Booking", "Facility", "Member")

def _percentile(sorted_vals, pct):
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, int(round((pct / 100.0) * (len(sorted_vals) - 1)))))
    return round(sorted_vals[idx], 2)

def _run_load_stress(total_requests: int, concurrency: int):
    latencies = []
    failures = []
    op_counts = {"tables": 0, "wal": 0}
    count_lock = threading.Lock()
    barrier = threading.Barrier(concurrency)
    requests_per_worker = [total_requests // concurrency] * concurrency
    for i in range(total_requests % concurrency):
        requests_per_worker[i] += 1

    started = time.perf_counter()

    def worker(worker_id: int, request_count: int):
        try:
            barrier.wait(timeout=5)
        except Exception:
            with count_lock:
                failures.append(f"Worker {worker_id}: barrier timeout")
            return

        for iteration in range(request_count):
            op = "tables" if (worker_id + iteration) % 5 else "wal"
            t0 = time.perf_counter()
            try:
                if op == "tables":
                    snap = table_snapshot()
                    if set(snap.keys()) != {"Member", "Facility", "Booking", "Complaint"}:
                        raise ValueError("Table snapshot shape mismatch")
                    if not all(isinstance(rows, list) for rows in snap.values()):
                        raise ValueError("Table snapshot contains non-list data")
                else:
                    summary = tm.wal_summary()
                    if "total" not in summary or "recent" not in summary:
                        raise ValueError("WAL summary missing expected fields")
                latency = round((time.perf_counter() - t0) * 1000, 2)
                with count_lock:
                    latencies.append(latency)
                    op_counts[op] += 1
            except Exception as e:
                latency = round((time.perf_counter() - t0) * 1000, 2)
                with count_lock:
                    latencies.append(latency)
                    failures.append(str(e))

    threads = [
        threading.Thread(target=worker, args=(idx, requests_per_worker[idx]), daemon=True)
        for idx in range(concurrency)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(30)

    duration_s = max(time.perf_counter() - started, 0.001)
    sorted_lat = sorted(latencies)
    successes = len(latencies) - len(failures)
    unique_failures = {}
    for msg in failures:
        unique_failures[msg] = unique_failures.get(msg, 0) + 1

    return {
        "test": "Stress Testing",
        "passed": len(failures) == 0 and len(latencies) == total_requests,
        "verdict": (
            "✅ PASS — system stayed correct under load with stable response times"
            if len(failures) == 0 and len(latencies) == total_requests else
            "❌ FAIL — errors or incomplete responses occurred during load"
        ),
        "total_requests": total_requests,
        "concurrency": concurrency,
        "completed_requests": len(latencies),
        "successful_requests": successes,
        "failed_requests": len(failures),
        "throughput_rps": round(len(latencies) / duration_s, 2),
        "avg_latency_ms": round(sum(sorted_lat) / len(sorted_lat), 2) if sorted_lat else 0.0,
        "p95_latency_ms": _percentile(sorted_lat, 95),
        "max_latency_ms": round(sorted_lat[-1], 2) if sorted_lat else 0.0,
        "duration_s": round(duration_s, 2),
        "op_counts": op_counts,
        "errors": unique_failures,
        "latency_ms": sorted_lat,
    }

# ── UI ────────────────────────────────────────────────────────────────────────
@app.route("/")
def index(): return render_template("index.html")

# ── Tables ────────────────────────────────────────────────────────────────────
@app.route("/api/tables")
def get_tables(): return ok_r({"tables": table_snapshot()})

# ── WAL ───────────────────────────────────────────────────────────────────────
@app.route("/api/wal")
def get_wal(): return ok_r(tm.wal_summary())

# ── Manual transaction API ────────────────────────────────────────────────────
_sessions: dict[str, object] = {}

@app.route("/api/txn/begin", methods=["POST"])
def txn_begin():
    txn = tm.begin(); _sessions[txn.txn_id] = txn
    return ok_r({"txn_id": txn.txn_id, "state": "ACTIVE"})

@app.route("/api/txn/commit", methods=["POST"])
def txn_commit():
    txn_id = (request.get_json() or {}).get("txn_id")
    txn = _sessions.get(txn_id)
    if txn is None: return err("Transaction not found")
    try:
        tm.commit(txn); _sessions.pop(txn_id, None)
        return ok_r({"txn_id": txn_id, "state": "COMMITTED", "tables": table_snapshot()})
    except Exception as e: return err(str(e))

@app.route("/api/txn/rollback", methods=["POST"])
def txn_rollback():
    txn_id = (request.get_json() or {}).get("txn_id")
    txn = _sessions.get(txn_id)
    if txn is None: return err("Transaction not found")
    try:
        tm.rollback(txn); _sessions.pop(txn_id, None)
        return ok_r({"txn_id": txn_id, "state": "ABORTED", "tables": table_snapshot()})
    except Exception as e: return err(str(e))

@app.route("/api/txn/insert", methods=["POST"])
def txn_insert():
    b = request.get_json() or {}
    txn = _sessions.get(b.get("txn_id"))
    if txn is None: return err("Transaction not found")
    try: tm.insert(txn, b["table"], b["record"]); return ok_r({"op": "INSERT"})
    except Exception as e: return err(str(e))

@app.route("/api/txn/update", methods=["POST"])
def txn_update():
    b = request.get_json() or {}
    txn = _sessions.get(b.get("txn_id"))
    if txn is None: return err("Transaction not found")
    try: tm.update(txn, b["table"], _coerce_key(b["table"], b["key"]), b["record"]); return ok_r({"op": "UPDATE"})
    except Exception as e: return err(str(e))

@app.route("/api/txn/delete", methods=["POST"])
def txn_delete():
    b = request.get_json() or {}
    txn = _sessions.get(b.get("txn_id"))
    if txn is None: return err("Transaction not found")
    try: tm.delete(txn, b["table"], _coerce_key(b["table"], b["key"])); return ok_r({"op": "DELETE"})
    except Exception as e: return err(str(e))

# ── ACID Demos ────────────────────────────────────────────────────────────────
@app.route("/api/acid/atomicity", methods=["POST"])
def demo_atomicity():
    member = members_table.get("M01")
    facility = facilities_table.get(1)
    if not member or not facility:
        return err("Seed data missing")
    complaint_id = next_complaint_id()
    booking_id = next_booking_id()
    pre = {
        "facility_status": facility["Status"],
        "booking_count": len(bookings_table.get_all()),
        "complaint_count": len(complaints_table.get_all()),
    }
    steps = []
    txn = tm.begin()
    steps.append({"step": 1, "action": f"BEGIN {txn.txn_id}"})
    try:
        tm.insert(txn, "Booking", {
            "Booking_ID": booking_id,
            "Facility_ID": 1,
            "Member_ID": "M01",
            "Time_In": "2026-04-05 10:00:00",
            "Time_Out": "2026-04-05 11:00:00",
        })
        steps.append({"step": 2, "action": f"INSERT Booking — #{booking_id} for M01", "ok": True})
        tm.update(txn, "Facility", 1, {**facility, "Status": "Maintenance"})
        steps.append({"step": 3, "action": "UPDATE Facility — Football Ground -> Maintenance", "ok": True})
        tm.insert(txn, "Complaint", {
            "Complaint_ID": complaint_id,
            "Member_ID": "M01",
            "Description": "Atomicity test temporary complaint",
            "Status": "Open",
            "Date": today_str(),
            "Resolved_By": "",
        })
        steps.append({"step": 4, "action": f"INSERT Complaint — {complaint_id}", "ok": True})
        steps.append({"step": 5, "action": "⚡ CRASH injected — power failure!", "crash": True})
        raise RuntimeError("SIMULATED CRASH: power failure mid-transaction")
    except RuntimeError as e:
        tm.rollback(txn)
        steps.append({"step": 6, "action": f"ROLLBACK triggered — {e}", "ok": True})
    post = {
        "facility_status": facilities_table.get(1)["Status"],
        "booking_count": len(bookings_table.get_all()),
        "complaint_count": len(complaints_table.get_all()),
    }
    unchanged = post == pre
    return ok_r({
        "test": "Atomicity", "passed": unchanged, "steps": steps,
        "pre": pre,
        "post": post,
        "verdict": ("✅ PASS — all changes rolled back, database identical to pre-crash"
                    if unchanged else "❌ FAIL — partial data detected"),
    })

@app.route("/api/acid/consistency", methods=["POST"])
def demo_consistency():
    facility = facilities_table.get(2)
    if not facility:
        return err("Seed data missing")
    pre_status = facility["Status"]
    steps = []
    txn = tm.begin()
    steps.append({"step": 1, "action": f"BEGIN {txn.txn_id}"})
    passed = False; violation_msg = None
    try:
        bad = "Broken"
        steps.append({"step": 2, "action": f"Attempt SET Facility.Status = {bad} (invalid)"})
        _validate_facility_status(bad)
        tm.update(txn, "Facility", 2, {**facility, "Status": bad})
        tm.commit(txn)
    except ValueError as e:
        violation_msg = str(e); tm.rollback(txn)
        steps.append({"step": 3, "action": f"ROLLBACK — {e}", "ok": True}); passed = True
    post_status = facilities_table.get(2)["Status"]
    return ok_r({
        "test": "Consistency", "passed": passed, "steps": steps,
        "pre_status": pre_status, "post_status": post_status, "violation": violation_msg,
        "verdict": ("✅ PASS — invalid facility update rejected, relation stayed valid"
                    if passed else "❌ FAIL — invalid facility status was accepted"),
    })

@app.route("/api/acid/isolation", methods=["POST"])
def demo_isolation():
    facility = facilities_table.get(2)
    if not facility:
        return err("Seed data missing")
    results, log, barrier = [], [], threading.Barrier(2)
    def txn_a():
        txn = tm.begin(); log.append(f"[A] BEGIN {txn.txn_id}"); barrier.wait(timeout=5)
        row = facilities_table.get(2); rv = row["Status"]
        log.append(f"[A] READ Facility 2 status = {rv}"); time.sleep(0.08)
        tm.update(txn, "Facility", 2, {**row, "Status": "Maintenance"}); tm.commit(txn)
        log.append("[A] COMMIT — wrote status = Maintenance"); results.append(("A", "Maintenance"))
    def txn_b():
        barrier.wait(timeout=5); txn = tm.begin()
        log.append(f"[B] BEGIN {txn.txn_id}")
        row = facilities_table.get(2); rv = row["Status"]
        log.append(f"[B] READ Facility 2 status = {rv} (must be original, not A's dirty write)")
        tm.commit(txn); log.append("[B] COMMIT (read-only)"); results.append(("B", rv))
    ta = threading.Thread(target=txn_a, daemon=True)
    tb = threading.Thread(target=txn_b, daemon=True)
    ta.start(); tb.start(); ta.join(10); tb.join(10)
    final = facilities_table.get(2)["Status"]
    b_val = next((v for n,v in results if n=="B"), None)
    passed = (b_val == facility["Status"])
    # restore demo state
    if final != facility["Status"]:
        fix = tm.begin()
        tm.update(fix, "Facility", 2, {**facility})
        tm.commit(fix)
    return ok_r({
        "test": "Isolation", "passed": passed, "log": log,
        "initial_status": facility["Status"],
        "txn_b_read_status": b_val, "final_status": final,
        "verdict": ("✅ PASS — Txn B read original facility state; no dirty read"
                    if passed else "❌ FAIL — dirty read detected"),
    })

@app.route("/api/acid/durability", methods=["POST"])
def demo_durability():
    booking_id = next_booking_id()
    new_booking = {
        "Booking_ID": booking_id,
        "Facility_ID": 3,
        "Member_ID": "M03",
        "Time_In": "2026-04-05 16:00:00",
        "Time_Out": "2026-04-05 17:00:00",
    }
    steps = []
    txn = tm.begin(); tm.insert(txn, "Booking", new_booking); tm.commit(txn)
    steps.append({"step": 1, "action": f"INSERT + COMMIT booking #{booking_id} — WAL fsync'd"})
    steps.append({"step": 2, "action": f"Record exists: {bookings_table.get(booking_id) is not None}"})
    bookings_table.tree = BPlusTree(4)
    steps.append({"step": 3, "action": "B+ Tree wiped — simulates restart", "crash": True})
    steps.append({"step": 4, "action": f"Record after wipe: {bookings_table.get(booking_id)}"})
    summary = tm.recover()
    steps.append({"step": 5, "action": f"ARIES recovery — REDOed {len(summary['committed'])} committed txns"})
    after = bookings_table.get(booking_id)
    steps.append({"step": 6, "action": f"Record after recovery: {after}"})
    passed = after is not None and after["Booking_ID"] == booking_id
    try:
        t2 = tm.begin(); tm.delete(t2, "Booking", booking_id); tm.commit(t2)
    except Exception: pass
    return ok_r({
        "test": "Durability", "passed": passed, "steps": steps,
        "recovery_summary": summary,
        "verdict": ("✅ PASS — committed booking restored from WAL after restart"
                    if passed else "❌ FAIL — booking not found after recovery"),
    })

@app.route("/api/acid/multi", methods=["POST"])
def demo_multi():
    body = request.get_json() or {}
    member_id = body.get("member_id", "M04")
    facility_id = int(body.get("facility_id", 4))
    member = members_table.get(member_id)
    facility = facilities_table.get(facility_id)
    if not member: return err(f"Member {member_id} not found")
    if not facility: return err(f"Facility {facility_id} not found")
    inject_fail = body.get("inject_fail", False)
    booking_id = next_booking_id()
    complaint_id = next_complaint_id()
    steps, pre = [], {
        "facility_status": facility["Status"],
        "booking_count": len(bookings_table.get_all()),
        "complaint_count": len(complaints_table.get_all()),
    }
    txn = tm.begin()
    steps.append({"step": 1, "action": f"BEGIN {txn.txn_id} — 3-table transaction"})
    committed = False
    injected_failure_triggered = False
    rollback_detail = None
    error_message = None
    try:
        _validate_facility_status(facility["Status"])
        if facility["Status"] != "Available":
            raise ValueError(f"Facility {facility_id} is currently {facility['Status']}")
        tm.insert(txn, "Booking", {
            "Booking_ID": booking_id,
            "Facility_ID": facility_id,
            "Member_ID": member_id,
            "Time_In": "2026-04-06 10:00:00",
            "Time_Out": "2026-04-06 11:00:00",
        })
        steps.append({"step": 2, "action": f"INSERT Booking.{booking_id} for {member_id}", "ok": True})
        tm.update(txn, "Facility", facility_id, {**facility, "Status": "Maintenance"})
        steps.append({"step": 3, "action": f"UPDATE Facility.{facility_id}: status -> Maintenance", "ok": True})
        if inject_fail:
            injected_failure_triggered = True
            steps.append({"step": 4, "action": "⚡ Failure injected before INSERT", "crash": True})
            raise RuntimeError("Injected failure — testing 3-table atomicity")
        tm.insert(txn, "Complaint", {
            "Complaint_ID": complaint_id,
            "Member_ID": member_id,
            "Description": f"Post-booking inspection for facility {facility_id}",
            "Status": "Open",
            "Date": today_str(),
            "Resolved_By": "",
        })
        steps.append({"step": 4, "action": f"INSERT Complaint: {complaint_id}", "ok": True})
        tm.commit(txn)
        steps.append({"step": 5, "action": "COMMIT — all 3 tables updated ✅", "ok": True})
        committed = True
    except Exception as e:
        error_message = str(e)
        tm.rollback(txn)
        if injected_failure_triggered:
            rollback_detail = f"Injected failure triggered rollback. Booking {booking_id}, Facility.{facility_id}, and Complaint {complaint_id} were restored."
        else:
            rollback_detail = f"{error_message}. No commit was applied to Booking, Facility, or Complaint."
        steps.append({
            "step": len(steps)+1,
            "action": f"ROLLBACK — {rollback_detail}",
            "ok": True
        })
    post = {
        "facility_status": facilities_table.get(facility_id)["Status"],
        "booking_count": len(bookings_table.get_all()),
        "complaint_count": len(complaints_table.get_all()),
    }
    return ok_r({
        "test": "Multi-Relation (3-table)", "committed": committed,
        "inject_fail": inject_fail, "steps": steps, "pre": pre, "post": post,
        "booking_id": booking_id if committed else None,
        "complaint_id": complaint_id if committed else None,
        "verdict": (
            f"✅ All 3 tables updated atomically — booking {booking_id}" if committed else
            "✅ Atomicity confirmed — injected failure rolled Booking, Facility, and Complaint back" if injected_failure_triggered else
            f"ℹ️ Transaction stopped before commit — {error_message}"
        ),
    })


@app.route("/api/acid/multi/facilities/update-all", methods=["POST"])
def update_all_available_facilities():
    maintenance_rows = [
        row for _, row in facilities_table.get_all()
        if row.get("Status") == "Maintenance"
    ]
    pre = {
        "available_facilities": sum(1 for _, row in facilities_table.get_all() if row.get("Status") == "Available"),
        "maintenance_facilities": sum(1 for _, row in facilities_table.get_all() if row.get("Status") == "Maintenance"),
    }
    if not maintenance_rows:
        return ok_r({
            "test": "Facility Bulk Update",
            "committed": True,
            "steps": [{"step": 1, "action": "No maintenance facilities found to update", "ok": True}],
            "pre": pre,
            "post": pre,
            "updated_count": 0,
            "verdict": "ℹ️ No facilities were updated because none are currently marked Maintenance",
        })

    txn = tm.begin()
    steps = [{"step": 1, "action": f"BEGIN {txn.txn_id} — update all maintenance facilities", "ok": True}]
    updated_ids = []
    try:
        for index, facility in enumerate(maintenance_rows, start=2):
            facility_id = facility["Facility_ID"]
            _validate_facility_status(facility["Status"])
            tm.update(txn, "Facility", facility_id, {**facility, "Status": "Available"})
            updated_ids.append(facility_id)
            steps.append({
                "step": index,
                "action": f"UPDATE Facility.{facility_id}: status -> Available",
                "ok": True,
            })
        tm.commit(txn)
        steps.append({
            "step": len(steps) + 1,
            "action": f"COMMIT — {len(updated_ids)} facilities updated ✅",
            "ok": True,
        })
    except Exception as e:
        tm.rollback(txn)
        steps.append({
            "step": len(steps) + 1,
            "action": f"ROLLBACK — {e}",
            "ok": True,
        })
        return ok_r({
            "test": "Facility Bulk Update",
            "committed": False,
            "steps": steps,
            "pre": pre,
            "post": {
                "available_facilities": sum(1 for _, row in facilities_table.get_all() if row.get("Status") == "Available"),
                "maintenance_facilities": sum(1 for _, row in facilities_table.get_all() if row.get("Status") == "Maintenance"),
            },
            "updated_count": 0,
            "verdict": f"❌ Bulk facility update failed — {e}",
        })

    post = {
        "available_facilities": sum(1 for _, row in facilities_table.get_all() if row.get("Status") == "Available"),
        "maintenance_facilities": sum(1 for _, row in facilities_table.get_all() if row.get("Status") == "Maintenance"),
    }
    return ok_r({
        "test": "Facility Bulk Update",
        "committed": True,
        "steps": steps,
        "pre": pre,
        "post": post,
        "updated_count": len(updated_ids),
        "updated_facility_ids": ", ".join(str(facility_id) for facility_id in updated_ids),
        "verdict": f"✅ Updated {len(updated_ids)} maintenance facilities to Available",
    })

@app.route("/api/acid/recover", methods=["GET"])
def run_recovery():
    return ok_r({"recovery": tm.recover()})

@app.route("/api/acid/stress", methods=["POST"])
def demo_stress():
    body = request.get_json() or {}
    attempts = max(2, min(int(body.get("attempts", 12)), 40))
    initial_slots = max(1, min(int(body.get("stock", 1)), 3))
    delay_ms = max(0, min(int(body.get("delay_ms", 40)), 250))

    run_id = uuid.uuid4().hex[:6].upper()
    facility_id = 900 + int(run_id[:2], 16) % 50
    members = []
    for i in range(attempts):
        member_id = f"MX{run_id}{i+1:02d}"
        members.append({
            "Member_ID": member_id,
            "Name": f"Stress Member {i+1}",
            "Gender": "M" if i % 2 == 0 else "F",
            "Email": f"stress{run_id.lower()}{i+1}@iitgn.ac.in",
            "Phone_Number": f"97{int(run_id[:4], 16) % 1000000:06d}{i+1:02d}",
            "Age": 20 + (i % 5),
            "DOB": "",
            "Image": "",
        })

    tm._acquire("Facility", "Member")
    try:
        facilities_table._raw_insert(facility_id, {
            "Facility_ID": facility_id,
            "Facility_Name": f"Stress Court {run_id}",
            "Facility_Description": f"Temporary race-condition facility {run_id}",
            "Status": "Available",
        })
        for member in members:
            members_table._raw_insert(member["Member_ID"], member)
    finally:
        tm._release("Facility", "Member")

    results = []
    booking_ids = []
    results_lock = threading.Lock()
    barrier = threading.Barrier(attempts)
    time_in = "2026-04-07 09:00:00"
    time_out = "2026-04-07 10:00:00"

    def worker(idx: int, member_id: str):
        booking_id = next_booking_id() + idx
        try:
            barrier.wait(timeout=5)
            result = _book_facility_slot(member_id, facility_id, booking_id, time_in, time_out, delay_ms)
        except Exception as e:
            result = {
                "ok": False,
                "member_id": member_id,
                "booking_id": booking_id,
                "error": f"Thread sync failure: {e}",
                "latency_ms": 0,
            }
        with results_lock:
            results.append(result)
            if result["ok"]:
                booking_ids.append(booking_id)

    threads = [
        threading.Thread(target=worker, args=(idx, member["Member_ID"]), daemon=True)
        for idx, member in enumerate(members)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(10)

    final_facility = facilities_table.get(facility_id) or {}
    stress_bookings = [
        row for _, row in bookings_table.get_all()
        if row["Facility_ID"] == facility_id and row["Time_In"] == time_in
    ]

    success_count = sum(1 for r in results if r["ok"])
    reject_count = attempts - success_count
    final_status = final_facility.get("Status")
    expected_success = min(initial_slots, 1)
    latency_ms = sorted(r["latency_ms"] for r in results)
    error_counts = {}
    for item in results:
        if item["ok"]:
            continue
        error_counts[item["error"]] = error_counts.get(item["error"], 0) + 1

    passed = (
        len(results) == attempts and
        success_count == expected_success and
        final_status == "Available" and
        len(stress_bookings) == success_count
    )

    summary = {
        "test": "Race Condition Test",
        "critical_operation": "Book the same facility slot concurrently",
        "passed": passed,
        "verdict": (
            "✅ PASS — concurrent bookings stayed correct; no double-booking occurred"
            if passed else
            "❌ FAIL — race-condition checks found inconsistent booking results"
        ),
        "attempts": attempts,
        "initial_stock": initial_slots,
        "successful_bookings": success_count,
        "rejected_bookings": reject_count,
        "final_stock": len(stress_bookings),
        "expected_final_stock": expected_success,
        "orders_created": len(stress_bookings),
        "delay_ms": delay_ms,
        "latency_ms": latency_ms,
        "errors": error_counts,
        "results": sorted(results, key=lambda item: item["member_id"]),
    }

    _cleanup_stress_artifacts(facility_id, [m["Member_ID"] for m in members], booking_ids)
    return ok_r(summary)

@app.route("/api/stress/load", methods=["POST"])
def demo_load_stress():
    body = request.get_json() or {}
    total_requests = max(100, min(int(body.get("requests", 500)), 5000))
    concurrency = max(2, min(int(body.get("concurrency", 20)), 100))
    if concurrency > total_requests:
        concurrency = total_requests
    return ok_r(_run_load_stress(total_requests, concurrency))

if __name__ == "__main__":
    print("=" * 55)
    print("  CS432 Assignment 3 — Module B Web Server")
    print("  IIT Gandhinagar · http://localhost:5001")
    print("=" * 55)
    serve(app, host='0.0.0.0', port=5001)
