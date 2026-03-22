from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

facilities_bp = Blueprint("facilities", __name__, url_prefix="/facilities")

@facilities_bp.route("/", methods=["GET"])
@login_required
def list_facilities():
    db = get_db()
    rows = db.execute("SELECT * FROM Facility").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@facilities_bp.route("/<int:facility_id>", methods=["PUT"])
@admin_required
def update_facility(facility_id):
    data = request.get_json(silent=True) or {}
    allowed = ["Status", "Facility_Description"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields"}), 400
    db = get_db()
    try:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        db.execute(f"UPDATE Facility SET {set_clause} WHERE Facility_ID=?",
                   list(updates.values()) + [facility_id])
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "UPDATE", "Facility", str(facility_id), str(updates), request.remote_addr, "SUCCESS")
        return jsonify({"message": "Facility updated"}), 200
    finally:
        db.close()
