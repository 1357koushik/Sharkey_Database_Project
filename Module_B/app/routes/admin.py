import time
from flask import Blueprint, request, jsonify
from auth_utils import admin_required
from audit import log_action
from db import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/logs", methods=["GET"])
@admin_required
def get_audit_logs():
    limit = request.args.get("limit", 100, type=int)
    db = get_db()
    rows = db.execute(
        "SELECT * FROM AuditLog ORDER BY Timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    db = get_db()
    rows = db.execute(
        """SELECT ul.User_ID, ul.Username, ul.Role, ul.Is_Active, ul.Member_ID, m.Name
           FROM UserLogin ul JOIN Member m ON ul.Member_ID=m.Member_ID"""
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@admin_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    import hashlib
    data = request.get_json(silent=True) or {}
    for f in ["Member_ID", "Username", "Password", "Role"]:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    pw_hash = hashlib.sha256(data["Password"].encode()).hexdigest()
    db = get_db()
    try:
        db.execute(
            "INSERT INTO UserLogin (Member_ID,Username,Password_Hash,Role) VALUES (?,?,?,?)",
            (data["Member_ID"], data["Username"], pw_hash, data["Role"])
        )
        db.commit()
        log_action(request.current_user["Username"], request.current_user["Member_ID"],
                   "admin", "CREATE", "UserLogin", data["Member_ID"],
                   f"Created user {data['Username']}", request.remote_addr, "SUCCESS")
        return jsonify({"message": "User created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM UserLogin WHERE User_ID=?", (user_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["Username"], request.current_user["Member_ID"],
                   "admin", "DELETE", "UserLogin", str(user_id),
                   "User deleted", request.remote_addr, "SUCCESS")
        return jsonify({"message": "User deleted"}), 200
    finally:
        db.close()

@admin_bp.route("/benchmark", methods=["GET"])
@admin_required
def benchmark():
    """
    Run BEFORE and AFTER index benchmarks on key queries.
    Returns timing data for the performance report.
    """
    results = {}
    db = get_db()

    # --- Query 1: Login lookup by username ---
    # Without index simulation: sequential scan (EXPLAIN shows this)
    q1 = "SELECT * FROM UserLogin WHERE Username = ?"
    t0 = time.perf_counter()
    for _ in range(500):
        db.execute(q1, ("admin_rakesh",)).fetchone()
    results["login_username_lookup_ms"] = round((time.perf_counter() - t0) * 1000, 3)

    # --- Query 2: Session token validation ---
    q2 = "SELECT * FROM UserSession WHERE Token = ? AND Is_Valid = 1"
    t0 = time.perf_counter()
    for _ in range(500):
        db.execute(q2, ("nonexistent_token_xyz",)).fetchone()
    results["session_token_lookup_ms"] = round((time.perf_counter() - t0) * 1000, 3)

    # --- Query 3: Booking overlap check (facility + time range) ---
    q3 = "SELECT 1 FROM Booking WHERE Facility_ID=? AND Time_In < ? AND (Time_Out IS NULL OR Time_Out > ?)"
    t0 = time.perf_counter()
    for _ in range(500):
        db.execute(q3, (1, "2026-03-01 14:00:00", "2026-03-01 12:00:00")).fetchone()
    results["booking_overlap_check_ms"] = round((time.perf_counter() - t0) * 1000, 3)

    # --- Query 4: Member attendance by date range ---
    q4 = "SELECT * FROM Attendance WHERE Member_ID=? AND Date BETWEEN ? AND ?"
    t0 = time.perf_counter()
    for _ in range(500):
        db.execute(q4, ("M01", "2026-01-01", "2026-03-01")).fetchall()
    results["attendance_date_range_ms"] = round((time.perf_counter() - t0) * 1000, 3)

    # --- Query 5: Complaint status filter ---
    q5 = "SELECT * FROM Complaint WHERE Status=?"
    t0 = time.perf_counter()
    for _ in range(500):
        db.execute(q5, ("Open",)).fetchall()
    results["complaint_status_filter_ms"] = round((time.perf_counter() - t0) * 1000, 3)

    # --- Query 6: Equipment loans by member ---
    q6 = "SELECT * FROM Equipment_Loan WHERE Member_ID=?"
    t0 = time.perf_counter()
    for _ in range(500):
        db.execute(q6, ("M01",)).fetchall()
    results["equipment_loan_lookup_ms"] = round((time.perf_counter() - t0) * 1000, 3)

    # --- EXPLAIN plans ---
    explain = {}
    for label, q, param in [
        ("login_lookup",    "EXPLAIN QUERY PLAN SELECT * FROM UserLogin WHERE Username=?", ("admin_rakesh",)),
        ("session_token",   "EXPLAIN QUERY PLAN SELECT * FROM UserSession WHERE Token=? AND Is_Valid=1", ("tok",)),
        ("booking_overlap", "EXPLAIN QUERY PLAN SELECT 1 FROM Booking WHERE Facility_ID=? AND Time_In<?", (1,"2026-01-01 00:00:00")),
        ("attendance_range","EXPLAIN QUERY PLAN SELECT * FROM Attendance WHERE Member_ID=? AND Date BETWEEN ? AND ?", ("M01","2026-01-01","2026-03-01")),
        ("complaint_status","EXPLAIN QUERY PLAN SELECT * FROM Complaint WHERE Status=?", ("Open",)),
    ]:
        rows = db.execute(q, param).fetchall()
        explain[label] = [dict(r) for r in rows]

    db.close()
    return jsonify({"timings_500_iterations": results, "explain_plans": explain}), 200

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard_stats():
    db = get_db()
    stats = {}
    stats["total_members"]   = db.execute("SELECT COUNT(*) FROM Member").fetchone()[0]
    stats["total_players"]   = db.execute("SELECT COUNT(*) FROM Player").fetchone()[0]
    stats["total_coaches"]   = db.execute("SELECT COUNT(*) FROM Coach").fetchone()[0]
    stats["total_admins"]    = db.execute("SELECT COUNT(*) FROM Administrator").fetchone()[0]
    stats["total_teams"]     = db.execute("SELECT COUNT(*) FROM Team").fetchone()[0]
    stats["total_events"]    = db.execute("SELECT COUNT(*) FROM Event").fetchone()[0]
    stats["open_complaints"] = db.execute("SELECT COUNT(*) FROM Complaint WHERE Status='Open'").fetchone()[0]
    stats["active_loans"]    = db.execute("SELECT COUNT(*) FROM Equipment_Loan WHERE Return_Time IS NULL").fetchone()[0]
    stats["active_bookings"] = db.execute("SELECT COUNT(*) FROM Booking WHERE Time_Out IS NULL").fetchone()[0]
    stats["recent_logs"]     = db.execute(
        "SELECT Action, Status, Timestamp FROM AuditLog ORDER BY Timestamp DESC LIMIT 10"
    ).fetchall()
    stats["recent_logs"] = [dict(r) for r in stats["recent_logs"]]
    db.close()
    return jsonify(stats), 200
