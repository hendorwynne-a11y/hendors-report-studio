from flask import Flask, request, jsonify, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from datetime import datetime
import sqlite3, os

APP_DIR = Path(__file__).parent.resolve()
DB_PATH = APP_DIR / "hendors.db"

app = Flask(__name__)
app.secret_key = "super-secret-key"

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )
    """)

    cur.execute("SELECT COUNT(*) as c FROM users")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
            ("admin", generate_password_hash("admin123"), "admin")
        )

    con.commit()
    con.close()

@app.route("/")
def home():
    return send_from_directory(APP_DIR / "static", "index.html")

# 🔐 LOGIN
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username","").lower()
    password = data.get("password","")

    con = db()
    user = con.execute(
        "SELECT * FROM users WHERE lower(username)=?",
        (username,)
    ).fetchone()
    con.close()

    if user and check_password_hash(user["password_hash"], password):
        session["user"] = {"username": user["username"], "role": user["role"]}
        return jsonify(ok=True)

    return jsonify(ok=False), 401

# 🔐 CHANGE PASSWORD
@app.route("/api/change-password", methods=["POST"])
def change_password():
    if "user" not in session:
        return jsonify(error="Login required"), 401

    data = request.json
    new_password = data.get("new_password")

    con = db()
    con.execute(
        "UPDATE users SET password_hash=? WHERE username=?",
        (generate_password_hash(new_password), session["user"]["username"])
    )
    con.commit()
    con.close()

    return jsonify(ok=True)

# 👤 ADMIN: CREATE USER
@app.route("/api/create-user", methods=["POST"])
def create_user():
    if session.get("user", {}).get("role") != "admin":
        return jsonify(error="Admin only"), 403

    data = request.json

    con = db()
    con.execute(
        "INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
        (
            data["username"],
            generate_password_hash(data["password"]),
            data["role"]
        )
    )
    con.commit()
    con.close()

    return jsonify(ok=True)

# 👤 ADMIN: LIST USERS
@app.route("/api/users")
def users():
    if session.get("user", {}).get("role") != "admin":
        return jsonify(error="Admin only"), 403

    con = db()
    rows = con.execute("SELECT username,role FROM users").fetchall()
    con.close()

    return jsonify([dict(r) for r in rows])

# 🚀 QUICK SETUP
@app.route("/api/admin-setup")
def admin_setup():
    con = db()

    for u,p,r in [
        ("admin","admin123","admin"),
        ("sono","Sono123!","sonographer"),
        ("rec","Rec123!","reception")
    ]:
        try:
            con.execute(
                "INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                (u, generate_password_hash(p), r)
            )
        except:
            pass

    con.commit()
    con.close()

    return jsonify(ok=True)

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=1420)
