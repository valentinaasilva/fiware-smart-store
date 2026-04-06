from collections import defaultdict
from uuid import uuid4

from flask import Blueprint, current_app, g, jsonify, redirect, render_template, request, url_for

from models.i18n import DEFAULT_LOCALE, translate
from routes.utils import (
    PRODUCT_CATEGORIES,
    denormalize_ngsi_entities,
    maybe_denormalize_for_view,
    extract_payload,
    normalize_ngsi_payload,
    wants_json,
)

products_bp = Blueprint("products", __name__, url_prefix="/products")


def _extract_attr_value(value):
    if isinstance(value, dict) and "value" in value:
        return value.get("value")
    return value


def _as_int(value, default=0):
    parsed = _extract_attr_value(value)
    try:
        return int(parsed)
    except (TypeError, ValueError):
        return default


def _short_entity_id(entity_id: str | None) -> str:
    if not isinstance(entity_id, str):
        return ""
    return entity_id.split(":")[-1]


def _build_inventory_item_id(product_id: str, store_id: str, shelf_id: str) -> str:
    return (
        "urn:ngsi-ld:InventoryItem:"
        f"{_short_entity_id(store_id)}-{_short_entity_id(shelf_id)}-{_short_entity_id(product_id)}-{uuid4().hex[:6]}"
    )


def _filter_products(products: list[dict], query: str, locale: str) -> list[dict]:
    q = (query or "").strip().lower()
    if not q:
        return products

    filtered = []
    for product in products:
        translated_name = translate(str(product.get("name", "")), locale)
        translated_category = translate(str(product.get("category", "")), locale)
        values = [
            str(product.get("id", "")),
            str(product.get("name", "")),
            translated_name,
            str(product.get("category", "")),
            translated_category,
            str(product.get("originCountry", "")),
        ]
        if any(q in value.lower() for value in values):
            filtered.append(product)
    return filtered


def _filter_stores(stores: list[dict], query: str) -> list[dict]:
    q = (query or "").strip().lower()
    if not q:
        return stores

    filtered = []
    for store in stores:
        address = store.get("address")
        if isinstance(address, dict):
            address_text = " ".join(
                [
                    str(address.get("streetAddress", "")),
                    str(address.get("addressLocality", "")),
                    str(address.get("addressRegion", "")),
                ]
            )
        else:
            address_text = str(address or "")

        values = [
            str(store.get("id", "")),
            str(store.get("name", "")),
            str(store.get("countryCode", "")),
            address_text,
        ]
        if any(q in value.lower() for value in values):
            filtered.append(store)
    return filtered


def _inventory_relationship_ids(item: dict) -> tuple[str | None, str | None, str | None]:
    return (
        _extract_attr_value(item.get("refStore")),
        _extract_attr_value(item.get("refShelf")),
        _extract_attr_value(item.get("refProduct")),
    )


def _ensure_product_inventory_business_rules(selector, payload: dict, product_id: str, exclude_inventory_id: str | None = None):
    ref_store, ref_shelf, ref_product = _inventory_relationship_ids(payload)
    if ref_product != product_id:
        raise ValueError("InventoryItem.refProduct must match the product context")

    store = selector.get_entity(ref_store) if ref_store else None
    if not store:
        raise ValueError("Referenced store does not exist")

    shelf = selector.get_entity(ref_shelf) if ref_shelf else None
    if not shelf:
        raise ValueError("Referenced shelf does not exist")

    shelf_store = _extract_attr_value(shelf.get("refStore"))
    if shelf_store != ref_store:
        raise ValueError("InventoryItem.refShelf must belong to InventoryItem.refStore")

    items_for_product = selector.list_entities_filtered("InventoryItem", "refProduct", product_id)
    for existing in items_for_product:
        if exclude_inventory_id and existing.get("id") == exclude_inventory_id:
            continue
        e_store, e_shelf, e_product = _inventory_relationship_ids(existing)
        if (e_store, e_shelf, e_product) == (ref_store, ref_shelf, ref_product):
            raise ValueError("InventoryItem with same store/shelf/product already exists")

    shelf_capacity = _as_int(shelf.get("maxCapacity"), default=0)
    incoming_shelf_count = _as_int(payload.get("shelfCount"), default=0)
    current_total = 0
    items_same_store = selector.list_entities_filtered("InventoryItem", "refStore", ref_store)
    for existing in items_same_store:
        if exclude_inventory_id and existing.get("id") == exclude_inventory_id:
            continue
        _, e_shelf, _ = _inventory_relationship_ids(existing)
        if e_shelf == ref_shelf:
            current_total += _as_int(existing.get("shelfCount"), default=0)
    if shelf_capacity > 0 and (current_total + incoming_shelf_count) > shelf_capacity:
        raise ValueError("Shelf capacity exceeded")


