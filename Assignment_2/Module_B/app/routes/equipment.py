from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")

@equipment_bp.route("/", methods=["GET"])
@login_required
def list_equipment():
    db = get_db()
    rows = db.execute(
        "SELECT e.*, s.Sport_Name FROM Equipment e JOIN Sport s ON e.Sport_ID=s.Sport_ID"
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@equipment_bp.route("/loans", methods=["GET"])
@login_required
def list_loans():
    db = get_db()
    user = request.current_user
    if user["role"] == "admin":
        rows = db.execute(
            """SELECT el.*, m.Name, e.Equipment_Name FROM Equipment_Loan el
               JOIN Member m ON el.Member_ID=m.Member_ID
               JOIN Equipment e ON el.Equipment_ID=e.Equipment_ID
               ORDER BY el.Issue_Time DESC"""
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT el.*, e.Equipment_Name FROM Equipment_Loan el
               JOIN Equipment e ON el.Equipment_ID=e.Equipment_ID
               WHERE el.Member_ID=? ORDER BY el.Issue_Time DESC""",
            (user["member_id"],)
        ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@equipment_bp.route("/loans", methods=["POST"])
@login_required
def create_loan():
    data = request.get_json(silent=True) or {}
    user = request.current_user
    member_id = data.get("Member_ID", user["member_id"])
    if user["role"] != "admin" and member_id != user["member_id"]:
        return jsonify({"error": "Cannot issue loan for other members"}), 403
    for f in ["Equipment_ID", "Quantity", "Issue_Time"]:
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Equipment_Loan (Member_ID,Equipment_ID,Quantity,Issue_Time) VALUES (?,?,?,?)",
            (member_id, data["Equipment_ID"], data["Quantity"], data["Issue_Time"])
        )
        db.commit()
        log_action(user["username"], user["member_id"], user["role"],
                   "CREATE", "Equipment_Loan", data["Equipment_ID"],
                   f"Loan qty={data['Quantity']}", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Loan created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@equipment_bp.route("/<equipment_id>", methods=["PUT"])
@admin_required
def update_equipment(equipment_id):
    data = request.get_json(silent=True) or {}
    allowed = ["Equipment_Name", "Total_Qty", "Status"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields"}), 400
    db = get_db()
    try:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        db.execute(f"UPDATE Equipment SET {set_clause} WHERE Equipment_ID=?",
                   list(updates.values()) + [equipment_id])
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "UPDATE", "Equipment", equipment_id,
                   str(updates), request.remote_addr, "SUCCESS")
        return jsonify({"message": "Equipment updated"}), 200
    finally:
        db.close()

@equipment_bp.route("/<equipment_id>", methods=["DELETE"])
@admin_required
def delete_equipment(equipment_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM Equipment WHERE Equipment_ID=?", (equipment_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Equipment", equipment_id,
                   "Deleted", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Deleted"}), 200
    finally:
        db.close()
