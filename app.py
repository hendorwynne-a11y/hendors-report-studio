
from flask import Flask, request, jsonify, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from datetime import datetime
import sqlite3, os

APP_DIR = Path(__file__).parent.resolve()
DB_PATH = APP_DIR / "hendors_v14_2_cloud.db"
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT)")
    cur.execute("""CREATE TABLE IF NOT EXISTS cases(
        id INTEGER PRIMARY KEY, created_at TEXT, patient_name TEXT, patient_id_file TEXT, exam_date TEXT,
        age TEXT, gender TEXT, dob TEXT, phone TEXT, email TEXT, perf_physician TEXT, operator TEXT,
        study_title TEXT, referring_doctor TEXT, measurements TEXT, report_body TEXT, comment TEXT,
        impression TEXT, transcript TEXT, prompt TEXT)""")
    cur.execute("CREATE TABLE IF NOT EXISTS doctors(id INTEGER PRIMARY KEY, name TEXT, email TEXT, whatsapp TEXT)")
    for u,p,r in [("admin","admin123","admin"),("sonographer","sono123","sonographer"),("reception","rec123","reception")]:
        cur.execute("INSERT OR REPLACE INTO users(username,password_hash,role) VALUES(?,?,?)",(u,generate_password_hash(p),r))
    cur.execute("SELECT COUNT(*) c FROM doctors")
    if cur.fetchone()["c"] == 0:
        cur.executemany("INSERT INTO doctors(name,email,whatsapp) VALUES(?,?,?)", [
            ("Dr E Kritzinger","kritzingerprak@gmail.com",""),("Dr L Stockigt","drstockigt@gmail.com",""),
            ("Dr Van Der Westhuizen","info@easycare.health",""),("Dr Amanjee","","0671234567"),
            ("Dr P. Van Niekerk","philvniekerk@icloud.com",""),("Dr Barnard","dfbarnard5@gmail.com",""),
            ("Dr L Hugo","",""),("Dr Schmidt","info@easycare.health",""),("Dr Antje Van Dorssen","",""),("Self Referral","","")
        ])
    con.commit(); con.close()

@app.route("/")
def home():
    return send_from_directory(APP_DIR / "static", "index.html")

@app.route("/api/login", methods=["POST"])
def login():
    d=request.json or {}; u=(d.get("username") or "").lower().strip(); p=(d.get("password") or "").strip()
    if {"admin":"admin123","sonographer":"sono123","reception":"rec123"}.get(u)==p:
        session["user"]={"username":u,"role":u}; return jsonify(ok=True)
    con=db(); row=con.execute("SELECT * FROM users WHERE lower(username)=?",(u,)).fetchone(); con.close()
    if row and check_password_hash(row["password_hash"], p):
        session["user"]={"username":row["username"],"role":row["role"]}; return jsonify(ok=True)
    return jsonify(ok=False),401

@app.route("/api/doctors", methods=["GET","POST"])
def doctors():
    con=db()
    if request.method=="POST":
        d=request.json or {}; con.execute("INSERT INTO doctors(name,email,whatsapp) VALUES(?,?,?)",(d.get("name",""),d.get("email",""),d.get("whatsapp",""))); con.commit()
    rows=con.execute("SELECT * FROM doctors ORDER BY id").fetchall(); con.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/cases", methods=["GET","POST"])
def cases():
    con=db()
    if request.method=="POST":
        d=request.json or {}; fields=["patient_name","patient_id_file","exam_date","age","gender","dob","phone","email","perf_physician","operator","study_title","referring_doctor","measurements","report_body","comment","impression","transcript","prompt"]
        con.execute(f"INSERT INTO cases(created_at,{','.join(fields)}) VALUES({','.join(['?']*(len(fields)+1))})",[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]+[d.get(f,"") for f in fields]); con.commit()
    rows=con.execute("SELECT * FROM cases ORDER BY id DESC LIMIT 50").fetchall(); con.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/generate", methods=["POST"])
def generate():
    d=request.json or {}
    imp=d.get("impression","").strip()
    if imp and not imp.startswith("-"):
        imp="\n".join("- "+x.strip(" -•") for x in imp.splitlines() if x.strip())
    report=f"""{d.get('study_title','ULTRASOUND REPORT')}

Clinical history:
{d.get('measurements','')}

Findings:
{d.get('report_body') or d.get('transcript','')}

Comment:
{d.get('comment') or 'The ultrasound findings are described above. Clinical correlation is advised.'}

Impression:
{imp or '- Clinical correlation advised'}
"""
    return jsonify(ok=True, report=report)

@app.route("/health")
def health(): return "ok"

if __name__=="__main__":
    init_db()
    print("Open http://localhost:1420")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",1420)))
