from flask import Blueprint, current_app, jsonify, render_template, request

from routes.utils import (
    denormalize_ngsi_entities,
    maybe_denormalize_for_view,
    extract_payload,
    normalize_ngsi_payload,
    wants_json,
)

stores_bp = Blueprint("stores", __name__, url_prefix="/stores")


@stores_bp.get("/")
def list_stores():
    stores = current_app.extensions["data_selector"].list_entities("Store")
    if wants_json(request):
        return jsonify(stores)
    return render_template("stores/list.html", stores=denormalize_ngsi_entities(stores))


@stores_bp.get("")
def list_stores_no_slash():
    return list_stores()


@stores_bp.get("/<path:entity_id>")
def get_store(entity_id: str):
    store = current_app.extensions["data_selector"].get_entity(entity_id)
    if not store:
        return jsonify({"error": "Store not found"}), 404
    if wants_json(request):
        return jsonify(store)
    return render_template("stores/detail.html", store=maybe_denormalize_for_view(store))


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
