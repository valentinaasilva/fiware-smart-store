from __future__ import annotations

from flask import Request

SUPPORTED_LOCALES = ("en", "es")
DEFAULT_LOCALE = "en"

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "Home": "Home",
        "Stores": "Stores",
        "Products": "Products",
        "Employees": "Employees",
        "Language": "Language",
        "Dashboard": "Dashboard",
        "Active source mode": "Active source mode",
        "Inventory Items": "Inventory Items",
        "Store Detail": "Store Detail",
        "Product Detail": "Product Detail",
        "Employee Detail": "Employee Detail",
        "ID": "ID",
        "Name": "Name",
        "Country": "Country",
        "Spain": "Spain",
        "Germany": "Germany",
        "France": "France",
        "Address": "Address",
        "Type": "Type",
        "Price": "Price",
        "Category": "Category",
        "Image": "Image",
        "Role": "Role",
        "Salary": "Salary",
        "Ref Store": "Ref Store",
        "Store Location": "Store Location",
        "Location unavailable": "Location unavailable",
    },
    "es": {
        "Home": "Inicio",
        "Stores": "Tiendas",
        "Products": "Productos",
        "Employees": "Empleados",
        "Language": "Idioma",
        "Dashboard": "Panel",
        "Active source mode": "Fuente activa",
        "Inventory Items": "Items de Inventario",
        "Store Detail": "Detalle de Tienda",
        "Product Detail": "Detalle de Producto",
        "Employee Detail": "Detalle de Empleado",
        "ID": "ID",
        "Name": "Nombre",
        "Country": "Pais",
        "Spain": "Espana",
        "Germany": "Alemania",
        "France": "Francia",
        "Address": "Direccion",
        "Type": "Tipo",
        "Price": "Precio",
        "Category": "Categoria",
        "Image": "Imagen",
        "Role": "Rol",
        "Salary": "Salario",
        "Ref Store": "Ref Tienda",
        "Store Location": "Ubicacion de tienda",
        "Location unavailable": "Ubicacion no disponible",
    },
}


def normalize_locale(value: str | None) -> str:
    if not value:
        return DEFAULT_LOCALE
    lang = value.strip().lower()[:2]
    return lang if lang in SUPPORTED_LOCALES else DEFAULT_LOCALE


def resolve_locale(request: Request, session_lang: str | None) -> str:
    requested = normalize_locale(request.args.get("lang")) if request.args.get("lang") else None
    if requested and requested in SUPPORTED_LOCALES:
        return requested

    saved = normalize_locale(session_lang) if session_lang else None
    if saved and saved in SUPPORTED_LOCALES:
        return saved

    best = request.accept_languages.best_match(SUPPORTED_LOCALES)
    return normalize_locale(best)


def translate(label: str, locale: str) -> str:
    lang = normalize_locale(locale)
    return _TRANSLATIONS.get(lang, {}).get(label, label)
