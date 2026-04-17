from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

complaints_bp = Blueprint("complaints", __name__, url_prefix="/complaints")

@complaints_bp.route("/", methods=["GET"])
@login_required
def list_complaints():
    db = get_db()
    user = request.current_user
    if user["role"] == "admin":
        rows = db.execute(
            """SELECT c.*, m.Name as Raised_By_Name
               FROM Complaint c JOIN Member m ON c.Raised_By=m.Member_ID"""
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM Complaint WHERE Raised_By=?", (user["member_id"],)
        ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@complaints_bp.route("/", methods=["POST"])
@login_required
def create_complaint():
    data = request.get_json(silent=True) or {}
    user = request.current_user
    for f in ["Complaint_ID", "Description"]:
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Complaint (Complaint_ID,Raised_By,Description,Status) VALUES (?,?,?,?)",
            (data["Complaint_ID"], user["member_id"], data["Description"], "Open")
        )
        db.commit()
        log_action(user["username"], user["member_id"], user["role"],
                   "CREATE", "Complaint", data["Complaint_ID"],
                   data["Description"][:80], request.remote_addr, "SUCCESS")
        return jsonify({"message": "Complaint filed"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@complaints_bp.route("/<complaint_id>", methods=["PUT"])
@admin_required
def resolve_complaint(complaint_id):
    user = request.current_user
    db = get_db()
    try:
        db.execute(
            "UPDATE Complaint SET Status='Resolved', Resolved_By=? WHERE Complaint_ID=?",
            (user["member_id"], complaint_id)
        )
        db.commit()
        log_action(user["username"], user["member_id"], user["role"],
                   "UPDATE", "Complaint", complaint_id,
                   "Marked resolved", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Complaint resolved"}), 200
    finally:
        db.close()

@complaints_bp.route("/<complaint_id>", methods=["DELETE"])
@admin_required
def delete_complaint(complaint_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM Complaint WHERE Complaint_ID=?", (complaint_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Complaint", complaint_id,
                   "Deleted", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Deleted"}), 200
    finally:
        db.close()
