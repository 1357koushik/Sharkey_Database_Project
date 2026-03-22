from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

bookings_bp = Blueprint("bookings", __name__, url_prefix="/bookings")

@bookings_bp.route("/", methods=["GET"])
@login_required
def list_bookings():
    db = get_db()
    user = request.current_user
    if user["role"] == "admin":
        rows = db.execute(
            """SELECT b.Booking_ID, b.Member_ID, m.Name, f.Facility_Name, b.Time_In, b.Time_Out
               FROM Booking b JOIN Member m ON b.Member_ID=m.Member_ID
               JOIN Facility f ON b.Facility_ID=f.Facility_ID ORDER BY b.Time_In DESC"""
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT b.Booking_ID, b.Member_ID, f.Facility_Name, b.Time_In, b.Time_Out
               FROM Booking b JOIN Facility f ON b.Facility_ID=f.Facility_ID
               WHERE b.Member_ID=? ORDER BY b.Time_In DESC""",
            (user["member_id"],)
        ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@bookings_bp.route("/", methods=["POST"])
@login_required
def create_booking():
    data = request.get_json(silent=True) or {}
    user = request.current_user
    member_id = data.get("Member_ID", user["member_id"])
    if user["role"] != "admin" and member_id != user["member_id"]:
        return jsonify({"error": "Cannot book for other members"}), 403
    required = ["Facility_ID", "Time_In"]
    for f in required:
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Booking (Facility_ID, Member_ID, Time_In, Time_Out) VALUES (?,?,?,?)",
            (data["Facility_ID"], member_id, data["Time_In"], data.get("Time_Out"))
        )
        db.commit()
        log_action(user["username"], user["member_id"], user["role"],
                   "CREATE", "Booking", None, f"Booked facility {data['Facility_ID']}",
                   request.remote_addr, "SUCCESS")
        return jsonify({"message": "Booking created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@bookings_bp.route("/<int:booking_id>", methods=["PUT"])
@login_required
def update_booking(booking_id):
    user = request.current_user
    db = get_db()
    booking = db.execute("SELECT * FROM Booking WHERE Booking_ID=?", (booking_id,)).fetchone()
    if not booking:
        db.close()
        return jsonify({"error": "Booking not found"}), 404
    if user["role"] != "admin" and booking["Member_ID"] != user["member_id"]:
        db.close()
        return jsonify({"error": "Cannot modify others' bookings"}), 403
    data = request.get_json(silent=True) or {}
    try:
        db.execute("UPDATE Booking SET Time_Out=? WHERE Booking_ID=?",
                   (data.get("Time_Out"), booking_id))
        db.commit()
        log_action(user["username"], user["member_id"], user["role"],
                   "UPDATE", "Booking", str(booking_id), "Updated booking",
                   request.remote_addr, "SUCCESS")
        return jsonify({"message": "Booking updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@bookings_bp.route("/<int:booking_id>", methods=["DELETE"])
@login_required
def delete_booking(booking_id):
    user = request.current_user
    db = get_db()
    booking = db.execute("SELECT * FROM Booking WHERE Booking_ID=?", (booking_id,)).fetchone()
    if not booking:
        db.close()
        return jsonify({"error": "Booking not found"}), 404
    if user["role"] != "admin" and booking["Member_ID"] != user["member_id"]:
        db.close()
        return jsonify({"error": "Cannot delete others' bookings"}), 403
    try:
        db.execute("DELETE FROM Booking WHERE Booking_ID=?", (booking_id,))
        db.commit()
        log_action(user["username"], user["member_id"], user["role"],
                   "DELETE", "Booking", str(booking_id), "Deleted booking",
                   request.remote_addr, "SUCCESS")
        return jsonify({"message": "Booking deleted"}), 200
    finally:
        db.close()