def _build_product_detail_context(product_id: str) -> dict:
    selector = current_app.extensions["data_selector"]
    inventory_items = selector.list_entities_filtered("InventoryItem", "refProduct", product_id)
    stores = selector.list_entities("Store")
    shelves = selector.list_entities("Shelf")

    store_by_id = {store.get("id"): store for store in stores}
    shelf_by_id = {shelf.get("id"): shelf for shelf in shelves}

    denorm_inventory = denormalize_ngsi_entities(inventory_items)
    available_stores = {}
    used_shelves_by_store: dict[str, set[str]] = defaultdict(set)
    grouped_by_store: dict[str, dict] = {}
    for item in denorm_inventory:
        store_id = item.get("refStore")
        shelf_id = item.get("refShelf")
        store = store_by_id.get(store_id)
        shelf = shelf_by_id.get(shelf_id)
        if not store:
            continue
        denorm_store = maybe_denormalize_for_view(store)
        if store_id not in available_stores:
            available_stores[store_id] = {
                "id": store_id,
                "name": denorm_store.get("name", store_id),
                "stockCount": 0,
                "shelfCount": 0,
            }
        available_stores[store_id]["stockCount"] += _as_int(item.get("stockCount"), 0)
        available_stores[store_id]["shelfCount"] += _as_int(item.get("shelfCount"), 0)

        store_group = grouped_by_store.setdefault(
            store_id,
            {
                "id": store_id,
                "name": denorm_store.get("name", store_id),
                "stockCountTotal": 0,
                "shelves": [],
                "availableShelves": [],
            },
        )
        store_group["stockCountTotal"] += _as_int(item.get("stockCount"), 0)
        store_group["shelves"].append(
            {
                **item,
                "storeName": denorm_store.get("name", store_id),
                "shelfName": maybe_denormalize_for_view(shelf).get("name") if shelf else shelf_id,
            }
        )
        if isinstance(shelf_id, str):
            used_shelves_by_store[store_id].add(shelf_id)

    inventory_rows = []
    for item in denorm_inventory:
        store = store_by_id.get(item.get("refStore"))
        shelf = shelf_by_id.get(item.get("refShelf"))
        inventory_rows.append(
            {
                **item,
                "storeName": maybe_denormalize_for_view(store).get("name") if store else item.get("refStore"),
                "shelfName": maybe_denormalize_for_view(shelf).get("name") if shelf else item.get("refShelf"),
            }
        )

    denorm_stores = [maybe_denormalize_for_view(store) for store in stores]
    denorm_shelves = [maybe_denormalize_for_view(shelf) for shelf in shelves]

    for store_id, group in grouped_by_store.items():
        for shelf in denorm_shelves:
            shelf_id = shelf.get("id")
            if shelf.get("refStore") != store_id:
                continue
            if shelf_id in used_shelves_by_store.get(store_id, set()):
                continue
            group["availableShelves"].append(
                {
                    "id": shelf_id,
                    "shortId": _short_entity_id(shelf_id),
                    "name": shelf.get("name") or shelf_id,
                }
            )

        group["availableShelves"] = sorted(group["availableShelves"], key=lambda row: row.get("name", ""))
        group["shelves"] = sorted(group["shelves"], key=lambda row: row.get("shelfName", ""))

    product_inventory_groups = sorted(grouped_by_store.values(), key=lambda row: row.get("name", ""))

    return {
        "inventory_items": sorted(inventory_rows, key=lambda row: row.get("id", "")),
        "available_stores": sorted(available_stores.values(), key=lambda row: row.get("name", "")),
        "all_stores": sorted(denorm_stores, key=lambda row: row.get("name", "")),
        "all_shelves": sorted(denorm_shelves, key=lambda row: row.get("name", "")),
        "product_inventory_groups": product_inventory_groups,
    }


