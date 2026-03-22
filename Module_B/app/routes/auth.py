from flask import Blueprint, request, jsonify
from auth_utils import (hash_password, create_session, validate_session,
                        invalidate_session, get_token_from_request)
from audit import log_action
from db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json(silent=True) or {}
    username = data.get("user", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        log_action(username or None, None, None, "LOGIN", None, None,
                   "Missing parameters", request.remote_addr, "FAILURE")
        return jsonify({"error": "Missing parameters"}), 401

    db   = get_db()
    user = db.execute(
        "SELECT * FROM UserLogin WHERE Username = ? AND Is_Active = 1", (username,)
    ).fetchone()
    db.close()

    if not user or user["Password_Hash"] != hash_password(password):
        log_action(username, None, None, "LOGIN", None, None,
                   "Invalid credentials", request.remote_addr, "FAILURE")
        return jsonify({"error": "Invalid credentials"}), 401

    # create_session now needs extra args to embed in JWT payload
    token = create_session(
        user_id   = user["User_ID"],
        username  = username,
        member_id = user["Member_ID"],
        role      = user["Role"],
    )

    log_action(username, user["Member_ID"], user["Role"], "LOGIN",
               "JWT", None, "Login successful", request.remote_addr, "SUCCESS")

    return jsonify({
        "message":       "Login successful",
        "session_token": token,          # this is now a real JWT string
        "username":      username,
        "member_id":     user["Member_ID"],
        "role":          user["Role"],
    }), 200


@auth_bp.route("/isAuth", methods=["GET"])
def is_auth():
    token        = get_token_from_request()
    user, error  = validate_session(token)
    if error:
        return jsonify({"error": error}), 401

    # JWT payload uses lowercase keys (set in create_session)
    import datetime
    expiry = datetime.datetime.utcfromtimestamp(user["exp"]).strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "message":   "User is authenticated",
        "username":  user["username"],
        "member_id": user["member_id"],
        "role":      user["role"],
        "expiry":    expiry,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    token       = get_token_from_request()
    user, _     = validate_session(token)
    if token:
        invalidate_session(token)      # adds to RevokedToken blocklist
    if user:
        log_action(user["username"], user["member_id"], user["role"], "LOGOUT",
                   "JWT", None, "Logged out", request.remote_addr, "SUCCESS")
    return jsonify({"message": "Logged out successfully"}), 200
