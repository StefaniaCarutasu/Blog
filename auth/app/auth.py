@app.route("/register", methods=["GET", "POST"])
def register():
    return ("")

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