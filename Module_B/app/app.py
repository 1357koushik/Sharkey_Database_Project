from flask import Flask
from routes.auth import auth_bp
from routes.members import members_bp
from routes.players import players_bp
from routes.coaches import coaches_bp
from routes.teams import teams_bp
from routes.facilities import facilities_bp
from routes.bookings import bookings_bp
from routes.equipment import equipment_bp
from routes.events import events_bp
from routes.complaints import complaints_bp
from routes.attendance import attendance_bp
from routes.stats import stats_bp
from routes.admin import admin_bp
from db import init_db, ensure_revoked_token_table
from flask import render_template, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "cs432_sports_club_secret_key_iitgn_2026"

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(members_bp)
app.register_blueprint(players_bp)
app.register_blueprint(coaches_bp)
app.register_blueprint(teams_bp)
app.register_blueprint(facilities_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(equipment_bp)
app.register_blueprint(events_bp)
app.register_blueprint(complaints_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def index():
    return {"message": "Welcome to Sports Club Management APIs — IIT Gandhinagar"}

@app.route("/ui")
@app.route("/ui/")
def ui():
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    ensure_revoked_token_table()
    app.run(debug=True, port=5000)
