from flask import Blueprint, current_app, jsonify, render_template, request

from routes.utils import extract_payload, normalize_ngsi_payload, wants_json

employees_bp = Blueprint("employees", __name__, url_prefix="/employees")


@employees_bp.get("/")
def list_employees():
    employees = current_app.extensions["data_selector"].list_entities("Employee")
    if wants_json(request):
        return jsonify(employees)
    return render_template("employees/list.html", employees=employees)


@employees_bp.get("")
def list_employees_no_slash():
    return list_employees()


@employees_bp.get("/<path:entity_id>")
def get_employee(entity_id: str):
    employee = current_app.extensions["data_selector"].get_entity(entity_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    if wants_json(request):
        return jsonify(employee)
    return render_template("employees/detail.html", employee=employee)


@employees_bp.post("/")
def create_employee():
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Employee")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    employee = current_app.extensions["data_selector"].create_entity(payload)
    return jsonify(employee), 201


@employees_bp.put("/<path:entity_id>")
def update_employee(entity_id: str):
    payload = extract_payload(request)
    employee = current_app.extensions["data_selector"].update_entity(entity_id, payload)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(employee)


@employees_bp.delete("/<path:entity_id>")
def delete_employee(entity_id: str):
    deleted = current_app.extensions["data_selector"].delete_entity(entity_id)
    if not deleted:
        return jsonify({"error": "Employee not found"}), 404
    return "", 204
