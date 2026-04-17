from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

players_bp = Blueprint("players", __name__, url_prefix="/players")

@players_bp.route("/", methods=["GET"])
@login_required
def list_players():
    db = get_db()
    rows = db.execute(
        """SELECT p.Member_ID, p.Roll_No, p.Height, p.Weight, p.Blood_Group,
                  m.Name, m.Gender, m.Age, m.Email
           FROM Player p JOIN Member m ON p.Member_ID=m.Member_ID"""
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@players_bp.route("/", methods=["POST"])
@admin_required
def create_player():
    data = request.get_json(silent=True) or {}
    for f in ["Member_ID", "Roll_No"]:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Player (Member_ID,Roll_No,Height,Weight,Blood_Group) VALUES (?,?,?,?,?)",
            (data["Member_ID"], data["Roll_No"],
             data.get("Height"), data.get("Weight"), data.get("Blood_Group"))
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "CREATE", "Player", data["Member_ID"], "", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Player created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@players_bp.route("/<member_id>", methods=["DELETE"])
@admin_required
def delete_player(member_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM Player WHERE Member_ID=?", (member_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Player", member_id, "", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Player deleted"}), 200
    finally:
        db.close()
