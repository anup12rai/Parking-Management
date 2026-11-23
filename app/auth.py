
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from app.database import get_db

auth_bp = Blueprint("auth", __name__)


# Login protection decorator
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))

        return function(*args, **kwargs)

    return wrapper


# Home route
@auth_bp.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    return redirect(url_for("auth.login"))


# ==========================
# LOGIN
# ==========================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "danger")
            return render_template("login.html")

        db = None

        try:
            db = get_db()

            with db.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id, name, email, password_hash, role
                    FROM users
                    WHERE email = %s AND is_active = TRUE
                    """,
                    (email,)
                )

                user = cursor.fetchone()

            if user and check_password_hash(
                user["password_hash"], password
            ):

                session.clear()

                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]
                session["user_role"] = user["role"]

                flash(
                    f"Welcome back, {user['name']}!",
                    "success"
                )

                return redirect(url_for("dashboard.dashboard"))

            flash("Invalid email or password.", "danger")

        except Exception as error:
            flash(f"Login error: {error}", "danger")

        finally:
            if db:
                db.close()

    return render_template("login.html")


# ==========================
# CREATE ACCOUNT
# ==========================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash(
                "Password must be at least 8 characters long.",
                "danger"
            )
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        db = None

        try:
            db = get_db()

            with db.cursor() as cursor:

                cursor.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,)
                )

                existing_user = cursor.fetchone()

                if existing_user:
                    flash("Email is already registered.", "warning")
                    return render_template("register.html")

                password_hash = generate_password_hash(password)

                cursor.execute(
                    """
                    INSERT INTO users
                    (name, email, password_hash, role, is_active)
                    VALUES (%s, %s, %s, 'staff', TRUE)
                    """,
                    (name, email, password_hash)
                )

            db.commit()

            flash(
                "Account created successfully! Please log in.",
                "success"
            )

            return redirect(url_for("auth.login"))

        except Exception as error:

            if db:
                db.rollback()

            flash(f"Registration error: {error}", "danger")

        finally:
            if db:
                db.close()

    return render_template("register.html")


# ==========================
# LOGOUT
# ==========================

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    session.clear()

    flash("You have logged out successfully.", "success")

    return redirect(url_for("auth.login"))
