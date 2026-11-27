
import os
import hmac
import re
import secrets
import sqlite3

from pathlib import Path
from functools import wraps

from flask import (
    Flask, abort, redirect, render_template,
    request, session, url_for, flash
)
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("RENDER") == "true",
)

HUB_USERNAME = os.environ.get("HUB_USERNAME", "admin")
HUB_PASSWORD = os.environ.get("HUB_PASSWORD", "")

DATABASE_PATH = Path(
    os.environ.get("DATABASE_PATH", "instance/kelyanti.sqlite3")
)

DEFAULT_COLOR = "#8b5cf6"

PAGES = {
    "dashboard": (
        "Tableau de bord",
        "Bienvenue sur ton espace Kelyanti Hub.",
        "dashboard"
    ),
    "minecraft": (
        "Minecraft",
        "Retrouve ici les outils de ton serveur Minecraft.",
        "minecraft"
    ),
    "arduino": (
        "Arduino",
        "Centralise tes projets et notes Arduino.",
        "arduino"
    ),
    "settings": (
        "Paramètres",
        "Personnalise ton espace Kelyanti Hub.",
        "settings"
    ),
    "account": (
        "Mon compte",
        "Gère ton espace personnel.",
        "account"
    ),
}


# -------------------------
# BASE DE DONNÉES
# -------------------------

def get_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = {
            row["name"]
            for row in db.execute("PRAGMA table_info(members)").fetchall()
        }

        if "grade" not in columns:
            db.execute("""
                ALTER TABLE members
                ADD COLUMN grade TEXT NOT NULL DEFAULT 'member'
            """)

        if "theme_color" not in columns:
            db.execute("""
                ALTER TABLE members
                ADD COLUMN theme_color TEXT NOT NULL DEFAULT '#8b5cf6'
            """)


init_db()


# -------------------------
# CSRF
# -------------------------

def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)

    return session["_csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


def check_csrf():
    submitted = request.form.get("_csrf", "")
    expected = session.get("_csrf", "")

    if not expected or not hmac.compare_digest(submitted, expected):
        abort(400, "Formulaire expiré. Recharge la page.")


# -------------------------
# OUTILS COMPTE
# -------------------------

def current_member():
    member_id = session.get("member_id")

    if not member_id:
        return None

    with get_db() as db:
        return db.execute(
            "SELECT * FROM members WHERE id = ?",
            (member_id,)
        ).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            member = current_member()

            if not member or not member["active"]:
                session.clear()
                return redirect(url_for("login"))

            # Actualise le grade depuis la base
            session["role"] = member["grade"]

        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)

        return view(*args, **kwargs)

    return wrapped


# -------------------------
# SERVICE WORKER
# -------------------------

@app.get("/service-worker.js")
def service_worker():
    response = app.send_static_file("service-worker.js")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Content-Type"] = (
        "application/javascript; charset=utf-8"
    )
    return response


# -------------------------
# ACCUEIL ET PAGES
# -------------------------

@app.get("/")
@login_required
def home():
    return redirect(url_for("section", page="dashboard"))


@app.get("/<page>")
@login_required
def section(page):
    if page not in PAGES:
        abort(404)

    title, description, active = PAGES[page]

    member = current_member() if session.get("role") != "admin" else None

    theme_color = (
        member["theme_color"]
        if member
        else DEFAULT_COLOR
    )

    return render_template(
        "section.html",
        title=title,
        description=description,
        active=active,
        page=page,
        theme_color=theme_color
    )


# -------------------------
# CONNEXION
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        check_csrf()

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Administrateur
        if (
            HUB_PASSWORD
            and hmac.compare_digest(username, HUB_USERNAME)
            and hmac.compare_digest(password, HUB_PASSWORD)
        ):
            session.clear()
            session["logged_in"] = True
            session["username"] = HUB_USERNAME
            session["role"] = "admin"

            return redirect(url_for("home"))

        # Membres
        with get_db() as db:
            member = db.execute(
                "SELECT * FROM members WHERE username = ?",
                (username,)
            ).fetchone()

        if (
            member
            and member["active"]
            and check_password_hash(member["password_hash"], password)
        ):
            session.clear()
            session["logged_in"] = True
            session["username"] = member["username"]
            session["role"] = member["grade"]
            session["member_id"] = member["id"]

            return redirect(url_for("home"))

        error = "Identifiant ou mot de passe incorrect."

    return render_template("login.html", error=error)


# -------------------------
# DÉCONNEXION
# -------------------------

@app.post("/logout")
@login_required
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("login"))


# -------------------------
# PERSONNALISATION
# -------------------------

@app.post("/settings/theme")
@login_required
def change_theme():
    check_csrf()

    if session.get("role") == "admin":
        flash(
            "La personnalisation du compte administrateur sera ajoutée séparément.",
            "error"
        )
        return redirect(url_for("section", page="settings"))

    color = request.form.get("theme_color", "").strip()

    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        flash("Cette couleur n'est pas valide.", "error")
        return redirect(url_for("section", page="settings"))

    with get_db() as db:
        db.execute(
            "UPDATE members SET theme_color = ? WHERE id = ?",
            (color, session["member_id"])
        )

    flash("Ta couleur a été enregistrée.", "success")
    return redirect(url_for("section", page="settings"))


