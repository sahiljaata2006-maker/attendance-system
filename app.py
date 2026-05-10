# ============================================
# SMART ATTENDANCE MANAGEMENT SYSTEM
# SAVE FILE NAME = app.py
# ============================================

from flask import Flask, render_template_string, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "attendance_secret"

# ============================================
# DATABASE
# ============================================

def connect_db():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn


conn = connect_db()
cur = conn.cursor()

# TIMETABLE TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    reg_number TEXT,
    subject TEXT,
    date TEXT,
    month TEXT,
    year TEXT,
    status TEXT
)
""")

# ATTENDANCE TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    date TEXT,
    month TEXT,
    year TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

# ============================================
# LOGIN PAGE
# ============================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        name = request.form["name"]
        reg = request.form["reg"]

        session["name"] = name
        session["reg"] = reg

        return redirect("/")

    return render_template_string("""

<!DOCTYPE html>
<html>

<head>

<title>Student Login</title>

<style>

body{
    background:#0f172a;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    font-family:Arial;
}

.box{
    background:#1e293b;
    padding:40px;
    border-radius:20px;
    width:320px;
    color:white;
}

input{
    width:100%;
    padding:12px;
    margin-top:15px;
    border:none;
    border-radius:10px;
}

button{
    width:100%;
    padding:12px;
    margin-top:20px;
    border:none;
    border-radius:10px;
    background:#3b82f6;
    color:white;
    font-size:18px;
}

</style>

</head>

<body>

<div class="box">

<h1>Student Login</h1>

<form method="POST">

<input
type="text"
name="name"
placeholder="Enter Your Name"
required>

<input
type="text"
name="reg"
placeholder="Registration Number"
required>

<button type="submit">
Login
</button>

</form>

</div>

</body>

</html>

""")


# ============================================
# HOME PAGE
# ============================================

@app.route("/")
def home():

    if "name" not in session:
        return redirect("/login")

    return render_template_string("""

<!DOCTYPE html>
<html>

<head>

<title>Dashboard</title>

<style>

body{
    background:#0f172a;
    color:white;
    font-family:Arial;
    padding:20px;
}

.card{
    background:#1e293b;
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
}

button{
    width:100%;
    padding:20px;
    margin-top:20px;
    border:none;
    border-radius:15px;
    background:#3b82f6;
    color:white;
    font-size:20px;
}

a{
    text-decoration:none;
}

</style>

</head>

<body>

<div class="card">

<h1>Welcome {{name}}</h1>

<h3>Registration Number : {{reg}}</h3>

</div>

<a href="/timetable">
<button>📅 Weekly Timetable</button>
</a>

<a href="/attendance">
<button>📊 Attendance Sheet</button>
</a>

<a href="/summary">
<button>📈 Monthly Summary</button>
</a>

</body>

</html>

""", name=session["name"], reg=session["reg"])


# ============================================
# TIMETABLE PAGE
# ============================================

@app.route("/timetable", methods=["GET", "POST"])
def timetable():

    conn = connect_db()
    cur = conn.cursor()

    if request.method == "POST":

        day = request.form["day"]
        subject = request.form["subject"]
        time = request.form["time"]

        cur.execute("""
        INSERT INTO timetable(day,subject,time)
        VALUES(?,?,?)
        """, (day, subject, time))

        conn.commit()

    cur.execute("SELECT * FROM timetable")
    data = cur.fetchall()

    conn.close()

    return render_template_string("""

<!DOCTYPE html>
<html>

<head>

<title>Timetable</title>

<style>

body{
    background:#0f172a;
    color:white;
    font-family:Arial;
    padding:20px;
}

form{
    background:#1e293b;
    padding:20px;
    border-radius:20px;
}

input,select{
    padding:10px;
    margin:10px;
    border:none;
    border-radius:10px;
}

button{
    padding:10px 20px;
    border:none;
    border-radius:10px;
    background:#3b82f6;
    color:white;
}

table{
    width:100%;
    margin-top:20px;
    border-collapse:collapse;
    background:white;
    color:black;
}

th,td{
    border:1px solid black;
    padding:10px;
    text-align:center;
}

th{
    background:#3b82f6;
    color:white;
}

</style>

</head>

<body>

<h1>Weekly Timetable</h1>

<form method="POST">

<select name="day">

<option>Monday</option>
<option>Tuesday</option>
<option>Wednesday</option>
<option>Thursday</option>
<option>Friday</option>
<option>Saturday</option>

</select>

<input type="text"
name="subject"
placeholder="Subject Name"
required>

<input type="text"
name="time"
placeholder="Class Time"
required>

<button type="submit">
Add Class
</button>

</form>

<table>

<tr>
<th>Day</th>
<th>Subject</th>
<th>Time</th>
</tr>

{% for row in data %}

<tr>

<td>{{row['day']}}</td>
<td>{{row['subject']}}</td>
<td>{{row['time']}}</td>

</tr>

{% endfor %}

</table>

<br>

<a href="/">
<button>Back</button>
</a>

</body>

</html>

