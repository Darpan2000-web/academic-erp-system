from flask import render_template, request, redirect, send_file, flash, session
from db import get_connection
from datetime import date, datetime, timedelta
import pandas as pd
import io


# ===============================
# DELETE ATTENDANCE OLDER THAN 1 YEAR
# ===============================
def cleanup_old_attendance():
    conn = get_connection()
    cur = conn.cursor()

    limit_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

    cur.execute(
        "DELETE FROM attendance WHERE date < ?",
        (limit_date,)
    )

    conn.commit()
    conn.close()


# ===============================
# REGISTER ALL ROUTES
# ===============================
def register_routes(app):

    # ===============================
    # HOME PAGE / DASHBOARD
    # ===============================
    @app.route("/")
    def home():

        if "user" not in session:
            return redirect("/login")

        cleanup_old_attendance()

        conn = get_connection()
        cur = conn.cursor()

        students = cur.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

        total_students = cur.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        total_present = cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE status='Present'"
        ).fetchone()[0]

        conn.close()

        return render_template(
            "index.html",
            students=students,
            total_students=total_students,
            total_present=total_present
        )

    # ===============================
    # ADD STUDENT
    # ===============================
    @app.route("/add", methods=["GET", "POST"])
    def add_student():

        if "user" not in session:
            return redirect("/login")

        if request.method == "POST":

            d = request.form

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO students
                (student_id,name,roll,mobile,email,department,semester,address)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                d["student_id"],
                d["name"],
                d["roll"],
                d["mobile"],
                d["email"],
                d["department"],
                d["semester"],
                d["address"]
            ))

            conn.commit()
            conn.close()

            flash("Student Added Successfully")
            return redirect("/")

        return render_template("add_student.html")

    # ===============================
    # EDIT STUDENT
    # ===============================
    @app.route("/edit/<student_id>", methods=["GET", "POST"])
    def edit_student(student_id):

        if "user" not in session:
            return redirect("/login")

        conn = get_connection()
        cur = conn.cursor()

        if request.method == "POST":

            d = request.form

            cur.execute("""
                UPDATE students
                SET name=?,
                    roll=?,
                    mobile=?,
                    email=?,
                    department=?,
                    semester=?,
                    address=?
                WHERE student_id=?
            """, (
                d["name"],
                d["roll"],
                d["mobile"],
                d["email"],
                d["department"],
                d["semester"],
                d["address"],
                student_id
            ))

            conn.commit()
            conn.close()

            flash("Student Updated Successfully")
            return redirect("/")

        student = cur.execute(
            "SELECT * FROM students WHERE student_id=?",
            (student_id,)
        ).fetchone()

        conn.close()

        return render_template(
            "edit_student.html",
            student=student
        )

    # ===============================
    # DELETE STUDENT
    # ===============================
    @app.route("/delete/<student_id>")
    def delete_student(student_id):

        if "user" not in session:
            return redirect("/login")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM students WHERE student_id=?",
            (student_id,)
        )

        conn.commit()
        conn.close()

        flash("Student Deleted Successfully")
        return redirect("/")

    # ===============================
    # SEARCH STUDENT
    # ===============================
    @app.route("/search", methods=["GET", "POST"])
    def search():

        if "user" not in session:
            return redirect("/login")

        results = []

        if request.method == "POST":

            keyword = "%" + request.form["keyword"] + "%"

            conn = get_connection()
            cur = conn.cursor()

            results = cur.execute("""
                SELECT * FROM students
                WHERE student_id LIKE ?
                OR name LIKE ?
                OR roll LIKE ?
                OR department LIKE ?
                OR semester LIKE ?
            """, (
                keyword,
                keyword,
                keyword,
                keyword,
                keyword
            )).fetchall()

            conn.close()

        return render_template(
            "search.html",
            results=results
        )

    # ===============================
    # ATTENDANCE ENTRY
    # ===============================
    @app.route("/attendance", methods=["GET", "POST"])
    def attendance():

        if "user" not in session:
            return redirect("/login")

        if request.method == "POST":

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO attendance
                (student_id,student_name,date,status)
                VALUES (?,?,?,?)
            """, (
                request.form["student_id"],
                request.form["student_name"],
                request.form["date"],
                request.form["status"]
            ))

            conn.commit()
            conn.close()

            flash("Attendance Saved")
            return redirect("/")

        return render_template(
            "attendance.html",
            today=date.today()
        )

    # ===============================
    # VIEW ATTENDANCE
    # ===============================
    @app.route("/view_attendance", methods=["GET", "POST"])
    def view_attendance():

        if "user" not in session:
            return redirect("/login")

        results = []

        if request.method == "POST":

            conn = get_connection()
            cur = conn.cursor()

            results = cur.execute("""
                SELECT * FROM attendance
                WHERE date=?
            """, (
                request.form["date"],
            )).fetchall()

            conn.close()

        return render_template(
            "view_attendance.html",
            results=results
        )

    # ===============================
    # EXPORT EXCEL
    # ===============================
    @app.route("/export")
    def export_excel():

        if "user" not in session:
            return redirect("/login")

        conn = get_connection()

        df = pd.read_sql_query(
            "SELECT * FROM students",
            conn
        )

        conn.close()

        output = io.BytesIO()

        df.to_excel(output, index=False)

        output.seek(0)

        return send_file(
            output,
            download_name="students.xlsx",
            as_attachment=True
        )