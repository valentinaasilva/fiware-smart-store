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
from routes.providers import providers_bp
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


def _as_float(value, default=0.0):
    parsed = _unwrap_attr(value)
    try:
        return float(parsed)
    except (TypeError, ValueError):
        return default


def _build_store_markers(selector: DataSourceSelector) -> list[dict]:
    stores = selector.list_entities("Store")
    markers: list[dict] = []
    for store in stores:
        store_id = store.get("id")
        name = _unwrap_attr(store.get("name"))
        address = _unwrap_attr(store.get("address"))
        country_code = _unwrap_attr(store.get("countryCode")) or ""
        image = _unwrap_attr(store.get("image")) or ""
        description = _unwrap_attr(store.get("description")) or ""
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
                "countryCode": country_code,
                "image": image,
                "description": description,
                "detailUrl": url_for("stores.get_store", entity_id=store_id),
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


def _estimate_stock_value(selector: DataSourceSelector) -> float:
    products = selector.list_entities("Product")
    inventory_items = selector.list_entities("InventoryItem")
    prices_by_product = {product.get("id"): _as_float(product.get("price"), 0.0) for product in products}

    total = 0.0
    for item in inventory_items:
        product_id = _unwrap_attr(item.get("refProduct"))
        stock_count = _as_int(item.get("stockCount"), 0)
        total += prices_by_product.get(product_id, 0.0) * max(stock_count, 0)

    return round(total, 2)


def _build_store_management_rows(selector: DataSourceSelector) -> list[dict]:
    stores = selector.list_entities("Store")
    rows: list[dict] = []
    for store in stores:
        name = _unwrap_attr(store.get("name")) or store.get("id")
        location = _unwrap_attr(store.get("location"))
        address = _unwrap_attr(store.get("address"))
        coords = location.get("coordinates") if isinstance(location, dict) else None
        city = ""
        if isinstance(address, dict):
            city = address.get("addressLocality") or ""
        status = "Operational" if isinstance(coords, list) and len(coords) == 2 else "Not operational"
        rows.append(
            {
                "id": store.get("id"),
                "name": name,
                "location": city or _unwrap_attr(store.get("countryCode")) or "-",
                "status": status,
            }
        )

    return sorted(rows, key=lambda row: row.get("name", ""))[:4]


def _build_featured_offers(selector: DataSourceSelector) -> list[dict]:
    products = selector.list_entities("Product")
    if not products:
        return []

    product_rows = []
    for product in products:
        product_rows.append(
            {
                "id": product.get("id"),
                "name": _unwrap_attr(product.get("name")) or "Producto",
                "category": _unwrap_attr(product.get("category")) or "",
                "price": _as_float(product.get("price"), 0.0),
                "image": _unwrap_attr(product.get("image")) or "",
            }
        )

    # Offer definitions map UI copy to real products in matching categories.
    definitions = [
        {
            "category": "Frescos",
            "title": "Frutas y Verduras de Temporada",
            "description": "Seleccion premium de nuestros agricultores locales.",
        },
        {
            "category": "Lacteos",
            "title": "Lacteos para Cada Dia",
            "description": "Ahorro diario en leche, queso y esenciales refrigerados.",
        },
        {
            "category": "Panaderia",
            "title": "Pan Recien Horneado",
            "description": "Especialidades artesanas horneadas cada manana.",
        },
    ]

    featured = []
    used_ids = set()
    for definition in definitions:
        candidates = [
            row for row in product_rows if row.get("category") == definition["category"] and row.get("id") not in used_ids
        ]
        if not candidates:
            candidates = [row for row in product_rows if row.get("id") not in used_ids]
        if not candidates:
            continue

        product = min(candidates, key=lambda row: row.get("price", 0.0))
        used_ids.add(product.get("id"))
        featured.append(
            {
                "product_id": product.get("id"),
                "title": definition["title"],
                "from_price": product.get("price", 0.0),
                "description": definition["description"],
                "image": product.get("image"),
                "product_name": product.get("name"),
            }
        )

    return featured


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
    app.register_blueprint(providers_bp)

    @app.get("/")
    def dashboard():
        stats = selector.get_dashboard_stats()
        return render_template(
            "dashboard.html",
            stats=stats,
            source_mode=selector.mode,
            low_stock_count=_count_low_stock(selector),
            estimated_stock_value=_estimate_stock_value(selector),
            stores_map=_build_store_markers(selector),
            managed_stores=_build_store_management_rows(selector),
            featured_offers=_build_featured_offers(selector),
        )

    @app.get("/stores-map")
    def stores_map():
        return render_template(
            "stores/map.html",
            stores_map=_build_store_markers(selector),
        )

    return app


app = create_app()
socketio.init_app(app)


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=True,
        allow_unsafe_werkzeug=True,
    )
