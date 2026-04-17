from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

events_bp = Blueprint("events", __name__, url_prefix="/events")

@events_bp.route("/", methods=["GET"])
@login_required
def list_events():
    db = get_db()
    rows = db.execute(
        """SELECT e.*, f.Facility_Name FROM Event e
           JOIN Facility f ON e.Facility_ID=f.Facility_ID
           ORDER BY e.Start_Time DESC"""
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@events_bp.route("/", methods=["POST"])
@admin_required
def create_event():
    data = request.get_json(silent=True) or {}
    for f in ["Event_ID", "Event_Name", "Facility_ID", "Description", "Start_Time", "End_Time", "Attendance_Status"]:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Event (Event_ID,Event_Name,Facility_ID,Description,Start_Time,End_Time,Attendance_Status) VALUES (?,?,?,?,?,?,?)",
            (data["Event_ID"], data["Event_Name"], data["Facility_ID"], data["Description"],
             data["Start_Time"], data["End_Time"], data["Attendance_Status"])
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "CREATE", "Event", data["Event_ID"], data["Event_Name"], request.remote_addr, "SUCCESS")
        return jsonify({"message": "Event created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@events_bp.route("/<event_id>", methods=["PUT"])
@admin_required
def update_event(event_id):
    data = request.get_json(silent=True) or {}
    allowed = ["Attendance_Status", "Event_Name", "Description"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields"}), 400
    db = get_db()
    try:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        db.execute(f"UPDATE Event SET {set_clause} WHERE Event_ID=?",
                   list(updates.values()) + [event_id])
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "UPDATE", "Event", event_id, str(updates), request.remote_addr, "SUCCESS")
        return jsonify({"message": "Event updated"}), 200
    finally:
        db.close()

@events_bp.route("/<event_id>", methods=["DELETE"])
@admin_required
def delete_event(event_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM Event WHERE Event_ID=?", (event_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Event", event_id, "", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Event deleted"}), 200
    finally:
        db.close()
