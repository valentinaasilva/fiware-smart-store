from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

from routes.utils import (
    denormalize_ngsi_entities,
    maybe_denormalize_for_view,
    extract_payload,
    normalize_ngsi_payload,
    wants_json,
)

stores_bp = Blueprint("stores", __name__, url_prefix="/stores")


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


def _is_html_form_request() -> bool:
    return not request.is_json and not wants_json(request)


def _inventory_relationship_ids(item: dict) -> tuple[str | None, str | None, str | None]:
    return (
        _extract_attr_value(item.get("refStore")),
        _extract_attr_value(item.get("refShelf")),
        _extract_attr_value(item.get("refProduct")),
    )


def _ensure_inventory_business_rules(selector, inventory_payload: dict, store_id: str, exclude_inventory_id: str | None = None):
    ref_store, ref_shelf, ref_product = _inventory_relationship_ids(inventory_payload)
    if ref_store != store_id:
        raise ValueError("InventoryItem.refStore must match the store context")

    shelf = selector.get_entity(ref_shelf) if ref_shelf else None
    if not shelf:
        raise ValueError("Referenced shelf does not exist")

    shelf_ref_store = _extract_attr_value(shelf.get("refStore"))
    if shelf_ref_store != store_id:
        raise ValueError("InventoryItem.refShelf must belong to the same store")

    product = selector.get_entity(ref_product) if ref_product else None
    if not product:
        raise ValueError("Referenced product does not exist")

    items_same_store = selector.list_entities_filtered("InventoryItem", "refStore", store_id)
    for existing in items_same_store:
        if exclude_inventory_id and existing.get("id") == exclude_inventory_id:
            continue
        e_store, e_shelf, e_product = _inventory_relationship_ids(existing)
        if (e_store, e_shelf, e_product) == (ref_store, ref_shelf, ref_product):
            raise ValueError("InventoryItem with same store/shelf/product already exists")

    shelf_capacity = _as_int(shelf.get("maxCapacity"), default=0)
    incoming_shelf_count = _as_int(inventory_payload.get("shelfCount"), default=0)
    current_total = 0
    for existing in items_same_store:
        if exclude_inventory_id and existing.get("id") == exclude_inventory_id:
            continue
        _, e_shelf, _ = _inventory_relationship_ids(existing)
        if e_shelf == ref_shelf:
            current_total += _as_int(existing.get("shelfCount"), default=0)
    if shelf_capacity > 0 and (current_total + incoming_shelf_count) > shelf_capacity:
        raise ValueError("Shelf capacity exceeded")


def _build_store_detail_context(store_id: str) -> dict:
    selector = current_app.extensions["data_selector"]
    shelves = selector.list_entities_filtered("Shelf", "refStore", store_id)
    inventory_items = selector.list_entities_filtered("InventoryItem", "refStore", store_id)
    products = selector.list_entities("Product")

    product_by_id = {product.get("id"): product for product in products}
    shelf_by_id = {shelf.get("id"): shelf for shelf in shelves}

    denorm_shelves = denormalize_ngsi_entities(shelves)
    denorm_inventory = denormalize_ngsi_entities(inventory_items)

    products_in_store = {}
    for item in denorm_inventory:
        product_id = item.get("refProduct")
        if not product_id:
            continue
        product = product_by_id.get(product_id)
        if not product:
            continue
        denorm_product = maybe_denormalize_for_view(product)
        key = product_id
        if key not in products_in_store:
            products_in_store[key] = {
                "id": product_id,
                "name": denorm_product.get("name", product_id),
                "stockCount": 0,
                "shelfCount": 0,
            }
        products_in_store[key]["stockCount"] += _as_int(item.get("stockCount"), 0)
        products_in_store[key]["shelfCount"] += _as_int(item.get("shelfCount"), 0)

    shelf_rows = []
    for shelf in denorm_shelves:
        shelf_id = shelf.get("id")
        capacity = _as_int(shelf.get("maxCapacity"), 0)
        shelf_total = sum(_as_int(item.get("shelfCount"), 0) for item in denorm_inventory if item.get("refShelf") == shelf_id)
        fill_percent = int((shelf_total * 100 / capacity)) if capacity > 0 else 0
        shelf_rows.append(
            {
                **shelf,
                "currentLoad": shelf_total,
                "fillPercent": min(fill_percent, 100),
            }
        )

    inventory_rows = []
    for item in denorm_inventory:
        product = product_by_id.get(item.get("refProduct"))
        shelf_raw = shelf_by_id.get(item.get("refShelf"))
        inventory_rows.append(
            {
                **item,
                "productName": maybe_denormalize_for_view(product).get("name") if product else item.get("refProduct"),
                "shelfName": maybe_denormalize_for_view(shelf_raw).get("name") if shelf_raw else item.get("refShelf"),
            }
        )

    return {
        "shelves": sorted(shelf_rows, key=lambda row: row.get("id", "")),
        "inventory_items": sorted(inventory_rows, key=lambda row: row.get("id", "")),
        "products_in_store": sorted(products_in_store.values(), key=lambda row: row.get("name", "")),
        "all_products": sorted([maybe_denormalize_for_view(product) for product in products], key=lambda row: row.get("name", "")),
    }


