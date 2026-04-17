from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

coaches_bp = Blueprint("coaches", __name__, url_prefix="/coaches")

@coaches_bp.route("/", methods=["GET"])
@login_required
def list_coaches():
    db = get_db()
    rows = db.execute(
        """SELECT c.Member_ID, c.Coach_ID, c.Sport_ID, c.Years_Experience,
                  c.Salary, c.Joining_Date, s.Sport_Name, m.Name, m.Email, m.Phone_Number
           FROM Coach c
           JOIN Member m ON c.Member_ID = m.Member_ID
           JOIN Sport s  ON c.Sport_ID  = s.Sport_ID"""
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@coaches_bp.route("/", methods=["POST"])
@admin_required
def create_coach():
    data = request.get_json(silent=True) or {}
    for f in ["Member_ID", "Coach_ID", "Sport_ID"]:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            """INSERT INTO Coach (Member_ID, Coach_ID, Sport_ID, Years_Experience, Salary, Joining_Date)
               VALUES (?,?,?,?,?,?)""",
            (data["Member_ID"], data["Coach_ID"], data["Sport_ID"],
             data.get("Years_Experience", 0), data.get("Salary", 0.0),
             data.get("Joining_Date"))
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "CREATE", "Coach", data["Member_ID"],
                   f"Coach created", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Coach created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@coaches_bp.route("/<member_id>", methods=["DELETE"])
@admin_required
def delete_coach(member_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM Coach WHERE Member_ID=?", (member_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Coach", member_id, "", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Coach deleted"}), 200
    finally:
        db.close()
