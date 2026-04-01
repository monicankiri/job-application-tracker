from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("jobs.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = get_db()

    search = request.args.get("search")
    status_filter = request.args.get("filter")

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if search:
        query += " AND (company LIKE ? OR role LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    jobs = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("index.html", jobs=jobs)

@app.route("/add", methods=["POST"])
def add_job():
    conn = get_db()
    conn.execute(
        "INSERT INTO jobs (company, role, status) VALUES (?, ?, ?)",
        (request.form["company"], request.form["role"], request.form["status"])
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/update/<int:job_id>", methods=["POST"])
def update_job(job_id):
    conn = get_db()
    conn.execute(
        "UPDATE jobs SET status = ? WHERE id = ?",
        (request.form["status"], job_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    conn = get_db()
    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)