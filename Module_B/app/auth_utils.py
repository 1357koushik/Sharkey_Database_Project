import hashlib
import datetime
import jwt                          # PyJWT library
from functools import wraps
from flask import request, jsonify
from db import get_db
from audit import log_action

# ─── Config ───────────────────────────────────────────────────────────────────
# In production, load this from an environment variable, never hardcode it.
JWT_SECRET  = "cs432_sports_club_secret_key_iitgn_2026"
JWT_ALGO    = "HS256"
SESSION_DURATION_HOURS = 8


# ─── Password hashing (unchanged) ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ─── JWT creation ─────────────────────────────────────────────────────────────
def create_session(user_id: int, username: str, member_id: int, role: str) -> str:
    """
    Build and sign a JWT.

    Payload (claims) stored INSIDE the token itself:
        sub       – subject (user_id)
        username  – username string
        member_id – member primary key
        role      – 'admin' | 'user' | 'coach'
        iat       – issued-at  (UTC timestamp)
        exp       – expiry     (UTC timestamp, 8 hours from now)

    The token is signed with HMAC-SHA256 using JWT_SECRET.
    No database write is needed — the token IS the session.
    """
    now     = datetime.datetime.utcnow()
    expires = now + datetime.timedelta(hours=SESSION_DURATION_HOURS)

    payload = {
        "sub":       user_id,
        "username":  username,
        "member_id": member_id,
        "role":      role,
        "iat":       now,
        "exp":       expires,
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    # PyJWT >= 2.x returns a str; older versions return bytes — handle both
    return token if isinstance(token, str) else token.decode("utf-8")


# ─── JWT validation ───────────────────────────────────────────────────────────
def validate_session(token: str):
    """
    Returns (payload_dict, error_string).

    How it works:
      1. Decode the token using the same secret → verifies the signature.
      2. PyJWT automatically checks the 'exp' claim and raises ExpiredSignatureError.
      3. No database query at all — completely stateless.

    payload_dict keys: sub, username, member_id, role, iat, exp
    """
    if not token:
        return None, "No session found"

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload, None

    except jwt.ExpiredSignatureError:
        return None, "Session expired"

    except jwt.InvalidTokenError:
        return None, "Invalid session token"


# ─── Logout — blocklist approach ──────────────────────────────────────────────
def invalidate_session(token: str):
    """
    JWTs can't be 'deleted' because they're self-contained.
    We store revoked tokens in the DB until their natural expiry passes.
    validate_session() checks this blocklist before returning success.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        expires = datetime.datetime.utcfromtimestamp(payload["exp"])
    except jwt.InvalidTokenError:
        return  # already invalid, nothing to store

    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO RevokedToken (Token, Expires_At) VALUES (?, ?)",
        (token, expires.strftime("%Y-%m-%d %H:%M:%S"))
    )
    db.commit()
    db.close()


def _is_revoked(token: str) -> bool:
    db = get_db()
    row = db.execute(
        "SELECT 1 FROM RevokedToken WHERE Token = ?", (token,)
    ).fetchone()
    db.close()
    return row is not None


# ─── Override validate_session to check blocklist ─────────────────────────────
_validate_jwt_only = validate_session

def validate_session(token: str):                          # noqa: F811
    payload, error = _validate_jwt_only(token)
    if error:
        return None, error
    if _is_revoked(token):
        return None, "Session expired"
    return payload, None


# ─── Token extraction from request (unchanged interface) ──────────────────────
def get_token_from_request():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    data = request.get_json(silent=True) or {}
    if "session_token" in data:
        return data["session_token"]
    return request.args.get("session_token", "")


# ─── Decorators (same interface as before) ────────────────────────────────────
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_from_request()
        user, error = validate_session(token)
        if error:
            log_action(None, None, None, "AUTH_CHECK", None, None,
                       error, request.remote_addr, "FAILURE")
            return jsonify({"error": error}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_from_request()
        user, error = validate_session(token)
        if error:
            log_action(None, None, None, "AUTH_CHECK", None, None,
                       error, request.remote_addr, "FAILURE")
            return jsonify({" error": error}), 401
        if user["role"] != "admin":
            log_action(user["username"], user["member_id"], user["role"],
                       "ADMIN_ACCESS_DENIED", None, None,
                       "Insufficient privileges", request.remote_addr, "UNAUTHORIZED")
            return jsonify({"error": "Admin privileges required"}), 403
        request.current_user = user
        return f(*args, **kwargs)
    return wrapper
