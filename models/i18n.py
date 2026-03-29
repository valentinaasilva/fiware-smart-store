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
        "Customer Support": "Customer Support",
        "Search products, stores...": "Search products, stores...",
        "Notifications": "Notifications",
        "Dark Mode": "Dark Mode",
        "Light Mode": "Light Mode",
        "Administrator": "Administrator",
        "Stores Map": "Stores Map",
        "Dashboard": "Dashboard",
        "Welcome to Xantadis": "Welcome to Xantadis",
        "Freshness, quality and trusted service for your day-to-day shopping.": "Freshness, quality and trusted service for your day-to-day shopping.",
        "Total Products": "Total Products",
        "Low Stock": "Low Stock",
        "View Catalog": "View Catalog",
        "Manage Stores": "Manage Stores",
        "Active source mode": "Active source mode",
        "Inventory Items": "Inventory Items",
        "Inventory": "Inventory",
        "Shelves": "Shelves",
        "Products in Store": "Products in Store",
        "Available in Stores": "Available in Stores",
        "Store Detail": "Store Detail",
        "Product Detail": "Product Detail",
        "Employee Detail": "Employee Detail",
        "ID": "ID",
        "Name": "Name",
        "Country": "Country",
        "Origin Country": "Origin Country",
        "Spain": "Spain",
        "Germany": "Germany",
        "France": "France",
        "Ecuador": "Ecuador",
        "Address": "Address",
        "Type": "Type",
        "Price": "Price",
        "Product": "Product",
        "Shelf": "Shelf",
        "Stock Count": "Stock Count",
        "Shelf Count": "Shelf Count",
        "Max Capacity": "Max Capacity",
        "Current Load": "Current Load",
        "Actions": "Actions",
        "Add Shelf": "Add Shelf",
        "Add Inventory Item": "Add Inventory Item",
        "Update": "Update",
        "Delete": "Delete",
        "No records": "No records",
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
        "Customer Support": "Atencion al Cliente",
        "Search products, stores...": "Buscar productos, sucursales...",
        "Notifications": "Notificaciones",
        "Dark Mode": "Modo Oscuro",
        "Light Mode": "Modo Claro",
        "Administrator": "Administrador",
        "Stores Map": "Mapa de Tiendas",
        "Dashboard": "Panel",
        "Welcome to Xantadis": "Bienvenido a Xantadis",
        "Freshness, quality and trusted service for your day-to-day shopping.": "Calidad, frescura y el mejor servicio para tu dia a dia.",
        "Total Products": "Productos Totales",
        "Low Stock": "Stock Bajo",
        "View Catalog": "Ver Todo el Catalogo",
        "Manage Stores": "Administrar Tiendas",
        "Active source mode": "Fuente activa",
        "Inventory Items": "Items de Inventario",
        "Inventory": "Inventario",
        "Shelves": "Estanterias",
        "Products in Store": "Productos en Tienda",
        "Available in Stores": "Disponible en Tiendas",
        "Store Detail": "Detalle de Tienda",
        "Product Detail": "Detalle de Producto",
        "Employee Detail": "Detalle de Empleado",
        "ID": "ID",
        "Name": "Nombre",
        "Country": "Pais",
        "Origin Country": "Pais de origen",
        "Spain": "Espana",
        "Germany": "Alemania",
        "France": "Francia",
        "Ecuador": "Ecuador",
        "Address": "Direccion",
        "Type": "Tipo",
        "Price": "Precio",
        "Product": "Producto",
        "Shelf": "Estanteria",
        "Stock Count": "Stock",
        "Shelf Count": "Cantidad en Estanteria",
        "Max Capacity": "Capacidad Maxima",
        "Current Load": "Carga Actual",
        "Actions": "Acciones",
        "Add Shelf": "Agregar Estanteria",
        "Add Inventory Item": "Agregar Item de Inventario",
        "Update": "Actualizar",
        "Delete": "Eliminar",
        "No records": "Sin registros",
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
