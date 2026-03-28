from flask import Blueprint, current_app, jsonify, request

from routes.utils import extract_payload, normalize_ngsi_payload

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.get("/")
def list_inventory_items():
    inventory = current_app.extensions["data_selector"].list_entities("InventoryItem")
    return jsonify(inventory)


@inventory_bp.post("/")
def create_inventory_item():
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "InventoryItem")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    item = current_app.extensions["data_selector"].create_entity(payload)
    return jsonify(item), 201


@inventory_bp.put("/<path:entity_id>")
def update_inventory_item(entity_id: str):
    payload = extract_payload(request)
    item = current_app.extensions["data_selector"].update_entity(entity_id, payload)
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
    return jsonify(item)


@inventory_bp.delete("/<path:entity_id>")
def delete_inventory_item(entity_id: str):
    deleted = current_app.extensions["data_selector"].delete_entity(entity_id)
    if not deleted:
        return jsonify({"error": "Inventory item not found"}), 404
    return "", 204
