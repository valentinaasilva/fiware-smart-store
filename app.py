import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO

from models.data_source import DataSourceSelector
from models.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, normalize_locale, resolve_locale, translate
from routes.employees import employees_bp
from routes.inventory import inventory_bp
from routes.notifications import notifications_bp
from routes.products import products_bp
from routes.stores import stores_bp

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    default_sqlite_path = Path(app.instance_path) / "fiware.db"
    app.config["SQLITE_PATH"] = os.getenv("SQLITE_PATH", str(default_sqlite_path))

    selector = DataSourceSelector(
        orion_url=os.getenv("ORION_URL", "http://localhost:1026"),
        sqlite_path=app.config["SQLITE_PATH"],
    )
    selector.bootstrap()

    app.extensions["data_selector"] = selector
    app.extensions["socketio"] = socketio

    @app.before_request
    def set_locale() -> None:
        selected = resolve_locale(request, session.get("lang"))
        session["lang"] = selected
        g.lang = selected

    @app.context_processor
    def inject_i18n():
        def _(label: str) -> str:
            return translate(label, getattr(g, "lang", DEFAULT_LOCALE))

        return {
            "_": _,
            "current_lang": getattr(g, "lang", DEFAULT_LOCALE),
            "supported_langs": SUPPORTED_LOCALES,
        }

    @app.get("/language/<lang>")
    def set_language(lang: str):
        session["lang"] = normalize_locale(lang)
        next_url = request.args.get("next", "")
        if not next_url.startswith("/"):
            next_url = url_for("dashboard")
        return redirect(next_url)

    app.register_blueprint(stores_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(notifications_bp)

    @app.get("/")
    def dashboard():
        stats = selector.get_dashboard_stats()
        return render_template("dashboard.html", stats=stats, source_mode=selector.mode)

    return app


app = create_app()
socketio.init_app(app)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("FLASK_PORT", "5000")), debug=True)
