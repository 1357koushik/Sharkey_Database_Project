from flask import render_template, send_from_directory
from app import app
import os

@app.route("/ui")
@app.route("/ui/")
def ui():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), "static"),
        filename
    )
