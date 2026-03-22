from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

teams_bp = Blueprint("teams", __name__, url_prefix="/teams")

@teams_bp.route("/", methods=["GET"])
@login_required
def list_teams():
    db = get_db()
    rows = db.execute(
        """SELECT t.Team_ID, t.Team_Name, t.Category, s.Sport_Name,
                  m.Name as Coach_Name
           FROM Team t JOIN Sport s ON t.Sport_ID=s.Sport_ID
           JOIN Coach c ON t.Coach_ID=c.Coach_ID
           JOIN Member m ON c.Member_ID=m.Member_ID"""
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@teams_bp.route("/<team_id>/roster", methods=["GET"])
@login_required
def team_roster(team_id):
    db = get_db()
    rows = db.execute(
        """SELECT tr.Roll_No, m.Name, m.Member_ID FROM Team_Roster tr
           JOIN Player p ON tr.Roll_No=p.Roll_No
           JOIN Member m ON p.Member_ID=m.Member_ID
           WHERE tr.Team_ID=?""",
        (team_id,)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@teams_bp.route("/", methods=["POST"])
@admin_required
def create_team():
    data = request.get_json(silent=True) or {}
    for f in ["Team_ID", "Team_Name", "Category", "Sport_ID", "Coach_ID"]:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Team (Team_ID,Team_Name,Category,Sport_ID,Coach_ID) VALUES (?,?,?,?,?)",
            (data["Team_ID"], data["Team_Name"], data["Category"], data["Sport_ID"], data["Coach_ID"])
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "CREATE", "Team", data["Team_ID"], data["Team_Name"], request.remote_addr, "SUCCESS")
        return jsonify({"message": "Team created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@teams_bp.route("/<team_id>", methods=["DELETE"])
@admin_required
def delete_team(team_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM Team WHERE Team_ID=?", (team_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Team", team_id, "", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Team deleted"}), 200
    finally:
        db.close()
