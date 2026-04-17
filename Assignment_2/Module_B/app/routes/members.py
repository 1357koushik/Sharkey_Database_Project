from flask import Blueprint, request, jsonify
from auth_utils import login_required, admin_required
from audit import log_action
from db import get_db

members_bp = Blueprint("members", __name__, url_prefix="/members")

@members_bp.route("/", methods=["GET"])
@login_required
def list_members():
    db = get_db()
    user = request.current_user
    if user["role"] == "admin":
        rows = db.execute(
            "SELECT Member_ID,Name,Gender,Email,Phone_Number,Age,DOB FROM Member"
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT Member_ID,Name,Gender,Email,Age FROM Member"
        ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows]), 200

@members_bp.route("/<member_id>", methods=["GET"])
@login_required
def get_member(member_id):
    db = get_db()
    user = request.current_user
    row = db.execute(
        "SELECT Member_ID,Name,Gender,Email,Phone_Number,Age,DOB FROM Member WHERE Member_ID=?",
        (member_id,)
    ).fetchone()
    db.close()
    if not row:
        return jsonify({"error": "Member not found"}), 404
    data = dict(row)
    if user["role"] != "admin" and user["member_id"] != member_id:
        data.pop("Phone_Number", None)
    return jsonify(data), 200

@members_bp.route("/portfolio/<member_id>", methods=["GET"])
@login_required
def portfolio(member_id):
    user = request.current_user
    if user["role"] != "admin" and user["member_id"] != member_id:
        log_action(user["username"], user["member_id"], user["role"],
                   "PORTFOLIO_VIEW", "Member", member_id,
                   "Unauthorized portfolio access", request.remote_addr, "UNAUTHORIZED")
        return jsonify({"error": "You can only view your own portfolio"}), 403

    db = get_db()
    member = db.execute(
        "SELECT Member_ID,Name,Gender,Email,Phone_Number,Age,DOB FROM Member WHERE Member_ID=?",
        (member_id,)
    ).fetchone()
    if not member:
        db.close()
        return jsonify({"error": "Member not found"}), 404

    player = db.execute(
        "SELECT Member_ID,Roll_No,Height,Weight,Blood_Group FROM Player WHERE Member_ID=?",
        (member_id,)
    ).fetchone()
    coach = db.execute(
        """SELECT c.Coach_ID, c.Years_Experience, c.Salary, c.Joining_Date, s.Sport_Name
           FROM Coach c JOIN Sport s ON c.Sport_ID=s.Sport_ID WHERE c.Member_ID=?""",
        (member_id,)
    ).fetchone()
    admin = db.execute(
        "SELECT Admin_Level,Department,Office_Location FROM Administrator WHERE Member_ID=?",
        (member_id,)
    ).fetchone()

    stats = []
    loans = []
    teams = []
    attendance = []
    bookings = []
    complaints = []

    if player:
        stats = [dict(r) for r in db.execute(
            "SELECT Metric_Name,Metric_Value,Recorded_Date,Event_ID FROM Player_Stat WHERE Member_ID=? ORDER BY Recorded_Date DESC",
            (member_id,)
        ).fetchall()]
        teams = [dict(r) for r in db.execute(
            """SELECT t.Team_Name, t.Category, s.Sport_Name
               FROM Team_Roster tr
               JOIN Player p ON tr.Roll_No=p.Roll_No
               JOIN Team t ON tr.Team_ID=t.Team_ID
               JOIN Sport s ON t.Sport_ID=s.Sport_ID
               WHERE p.Member_ID=?""",
            (member_id,)
        ).fetchall()]
        attendance = [dict(r) for r in db.execute(
            "SELECT Session,Date,Status FROM Attendance WHERE Member_ID=? ORDER BY Date DESC",
            (member_id,)
        ).fetchall()]

    loans = [dict(r) for r in db.execute(
        """SELECT e.Equipment_Name, el.Quantity, el.Issue_Time, el.Return_Time
           FROM Equipment_Loan el JOIN Equipment e ON el.Equipment_ID=e.Equipment_ID
           WHERE el.Member_ID=? ORDER BY el.Issue_Time DESC""",
        (member_id,)
    ).fetchall()]
    bookings = [dict(r) for r in db.execute(
        """SELECT f.Facility_Name, b.Time_In, b.Time_Out
           FROM Booking b JOIN Facility f ON b.Facility_ID=f.Facility_ID
           WHERE b.Member_ID=? ORDER BY b.Time_In DESC""",
        (member_id,)
    ).fetchall()]
    complaints = [dict(r) for r in db.execute(
        "SELECT Complaint_ID,Description,Status,Date_Filed FROM Complaint WHERE Raised_By=?",
        (member_id,)
    ).fetchall()]

    db.close()
    log_action(user["username"], user["member_id"], user["role"],
               "PORTFOLIO_VIEW", "Member", member_id,
               "Portfolio accessed", request.remote_addr, "SUCCESS")
    return jsonify({
        "member":             dict(member),
        "role_type":          "admin" if admin else ("coach" if coach else "player"),
        "player_info":        dict(player) if player else None,
        "coach_info":         dict(coach)  if coach  else None,
        "admin_info":         dict(admin)  if admin  else None,
        "teams":              teams,
        "stats":              stats,
        "attendance":         attendance,
        "equipment_loans":    loans,
        "facility_bookings":  bookings,
        "complaints":         complaints
    }), 200

@members_bp.route("/", methods=["POST"])
@admin_required
def create_member():
    data = request.get_json(silent=True) or {}
    required = ["Member_ID", "Name", "Gender", "Email", "Age"]
    for f in required:
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Member (Member_ID,Name,Gender,Email,Phone_Number,Age,DOB) VALUES (?,?,?,?,?,?,?)",
            (data["Member_ID"], data["Name"], data["Gender"], data["Email"],
             data.get("Phone_Number"), data["Age"], data.get("DOB"))
        )
        db.commit()
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "CREATE", "Member", data["Member_ID"],
                   f"Created member {data['Name']}", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Member created", "Member_ID": data["Member_ID"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@members_bp.route("/<member_id>", methods=["PUT"])
@login_required
def update_member(member_id):
    user = request.current_user
    if user["role"] != "admin" and user["member_id"] != member_id:
        log_action(user["username"], user["member_id"], user["role"],
                   "UPDATE", "Member", member_id,
                   "Unauthorized update attempt", request.remote_addr, "UNAUTHORIZED")
        return jsonify({"error": "You can only update your own profile"}), 403

    data = request.get_json(silent=True) or {}
    allowed = ["Name", "Email", "Phone_Number", "Age", "DOB"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    db = get_db()
    try:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        db.execute(f"UPDATE Member SET {set_clause} WHERE Member_ID=?",
                   list(updates.values()) + [member_id])
        db.commit()
        log_action(user["username"], user["member_id"], user["role"],
                   "UPDATE", "Member", member_id,
                   f"Updated fields: {list(updates.keys())}", request.remote_addr, "SUCCESS")
        return jsonify({"message": "Member updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@members_bp.route("/<member_id>", methods=["DELETE"])
@admin_required
def delete_member(member_id):
    db = get_db()
    try:
        result = db.execute("DELETE FROM Member WHERE Member_ID=?", (member_id,))
        db.commit()
        if result.rowcount == 0:
            return jsonify({"error": "Member not found"}), 404
        log_action(request.current_user["username"], request.current_user["member_id"],
                   "admin", "DELETE", "Member", member_id,
                   "Member deleted (cascade)", request.remote_addr, "SUCCESS")
        return jsonify({"message": f"Member {member_id} deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()
