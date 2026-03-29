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


def _unwrap_attr(value):
    if isinstance(value, dict) and "value" in value:
        return value.get("value")
    return value


def _as_int(value, default=0):
    parsed = _unwrap_attr(value)
    try:
        return int(parsed)
    except (TypeError, ValueError):
        return default


def _build_store_markers(selector: DataSourceSelector) -> list[dict]:
    stores = selector.list_entities("Store")
    markers: list[dict] = []
    for store in stores:
        store_id = store.get("id")
        name = _unwrap_attr(store.get("name"))
        address = _unwrap_attr(store.get("address"))
        location = _unwrap_attr(store.get("location"))
        coords = location.get("coordinates") if isinstance(location, dict) else None
        if not isinstance(coords, list) or len(coords) != 2:
            continue
        lng, lat = coords[0], coords[1]
        try:
            lng = float(lng)
            lat = float(lat)
        except (TypeError, ValueError):
            continue
        if lat < -90 or lat > 90 or lng < -180 or lng > 180:
            continue
        markers.append(
            {
                "id": store_id,
                "name": name or store_id,
                "address": address,
                "lat": lat,
                "lng": lng,
            }
        )
    return markers


def _count_low_stock(selector: DataSourceSelector) -> int:
    inventory_items = selector.list_entities("InventoryItem")
    count = 0
    for item in inventory_items:
        stock_count = _as_int(item.get("stockCount"), 0)
        shelf_count = _as_int(item.get("shelfCount"), 0)
        if stock_count <= 10 or shelf_count <= 3:
            count += 1
    return count


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
        return render_template(
            "dashboard.html",
            stats=stats,
            source_mode=selector.mode,
            low_stock_count=_count_low_stock(selector),
            stores_map=_build_store_markers(selector),
        )

    return app


app = create_app()
socketio.init_app(app)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("FLASK_PORT", "5000")), debug=True)