@stores_bp.get("/")
def list_stores():
    stores = current_app.extensions["data_selector"].list_entities("Store")
    if wants_json(request):
        return jsonify(stores)
    return render_template("stores/list.html", stores=denormalize_ngsi_entities(stores))


@stores_bp.get("")
def list_stores_no_slash():
    return list_stores()


@stores_bp.get("/new")
def new_store_page():
    return render_template("stores/form.html", store=None)


@stores_bp.post("/new")
def create_store_form():
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Store")
        current_app.extensions["data_selector"].create_entity(payload)
    except ValueError:
        pass
    return redirect(url_for("stores.list_stores"))


@stores_bp.get("/edit/<path:entity_id>")
def edit_store_page(entity_id: str):
    store = current_app.extensions["data_selector"].get_entity(entity_id)
    if not store:
        return redirect(url_for("stores.list_stores"))
    return render_template("stores/form.html", store=maybe_denormalize_for_view(store))


@stores_bp.post("/edit/<path:entity_id>")
def update_store_form(entity_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(entity_id)
    if current:
        incoming = extract_payload(request)
        incoming.pop("id", None)
        try:
            payload = normalize_ngsi_payload(incoming, "Store", partial=True)
            selector.update_entity(entity_id, payload)
        except ValueError:
            pass
    return redirect(url_for("stores.list_stores"))


@stores_bp.post("/delete/<path:entity_id>")
def delete_store_form(entity_id: str):
    selector = current_app.extensions["data_selector"]
    has_shelves = selector.list_entities_filtered("Shelf", "refStore", entity_id)
    has_inventory = selector.list_entities_filtered("InventoryItem", "refStore", entity_id)
    has_employees = selector.list_entities_filtered("Employee", "refStore", entity_id)
    if not has_shelves and not has_inventory and not has_employees:
        selector.delete_entity(entity_id)
    return redirect(url_for("stores.list_stores"))


@stores_bp.get("/<path:entity_id>")
def get_store(entity_id: str):
    selector = current_app.extensions["data_selector"]
    store = selector.get_entity(entity_id)
    if not store:
        return jsonify({"error": "Store not found"}), 404
    context = _build_store_detail_context(entity_id)
    if wants_json(request):
        return jsonify(store)
    return render_template("stores/detail.html", store=maybe_denormalize_for_view(store), **context)


@stores_bp.post("/")
def create_store():
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Store")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    store = current_app.extensions["data_selector"].create_entity(payload)
    return jsonify(store), 201


@stores_bp.put("/<path:entity_id>")
def update_store(entity_id: str):
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Store", partial=True)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    store = current_app.extensions["data_selector"].update_entity(entity_id, payload)
    if not store:
        return jsonify({"error": "Store not found"}), 404
    return jsonify(store)


@stores_bp.delete("/<path:entity_id>")
def delete_store(entity_id: str):
    deleted = current_app.extensions["data_selector"].delete_entity(entity_id)
    if not deleted:
        return jsonify({"error": "Store not found"}), 404
    return "", 204


@stores_bp.get("/<path:store_id>/shelves")
def list_store_shelves(store_id: str):
    shelves = current_app.extensions["data_selector"].list_entities_filtered("Shelf", "refStore", store_id)
    return jsonify(shelves)


@stores_bp.post("/<path:store_id>/shelves")
def create_store_shelf(store_id: str):
    selector = current_app.extensions["data_selector"]
    if not selector.get_entity(store_id):
        return jsonify({"error": "Store not found"}), 404

    incoming = extract_payload(request)
    incoming["refStore"] = {"type": "Relationship", "value": store_id}
    try:
        payload = normalize_ngsi_payload(incoming, "Shelf")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    shelf = selector.create_entity(payload)
    if _is_html_form_request():
        return redirect(url_for("stores.get_store", entity_id=store_id))
    return jsonify(shelf), 201


@stores_bp.put("/<path:store_id>/shelves/<path:shelf_id>")
def update_store_shelf(store_id: str, shelf_id: str):
    selector = current_app.extensions["data_selector"]
    shelf = selector.get_entity(shelf_id)
    if not shelf or _extract_attr_value(shelf.get("refStore")) != store_id:
        return jsonify({"error": "Shelf not found for store"}), 404

    incoming = extract_payload(request)
    incoming["refStore"] = {"type": "Relationship", "value": store_id}
    try:
        payload = normalize_ngsi_payload(incoming, "Shelf", partial=True)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    updated = selector.update_entity(shelf_id, payload)
    return jsonify(updated)


@stores_bp.delete("/<path:store_id>/shelves/<path:shelf_id>")
def delete_store_shelf(store_id: str, shelf_id: str):
    selector = current_app.extensions["data_selector"]
    shelf = selector.get_entity(shelf_id)
    if not shelf or _extract_attr_value(shelf.get("refStore")) != store_id:
        return jsonify({"error": "Shelf not found for store"}), 404

    inventory_items = selector.list_entities_filtered("InventoryItem", "refShelf", shelf_id)
    if inventory_items:
        return jsonify({"error": "Cannot delete shelf with inventory items"}), 409

    selector.delete_entity(shelf_id)
    return "", 204


@stores_bp.post("/<path:store_id>/shelves/<path:shelf_id>/update")
def update_store_shelf_form(store_id: str, shelf_id: str):
    selector = current_app.extensions["data_selector"]
    shelf = selector.get_entity(shelf_id)
    if not shelf or _extract_attr_value(shelf.get("refStore")) != store_id:
        return redirect(url_for("stores.get_store", entity_id=store_id))

    incoming = extract_payload(request)
    incoming["refStore"] = {"type": "Relationship", "value": store_id}
    try:
        payload = normalize_ngsi_payload(incoming, "Shelf", partial=True)
        selector.update_entity(shelf_id, payload)
    except ValueError:
        pass
    return redirect(url_for("stores.get_store", entity_id=store_id))


@stores_bp.post("/<path:store_id>/shelves/<path:shelf_id>/delete")
def delete_store_shelf_form(store_id: str, shelf_id: str):
    selector = current_app.extensions["data_selector"]
    inventory_items = selector.list_entities_filtered("InventoryItem", "refShelf", shelf_id)
    if not inventory_items:
        selector.delete_entity(shelf_id)
    return redirect(url_for("stores.get_store", entity_id=store_id))


@stores_bp.get("/<path:store_id>/inventory")
def list_store_inventory(store_id: str):
    inventory_items = current_app.extensions["data_selector"].list_entities_filtered("InventoryItem", "refStore", store_id)
    return jsonify(inventory_items)


@stores_bp.post("/<path:store_id>/inventory")
def create_store_inventory(store_id: str):
    selector = current_app.extensions["data_selector"]
    if not selector.get_entity(store_id):
        return jsonify({"error": "Store not found"}), 404

    incoming = extract_payload(request)
    incoming["refStore"] = {"type": "Relationship", "value": store_id}
    try:
        payload = normalize_ngsi_payload(incoming, "InventoryItem")
        _ensure_inventory_business_rules(selector, payload, store_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    item = selector.create_entity(payload)
    if _is_html_form_request():
        return redirect(url_for("stores.get_store", entity_id=store_id))
    return jsonify(item), 201


@stores_bp.put("/<path:store_id>/inventory/<path:inventory_id>")
def update_store_inventory(store_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if not current or _extract_attr_value(current.get("refStore")) != store_id:
        return jsonify({"error": "Inventory item not found for store"}), 404

    incoming = extract_payload(request)
    incoming["refStore"] = {"type": "Relationship", "value": store_id}
    try:
        partial_payload = normalize_ngsi_payload(incoming, "InventoryItem", partial=True)
        merged = dict(current)
        merged.update(partial_payload)
        full_payload = normalize_ngsi_payload(merged, "InventoryItem")
        _ensure_inventory_business_rules(selector, full_payload, store_id, exclude_inventory_id=inventory_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    updated = selector.update_entity(inventory_id, partial_payload)
    return jsonify(updated)


@stores_bp.delete("/<path:store_id>/inventory/<path:inventory_id>")
def delete_store_inventory(store_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if not current or _extract_attr_value(current.get("refStore")) != store_id:
        return jsonify({"error": "Inventory item not found for store"}), 404
    selector.delete_entity(inventory_id)
    return "", 204


@stores_bp.post("/<path:store_id>/inventory/<path:inventory_id>/update")
def update_store_inventory_form(store_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if not current or _extract_attr_value(current.get("refStore")) != store_id:
        return redirect(url_for("stores.get_store", entity_id=store_id))

    incoming = extract_payload(request)
    incoming["refStore"] = {"type": "Relationship", "value": store_id}
    try:
        partial_payload = normalize_ngsi_payload(incoming, "InventoryItem", partial=True)
        merged = dict(current)
        merged.update(partial_payload)
        full_payload = normalize_ngsi_payload(merged, "InventoryItem")
        _ensure_inventory_business_rules(selector, full_payload, store_id, exclude_inventory_id=inventory_id)
        selector.update_entity(inventory_id, partial_payload)
    except ValueError:
        pass
    return redirect(url_for("stores.get_store", entity_id=store_id))


@stores_bp.post("/<path:store_id>/inventory/<path:inventory_id>/delete")
def delete_store_inventory_form(store_id: str, inventory_id: str):
    selector = current_app.extensions["data_selector"]
    current = selector.get_entity(inventory_id)
    if current and _extract_attr_value(current.get("refStore")) == store_id:
        selector.delete_entity(inventory_id)
    return redirect(url_for("stores.get_store", entity_id=store_id))
