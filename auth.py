from flask import render_template, request, redirect, session, flash
from db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

from otp import generate_otp, verify_otp
from validators import valid_password, valid_email, valid_phone


def register_auth(app):

    # ==========================
    # LOGIN PAGE
    # ==========================
    @app.route("/login", methods=["GET", "POST"])
    def login():

        # already logged in
        if "user" in session:
            return redirect("/")

        if request.method == "POST":

            username = request.form["username"].strip()
            password = request.form["password"]

            conn = get_connection()
            cur = conn.cursor()

            user = cur.execute(
                """
                SELECT * FROM users
                WHERE email = ? OR phone = ?
                """,
                (username, username)
            ).fetchone()

            conn.close()

            if user:
                if check_password_hash(user["password"], password):
                    session["user"] = user["name"]
                    session["username"] = username
                    flash("Login successful")
                    return redirect("/")
                else:
                    flash("Wrong password")
            else:
                flash("User not found")

        return render_template("login.html")

    # ==========================
    # REGISTER PAGE
    # ==========================
    @app.route("/register", methods=["GET", "POST"])
    def register():

        if request.method == "POST":

            name = request.form["name"].strip()
            phone = request.form["phone"].strip()
            email = request.form["email"].strip()
            password = request.form["password"]

            # validations
            if not valid_phone(phone):
                flash("Enter valid 10 digit mobile number")
                return redirect("/register")

            if not valid_email(email):
                flash("Enter valid email address")
                return redirect("/register")

            if not valid_password(password):
                flash("Password must be 6+ chars with symbol, letter and number")
                return redirect("/register")

            conn = get_connection()
            cur = conn.cursor()

            # check existing user
            old_user = cur.execute(
                """
                SELECT * FROM users
                WHERE email = ? OR phone = ?
                """,
                (email, phone)
            ).fetchone()

            if old_user:
                conn.close()
                flash("Email or phone already registered")
                return redirect("/register")

            # insert user
            cur.execute(
                """
                INSERT INTO users(name, phone, email, password)
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    phone,
                    email,
                    generate_password_hash(password)
                )
            )

            conn.commit()
            conn.close()

            flash("Registration successful. Please login.")
            return redirect("/login")

        return render_template("register.html")

    # ==========================
    # FORGOT PASSWORD
    # ==========================
    @app.route("/forgot", methods=["GET", "POST"])
    def forgot():

        if request.method == "POST":

            username = request.form["username"].strip()

            conn = get_connection()
            cur = conn.cursor()

            user = cur.execute(
                """
                SELECT * FROM users
                WHERE email = ? OR phone = ?
                """,
                (username, username)
            ).fetchone()

            conn.close()

            if not user:
                flash("User not found")
                return redirect("/forgot")

            # generate OTP
            otp = generate_otp(username)

            # DEMO MODE:
            flash("Your OTP is: " + otp)

            # later real email/SMS can be added

            return redirect(f"/verify/{username}")

        return render_template("forgot.html")

    # ==========================
    # VERIFY OTP + RESET PASSWORD
    # ==========================
    @app.route("/verify/<username>", methods=["GET", "POST"])
    def verify(username):

        if request.method == "POST":

            entered_otp = request.form["otp"].strip()
            new_password = request.form["password"]

            if not valid_password(new_password):
                flash("Weak password")
                return redirect(f"/verify/{username}")

            # verify OTP
            if verify_otp(username, entered_otp):

                conn = get_connection()
                cur = conn.cursor()

                cur.execute(
                    """
                    UPDATE users
                    SET password = ?
                    WHERE email = ? OR phone = ?
                    """,
                    (
                        generate_password_hash(new_password),
                        username,
                        username
                    )
                )

                conn.commit()
                conn.close()

                flash("Password updated successfully")
                return redirect("/login")

            else:
                flash("Invalid or expired OTP")

        return render_template("verify.html", username=username)

    # ==========================
    # LOGOUT
    # ==========================
    @app.route("/logout")
    def logout():

        session.clear()
        flash("Logged out successfully")
        return redirect("/login")