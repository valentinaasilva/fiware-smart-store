from flask import Blueprint, current_app, jsonify, render_template, request

from routes.utils import (
    denormalize_ngsi_entities,
    maybe_denormalize_for_view,
    extract_payload,
    normalize_ngsi_payload,
    wants_json,
)

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.get("/")
def list_products():
    products = current_app.extensions["data_selector"].list_entities("Product")
    if wants_json(request):
        return jsonify(products)
    return render_template("products/list.html", products=denormalize_ngsi_entities(products))


@products_bp.get("")
def list_products_no_slash():
    return list_products()


@products_bp.get("/<path:entity_id>")
def get_product(entity_id: str):
    product = current_app.extensions["data_selector"].get_entity(entity_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if wants_json(request):
        return jsonify(product)
    return render_template("products/detail.html", product=maybe_denormalize_for_view(product))


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
    deleted = current_app.extensions["data_selector"].delete_entity(entity_id)
    if not deleted:
        return jsonify({"error": "Product not found"}), 404
    return "", 204
