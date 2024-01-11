from flask import Flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import templates

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def auth_app():
    return app


@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

# @app.route("/login", methods=["POST"])
# def login():
#     if not request.is_json:
#         return jsonify({"error": "Invalid request format"}), 400

#     data = request.get_json()
#     if not data or not "username" in data or not "password" in data:
#         return jsonify({"error": "Missing required field"}), 400

#     user = User.query.filter_by(username=data["username"]).first()
#     if user and user.check_password(data["password"]):
#         token = generate_token(user)
#         return jsonify({"token": token}), 200

#     return jsonify({"error": "Invalid username or password"}), 401