@products_bp.get("/")
def list_products():
    selector = current_app.extensions["data_selector"]
    products = denormalize_ngsi_entities(selector.list_entities("Product"))
    query = request.args.get("q", "").strip()
    locale = getattr(g, "lang", DEFAULT_LOCALE)
    filtered_products = _filter_products(products, query, locale)

    search_results: list[dict] = []
    if query:
        stores = denormalize_ngsi_entities(selector.list_entities("Store"))
        filtered_stores = _filter_stores(stores, query)
        search_results = [
            {
                "id": product.get("id"),
                "name": product.get("name") or product.get("id"),
                "display_name": translate(str(product.get("name") or product.get("id")), locale),
                "type": "Product",
                "detail_url": url_for("products.get_product", entity_id=product.get("id")),
            }
            for product in filtered_products
        ] + [
            {
                "id": store.get("id"),
                "name": store.get("name") or store.get("id"),
                "display_name": store.get("name") or store.get("id"),
                "type": "Store",
                "detail_url": url_for("stores.get_store", entity_id=store.get("id")),
            }
            for store in filtered_stores
        ]

        search_results = sorted(
            search_results,
            key=lambda row: (row.get("display_name") or row.get("name") or "").lower(),
        )

    if wants_json(request):
        return jsonify(filtered_products)
    return render_template(
        "products/list.html",
        products=filtered_products,
        search_results=search_results,
        query=query,
        product_categories=sorted(PRODUCT_CATEGORIES),
    )


@products_bp.get("")
def list_products_no_slash():
    return list_products()


@products_bp.get("/new")
def new_product_page():
    return render_template("products/form.html", product=None, product_categories=sorted(PRODUCT_CATEGORIES))


@products_bp.post("/new")
def create_product_form():
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Product")
        current_app.extensions["data_selector"].create_entity(payload)
    except ValueError:
        pass
    return redirect(url_for("products.list_products"))


@products_bp.get("/edit/<path:entity_id>")
def edit_product_page(entity_id: str):
    product = current_app.extensions["data_selector"].get_entity(entity_id)
    if not product:
        return redirect(url_for("products.list_products"))
    return render_template(
        "products/form.html",
        product=maybe_denormalize_for_view(product),
        product_categories=sorted(PRODUCT_CATEGORIES),
    )


