from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

@attendance_bp.route("/", methods=["GET"])
@login_required
def list_attendance():
    db = get_db()
    user = request.current_user
    if user["role"] == "admin":
        rows = db.execute(
            """SELECT a.*, m.Name FROM Attendance a JOIN Member m ON a.Member_ID=m.Member_ID
               ORDER BY a.Date DESC"""
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM Attendance WHERE Member_ID=? ORDER BY Date DESC",
            (user["member_id"],)
        ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@attendance_bp.route("/", methods=["POST"])
@admin_required
def mark_attendance():
    data = request.get_json(silent=True) or {}
    for f in ["Member_ID", "Session", "Date", "Status"]:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Attendance (Member_ID, Session, Date, Status) VALUES (?,?,?,?)",
            (data["Member_ID"], data["Session"], data["Date"], data["Status"])
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "CREATE", "Attendance", data["Member_ID"],
                   f"{data['Session']} {data['Date']} {data['Status']}", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Attendance marked"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()
