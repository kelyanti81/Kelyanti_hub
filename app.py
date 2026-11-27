import hmac
import os
import secrets
from functools import wraps

from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("RENDER") == "true",
)

HUB_USERNAME = os.environ.get("HUB_USERNAME", "admin")
HUB_PASSWORD = os.environ.get("HUB_PASSWORD", "")

PAGES = {
    "dashboard": ("Tableau de bord", "Bienvenue sur ton espace Kelyanti Hub.", "dashboard"),
    "minecraft": ("Minecraft", "Retrouve ici les outils et informations de ton serveur Minecraft.", "minecraft"),
    "arduino": ("Arduino", "Centralise tes projets, montages et notes Arduino.", "arduino"),
    "settings": ("Paramètres", "Les réglages généraux de ton espace arriveront ici.", "settings"),
    "account": ("Mon compte", "Gère ta session et les informations de ton compte.", "account"),
}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


def check_csrf():
    submitted = request.form.get("_csrf", "")
    expected = session.get("_csrf", "")
    if not expected or not hmac.compare_digest(submitted, expected):
        abort(400, "Formulaire expiré. Recharge la page et réessaie.")


@app.get("/service-worker.js")
def service_worker():
    response = app.send_static_file("service-worker.js")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Content-Type"] = "application/javascript; charset=utf-8"
    return response


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
    return render_template("section.html", title=title, description=description, active=active, page=page)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if HUB_PASSWORD and hmac.compare_digest(username, HUB_USERNAME) and hmac.compare_digest(password, HUB_PASSWORD):
            session.clear()
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        error = "Identifiant ou mot de passe incorrect."
    return render_template("login.html", error=error)


@app.post("/logout")
@login_required
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("login"))


@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", code=400, message=getattr(error, "description", "Requête incorrecte.")), 400


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Cette page n'existe pas."), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
