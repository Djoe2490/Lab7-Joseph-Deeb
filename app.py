import sqlite3

from flask import Flask, jsonify, request

DATABASE = "users.db"

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
        """
    )
    count = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
    if count == 0:
        connection.executemany(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [("Alice", "alice@example.com"), ("Bob", "bob@example.com")],
        )
    connection.commit()
    connection.close()


def Insert_user(name, email):
    connection = get_db_connection()
    cursor = connection.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)", (name, email)
    )
    connection.commit()
    user_id = cursor.lastrowid
    connection.close()
    return user_id


def Get_users():
    connection = get_db_connection()
    rows = connection.execute("SELECT id, name, email FROM users").fetchall()
    connection.close()
    return [dict(row) for row in rows]


def Get_users_by_id(user_id):
    connection = get_db_connection()
    row = connection.execute(
        "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    connection.close()
    return dict(row) if row else None


def Update_user(user_id, name, email):
    connection = get_db_connection()
    cursor = connection.execute(
        "UPDATE users SET name = ?, email = ? WHERE id = ?",
        (name, email, user_id),
    )
    connection.commit()
    updated = cursor.rowcount
    connection.close()
    return updated > 0


def Delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    deleted = cursor.rowcount
    connection.close()
    return deleted > 0


@app.route("/api/users", methods=["GET"])
def Api_get_user():
    return jsonify(Get_users()), 200


@app.route("/api/users", methods=["POST"])
def Api_add_user():
    data = request.get_json(silent=True)
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "name and email are required"}), 400

    user_id = Insert_user(data["name"], data["email"])
    return jsonify(Get_users_by_id(user_id)), 201


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def Api_update_user(user_id):
    data = request.get_json(silent=True)
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "name and email are required"}), 400

    if not Update_user(user_id, data["name"], data["email"]):
        return jsonify({"error": "User not found"}), 404
    return jsonify(Get_users_by_id(user_id)), 200


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def Api_delete_user(user_id):
    if not Delete_user(user_id):
        return jsonify({"error": "User not found"}), 404
    return jsonify({"deleted": True}), 200


initialize_database()


if __name__ == "__main__":
    app.run(debug=True)