# -------------------------
# MOT DE PASSE PERSONNEL
# -------------------------

@app.post("/account/password")
@login_required
def change_own_password():
    check_csrf()

    if session.get("role") == "admin":
        flash(
            "Le mot de passe administrateur se gère dans les paramètres Render.",
            "error"
        )
        return redirect(url_for("section", page="account"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    member = current_member()

    if not member or not check_password_hash(
        member["password_hash"], current_password
    ):
        flash("Ton mot de passe actuel est incorrect.", "error")
        return redirect(url_for("section", page="account"))

    if len(new_password) < 10:
        flash("Le nouveau mot de passe doit contenir au moins 10 caractères.", "error")
        return redirect(url_for("section", page="account"))

    if new_password != confirm_password:
        flash("Les deux nouveaux mots de passe ne correspondent pas.", "error")
        return redirect(url_for("section", page="account"))

    with get_db() as db:
        db.execute(
            "UPDATE members SET password_hash = ? WHERE id = ?",
            (
                generate_password_hash(new_password),
                session["member_id"]
            )
        )

    flash("Ton mot de passe a été modifié.", "success")
    return redirect(url_for("section", page="account"))


# -------------------------
# GESTION DES MEMBRES
# ADMIN UNIQUEMENT
# -------------------------

@app.get("/members")
@admin_required
def members():
    with get_db() as db:
        all_members = db.execute("""
            SELECT id, username, active, created_at, grade, theme_color
            FROM members
            ORDER BY id DESC
        """).fetchall()

    return render_template("members.html", members=all_members)


@app.post("/members/create")
@admin_required
def create_member():
    check_csrf()

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not re.fullmatch(r"[a-zA-Z0-9_.-]{3,30}", username):
        flash("Le pseudo doit contenir 3 à 30 caractères et uniquement des lettres, chiffres, points, tirets ou underscores.", "error")
        return redirect(url_for("members"))

    if username.casefold() == HUB_USERNAME.casefold():
        flash("Ce pseudo est réservé à l'administrateur.", "error")
        return redirect(url_for("members"))

    if len(password) < 10:
        flash("Le mot de passe doit contenir au moins 10 caractères.", "error")
        return redirect(url_for("members"))

    try:
        with get_db() as db:
            db.execute(
                """
                INSERT INTO members (username, password_hash)
                VALUES (?, ?)
                """,
                (username, generate_password_hash(password))
            )

        flash("Le membre a été créé.", "success")

    except sqlite3.IntegrityError:
        flash("Ce pseudo existe déjà.", "error")

    return redirect(url_for("members"))


@app.post("/members/<int:member_id>/grade")
@admin_required
def change_member_grade(member_id):
    check_csrf()

    grade = request.form.get("grade", "")

    if grade not in ("member", "moderator"):
        flash("Ce grade n'est pas autorisé.", "error")
        return redirect(url_for("members"))

    with get_db() as db:
        db.execute(
            "UPDATE members SET grade = ? WHERE id = ?",
            (grade, member_id)
        )

    flash("Le grade du membre a été modifié.", "success")
    return redirect(url_for("members"))


@app.post("/members/<int:member_id>/toggle")
@admin_required
def toggle_member(member_id):
    check_csrf()

    with get_db() as db:
        member = db.execute(
            "SELECT active FROM members WHERE id = ?",
            (member_id,)
        ).fetchone()

        if member:
            new_status = 0 if member["active"] else 1

            db.execute(
                "UPDATE members SET active = ? WHERE id = ?",
                (new_status, member_id)
            )

            flash("Le statut du membre a été modifié.", "success")

    return redirect(url_for("members"))


@app.post("/members/<int:member_id>/password")
@admin_required
def change_member_password(member_id):
    check_csrf()

    password = request.form.get("password", "")

    if len(password) < 10:
        flash("Le mot de passe doit contenir au moins 10 caractères.", "error")
        return redirect(url_for("members"))

    with get_db() as db:
        db.execute(
            "UPDATE members SET password_hash = ? WHERE id = ?",
            (generate_password_hash(password), member_id)
        )

    flash("Le mot de passe a été modifié.", "success")
    return redirect(url_for("members"))


@app.post("/members/<int:member_id>/delete")
@admin_required
def delete_member(member_id):
    check_csrf()

    with get_db() as db:
        db.execute(
            "DELETE FROM members WHERE id = ?",
            (member_id,)
        )

    flash("Le compte a été supprimé.", "success")
    return redirect(url_for("members"))


# -------------------------
# ERREURS
# -------------------------

@app.errorhandler(400)
def bad_request(error):
    return render_template(
        "error.html",
        code=400,
        message=getattr(error, "description", "Requête incorrecte.")
    ), 400


@app.errorhandler(403)
def forbidden(error):
    return render_template(
        "error.html",
        code=403,
        message="Tu n'as pas l'autorisation d'accéder à cette page."
    ), 403


@app.errorhandler(404)
def not_found(error):
    return render_template(
        "error.html",
        code=404,
        message="Cette page n'existe pas."
    ), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