""", data=data)


# ============================================
# ATTENDANCE PAGE
# ============================================

@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    conn = connect_db()
    cur = conn.cursor()

    subjects = []
    selected_date = ""

    if request.method == "POST":

        # LOAD SUBJECTS BY DATE
        if "load_classes" in request.form:

            selected_date = request.form["date"]

            dt = datetime.strptime(selected_date, "%Y-%m-%d")

            day_name = dt.strftime("%A")

            cur.execute("""
            SELECT * FROM timetable
            WHERE day=?
            """, (day_name,))

            subjects = cur.fetchall()

        # SAVE ATTENDANCE
        elif "save_attendance" in request.form:

            date = request.form["date"]
            month = date[:7]
            year = date[:4]

            subject_list = request.form.getlist("subject")
            status_list = request.form.getlist("status")

            for i in range(len(subject_list)):

                cur.execute("""
INSERT INTO attendance(
student_name,
reg_number,
subject,
date,
month,
year,
status
)
VALUES(?,?,?,?,?,?,?)
                """, (
session["name"],
session["reg"],
subject_list[i],
date,
month,
year,
status_list[i]
))

            conn.commit()

            return redirect("/summary")

    return render_template_string("""

<!DOCTYPE html>
<html>

<head>

<title>Attendance Sheet</title>

<style>

body{
    background:#0f172a;
    color:white;
    font-family:Arial;
    padding:20px;
}

.card{
    background:#1e293b;
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
}

input,select{
    padding:10px;
    margin:10px;
    border:none;
    border-radius:10px;
}

button{
    padding:10px 20px;
    border:none;
    border-radius:10px;
    background:#3b82f6;
    color:white;
}

table{
    width:100%;
    border-collapse:collapse;
    background:white;
    color:black;
}

th,td{
    border:1px solid black;
    padding:10px;
    text-align:center;
}

th{
    background:#3b82f6;
    color:white;
}

</style>

</head>

<body>

<h1>Attendance Sheet</h1>

<div class="card">

<form method="POST">

<input type="date" name="date" required>

<button type="submit" name="load_classes">
Load Classes
</button>

</form>

</div>

{% if subjects %}

<div class="card">

<h2>Today's Classes</h2>

<form method="POST">

<input type="hidden"
name="date"
value="{{selected_date}}">

<table>

<tr>
<th>Date</th>
<th>Subject</th>
<th>Status</th>
</tr>

{% for row in subjects %}

<tr>

<td>{{selected_date}}</td>

<td>

{{row['subject']}}

<input
type="hidden"
name="subject"
value="{{row['subject']}}">

</td>

<td>

<select name="status">

<option value="P">
Present
</option>

<option value="A">
Absent
</option>

<option value="S">
Shifted
</option>

</select>

</td>

</tr>

{% endfor %}

</table>

<br>

<button type="submit"
name="save_attendance">

Save Attendance

</button>

</form>

</div>

{% endif %}

<a href="/">
<button>Back</button>
</a>

</body>

</html>

""", subjects=subjects,
selected_date=selected_date)


# ============================================
# MONTHLY SUMMARY
# ============================================

@app.route("/summary", methods=["GET", "POST"])
def summary():

    conn = connect_db()
    cur = conn.cursor()

    data = []

    if request.method == "POST":

        month = request.form["month"]

        cur.execute("""

        SELECT
        subject,
        COUNT(*) as total,
        SUM(CASE WHEN status='P' THEN 1 ELSE 0 END) as present,
        SUM(CASE WHEN status='A' THEN 1 ELSE 0 END) as absent,
        SUM(CASE WHEN status='S' THEN 1 ELSE 0 END) as shifted

        FROM attendance

WHERE month=?
AND reg_number=?

GROUP BY subject

""", (month, session["reg"]))

        data = cur.fetchall()

    return render_template_string("""

<!DOCTYPE html>
<html>

<head>

<title>Monthly Summary</title>

<style>

body{
    background:#0f172a;
    color:white;
    font-family:Arial;
    padding:20px;
}

.card{
    background:#1e293b;
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
}

input{
    padding:10px;
    border:none;
    border-radius:10px;
}

button{
    padding:10px 20px;
    border:none;
    border-radius:10px;
    background:#3b82f6;
    color:white;
}

table{
    width:100%;
    border-collapse:collapse;
    background:white;
    color:black;
}

th,td{
    border:1px solid black;
    padding:10px;
    text-align:center;
}

th{
    background:#3b82f6;
    color:white;
}

</style>

</head>

<body>

<h1>Monthly Summary</h1>

<div class="card">

<form method="POST">

<input type="month"
name="month"
required>

<button type="submit">
Load Summary
</button>

</form>

</div>

{% if data %}

<table>

<tr>
<th>Subject</th>
<th>Total</th>
<th>Present</th>
<th>Absent</th>
<th>Shifted</th>
<th>Percentage</th>
</tr>

{% for row in data %}

<tr>

<td>{{row['subject']}}</td>

<td>{{row['total']}}</td>

<td>{{row['present']}}</td>

<td>{{row['absent']}}</td>

<td>{{row['shifted']}}</td>

<td>

{{ ((row['present']/row['total'])*100)|round(2) }}%

</td>

</tr>

{% endfor %}

</table>

{% endif %}

<br>

<a href="/">
<button>Back</button>
</a>

</body>

</html>

""", data=data)


# ============================================
# LOGOUT
# ============================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ============================================
# RUN APP
# ============================================

if __name__ == "__main__":
 import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)