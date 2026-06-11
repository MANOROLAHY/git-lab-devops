from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


# -------------------------
# CREATE USER
# -------------------------
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data["name"]
    email = data["email"]

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;",
        (name, email)
    )

    user_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"id": user_id, "name": name, "email": email})


# -------------------------
# GET ALL USERS
# -------------------------
@app.route("/users", methods=["GET"])
def get_users():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "name": row[1],
            "email": row[2]
        })

    return jsonify(users)


# -------------------------
# GET ONE USER
# -------------------------
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return jsonify({"id": row[0], "name": row[1], "email": row[2]})
    return jsonify({"error": "User not found"}), 404


# -------------------------
# UPDATE USER
# -------------------------
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET name=%s, email=%s WHERE id=%s;",
        (data["name"], data["email"], user_id)
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "User updated"})


# -------------------------
# DELETE USER
# -------------------------
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id=%s;", (user_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "User deleted"})


# -------------------------
# TEST DB
# -------------------------
@app.route("/db")
def db_test():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    conn.close()

    return f"DB OK ✅ {version[0]}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)