@products_bp.post("/edit/<path:entity_id>")
def update_product_form(entity_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(entity_id)
    if current:
        incoming = extract_payload(request)
        incoming.pop("id", None)
        try:
            payload = normalize_ngsi_payload(incoming, "Product", partial=True)
            selector.update_entity(entity_id, payload)
        except ValueError:
            pass
    return redirect(url_for("products.list_products"))


@products_bp.post("/delete/<path:entity_id>")
def delete_product_form(entity_id: str):
    selector = current_app.extensions["data_selector"]
    inventory_items = selector.list_entities_filtered("InventoryItem", "refProduct", entity_id)
    if not inventory_items:
        selector.delete_entity(entity_id)
    return redirect(url_for("products.list_products"))


@products_bp.get("/<path:entity_id>")
def get_product(entity_id: str):
    selector = current_app.extensions["data_selector"]
    product = selector.get_entity(entity_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    context = _build_product_detail_context(entity_id)
    if wants_json(request):
        return jsonify(product)
    return render_template("products/detail.html", product=maybe_denormalize_for_view(product), **context)


@products_bp.post("/")
def create_product():
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Product")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    product = current_app.extensions["data_selector"].create_entity(payload)
    return jsonify(product), 201


@products_bp.put("/<path:entity_id>")
def update_product(entity_id: str):
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Product", partial=True)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    product = current_app.extensions["data_selector"].update_entity(entity_id, payload)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


@products_bp.delete("/<path:entity_id>")
def delete_product(entity_id: str):
    selector = current_app.extensions["data_selector"]
    inventory_items = selector.list_entities_filtered("InventoryItem", "refProduct", entity_id)
    if inventory_items:
        return jsonify({"error": "Cannot delete product with inventory items"}), 409
    deleted = current_app.extensions["data_selector"].delete_entity(entity_id)
    if not deleted:
        return jsonify({"error": "Product not found"}), 404
    return "", 204


@products_bp.get("/<path:product_id>/inventory")
def list_product_inventory(product_id: str):
    inventory_items = current_app.extensions["data_selector"].list_entities_filtered("InventoryItem", "refProduct", product_id)
    return jsonify(inventory_items)


@products_bp.post("/<path:product_id>/inventory")
def create_product_inventory(product_id: str):
    selector = current_app.extensions["data_selector"]
    if not selector.get_entity(product_id):
        return jsonify({"error": "Product not found"}), 404

    incoming = extract_payload(request)
    incoming["refProduct"] = {"type": "Relationship", "value": product_id}
    if not incoming.get("id"):
        ref_store = _extract_attr_value(incoming.get("refStore"))
        ref_shelf = _extract_attr_value(incoming.get("refShelf"))
        if isinstance(ref_store, str) and isinstance(ref_shelf, str):
            incoming["id"] = _build_inventory_item_id(product_id, ref_store, ref_shelf)
    try:
        payload = normalize_ngsi_payload(incoming, "InventoryItem")
        _ensure_product_inventory_business_rules(selector, payload, product_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    item = selector.create_entity(payload)
    if not request.is_json and not wants_json(request):
        return redirect(url_for("products.get_product", entity_id=product_id))
    return jsonify(item), 201


@products_bp.put("/<path:product_id>/inventory/<path:inventory_id>")
def update_product_inventory(product_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if not current or _extract_attr_value(current.get("refProduct")) != product_id:
        return jsonify({"error": "Inventory item not found for product"}), 404

    incoming = extract_payload(request)
    incoming["refProduct"] = {"type": "Relationship", "value": product_id}
    try:
        partial_payload = normalize_ngsi_payload(incoming, "InventoryItem", partial=True)
        merged = dict(current)
        merged.update(partial_payload)
        full_payload = normalize_ngsi_payload(merged, "InventoryItem")
        _ensure_product_inventory_business_rules(selector, full_payload, product_id, exclude_inventory_id=inventory_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    updated = selector.update_entity(inventory_id, partial_payload)
    return jsonify(updated)


@products_bp.delete("/<path:product_id>/inventory/<path:inventory_id>")
def delete_product_inventory(product_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if not current or _extract_attr_value(current.get("refProduct")) != product_id:
        return jsonify({"error": "Inventory item not found for product"}), 404
    selector.delete_entity(inventory_id)
    return "", 204


@products_bp.post("/<path:product_id>/inventory/<path:inventory_id>/update")
def update_product_inventory_form(product_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if not current or _extract_attr_value(current.get("refProduct")) != product_id:
        return redirect(url_for("products.get_product", entity_id=product_id))

    incoming = extract_payload(request)
    incoming["refProduct"] = {"type": "Relationship", "value": product_id}
    try:
        partial_payload = normalize_ngsi_payload(incoming, "InventoryItem", partial=True)
        merged = dict(current)
        merged.update(partial_payload)
        full_payload = normalize_ngsi_payload(merged, "InventoryItem")
        _ensure_product_inventory_business_rules(selector, full_payload, product_id, exclude_inventory_id=inventory_id)
        selector.update_entity(inventory_id, partial_payload)
    except ValueError:
        pass

    return redirect(url_for("products.get_product", entity_id=product_id))


@products_bp.post("/<path:product_id>/inventory/<path:inventory_id>/delete")
def delete_product_inventory_form(product_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if current and _extract_attr_value(current.get("refProduct")) == product_id:
        selector.delete_entity(inventory_id)
    return redirect(url_for("products.get_product", entity_id=product_id))
