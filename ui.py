
from flask import Flask, render_template_string
import os
import mysql.connector
from datetime import datetime

app = Flask(__name__)

DB_USER = "root"
DB_PASSWORD = "dbms123"
DB_HOST = "localhost"
DB_NAME = "college_db"
BACKUP_FOLDER = "backup"

os.makedirs(BACKUP_FOLDER, exist_ok=True)


def create_backup():
    try:
        con = mysql.connector.connect(
            host=DB_HOST, user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        cur = con.cursor()

        cur.execute("SHOW TABLES LIKE 'students'")
        if cur.fetchone() is None:
            cur.execute("""
                CREATE TABLE students (
                    id INT PRIMARY KEY,
                    name VARCHAR(100),
                    course VARCHAR(50),
                    fees INT
                )
            """)
            con.commit()

        cur.execute("SELECT COUNT(*) FROM students")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO students VALUES (1,'DISHA','IT',25000)"
            )
            con.commit()

        cur.execute("SELECT * FROM students ORDER BY id")
        rows = cur.fetchall()

        path = os.path.join(
            BACKUP_FOLDER,
            "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".sql"
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    course VARCHAR(50),
    fees INT
);
""")
            for row in rows:
                values = [
                    "NULL" if v is None else
                    "'" + v.replace("'", "''") + "'" if isinstance(v, str)
                    else str(v)
                    for v in row
                ]
                f.write(
                    "INSERT INTO students VALUES ("
                    + ", ".join(values) + ");\n"
                )

            f.write("COMMIT;\n")

        cur.close()
        con.close()
        return f"Backup successful! Records: {len(rows)}. File: {path}"

    except Exception as e:
        return f"Backup failed: {e}"


PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Database Backup Utility</title>
<style>
body {font-family:Arial;background:#eef2f7;text-align:center;padding:70px 15px}
.box {background:white;max-width:600px;margin:auto;padding:35px;border-radius:15px}
h1 {color:#243b64}
.author {color:#2457d6;font-weight:bold}
button {background:#2457d6;color:white;padding:14px 25px;border:0;border-radius:8px;cursor:pointer}
.msg {margin-top:25px;padding:15px;background:#e9f7ef;overflow-wrap:anywhere}
</style>
</head>
<body>
<div class="box">
<h1>Database Backup Utility</h1>
<p class="author">Developed by: YOUR NAME</p>
<p>Python + MySQL Database Backup System</p>
<p>Create a backup of your students table.</p>
<form method="POST" action="/backup">
<button type="submit">Create Backup</button>
</form>
{% if message %}<div class="msg">{{ message }}</div>{% endif %}
</div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/backup", methods=["POST"])
def backup():
    return render_template_string(PAGE, message=create_backup())


if __name__ == "__main__":
    app.run(debug=True)
