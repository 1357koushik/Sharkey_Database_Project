from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")

@stats_bp.route("/", methods=["GET"])
@login_required
def list_stats():
    db = get_db()
    user = request.current_user
    if user["role"] == "admin":
        rows = db.execute(
            """SELECT ps.*, m.Name FROM Player_Stat ps JOIN Member m ON ps.Member_ID=m.Member_ID
               ORDER BY ps.Recorded_Date DESC"""
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM Player_Stat WHERE Member_ID=? ORDER BY Recorded_Date DESC",
            (user["member_id"],)
        ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@stats_bp.route("/", methods=["POST"])
@admin_required
def create_stat():
    data = request.get_json(silent=True) or {}
    for f in ["Member_ID", "Metric_Name", "Metric_Value", "Recorded_Date"]:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Player_Stat (Member_ID,Event_ID,Metric_Name,Metric_Value,Recorded_Date) VALUES (?,?,?,?,?)",
            (data["Member_ID"], data.get("Event_ID"), data["Metric_Name"],
             data["Metric_Value"], data["Recorded_Date"])
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "CREATE", "Player_Stat", data["Member_ID"],
                   f"{data['Metric_Name']}={data['Metric_Value']}", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Stat recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@stats_bp.route("/<member_id>/<metric_name>/<recorded_date>", methods=["PUT"])
@admin_required
def update_stat(member_id, metric_name, recorded_date):
    data = request.get_json(silent=True) or {}
    if "Metric_Value" not in data:
        return jsonify({"error": "Missing Metric_Value"}), 400
    db = get_db()
    try:
        db.execute(
            "UPDATE Player_Stat SET Metric_Value=? WHERE Member_ID=? AND Metric_Name=? AND Recorded_Date=?",
            (data["Metric_Value"], member_id, metric_name, recorded_date)
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "UPDATE", "Player_Stat", member_id,
                   f"{metric_name}={data['Metric_Value']}", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Stat updated"}), 200
    finally:
        db.close()

@stats_bp.route("/<member_id>/<metric_name>/<recorded_date>", methods=["DELETE"])
@admin_required
def delete_stat(member_id, metric_name, recorded_date):
    db = get_db()
    try:
        result = db.execute(
            "DELETE FROM Player_Stat WHERE Member_ID=? AND Metric_Name=? AND Recorded_Date=?",
            (member_id, metric_name, recorded_date)
        )
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Player_Stat", member_id,
                   metric_name, request.remote_addr, "SUCCESS")
        return jsonify({"message": "Stat deleted"}), 200
    finally:
        db.close()
