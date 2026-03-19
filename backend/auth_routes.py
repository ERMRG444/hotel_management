from flask import Blueprint, request, jsonify
from database import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json
    username = data["username"]
    password = data["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cur.fetchone()

    if user:
        return jsonify({"message":"login success"})
    else:
        return jsonify({"message":"invalid credentials"}),401
