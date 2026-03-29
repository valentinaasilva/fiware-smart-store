from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

from routes.utils import (
    denormalize_ngsi_entities,
    maybe_denormalize_for_view,
    extract_payload,
    normalize_ngsi_payload,
    wants_json,
)

employees_bp = Blueprint("employees", __name__, url_prefix="/employees")


@employees_bp.get("/")
def list_employees():
    employees = current_app.extensions["data_selector"].list_entities("Employee")
    if wants_json(request):
        return jsonify(employees)
    return render_template("employees/list.html", employees=denormalize_ngsi_entities(employees))


@employees_bp.get("")
def list_employees_no_slash():
    return list_employees()


@employees_bp.get("/new")
def new_employee_page():
    stores = denormalize_ngsi_entities(current_app.extensions["data_selector"].list_entities("Store"))
    return render_template("employees/form.html", employee=None, stores=stores)


@employees_bp.post("/new")
def create_employee_form():
    data = extract_payload(request)
    raw_skills = data.get("skills", "")
    data["skills"] = [skill.strip() for skill in str(raw_skills).split(",") if skill.strip()]
    try:
        payload = normalize_ngsi_payload(data, "Employee")
        current_app.extensions["data_selector"].create_entity(payload)
    except ValueError:
        pass
    return redirect(url_for("employees.list_employees"))


@employees_bp.get("/edit/<path:entity_id>")
def edit_employee_page(entity_id: str):
    selector = current_app.extensions["data_selector"]
    employee = selector.get_entity(entity_id)
    if not employee:
        return redirect(url_for("employees.list_employees"))
    stores = denormalize_ngsi_entities(selector.list_entities("Store"))
    denorm = maybe_denormalize_for_view(employee)
    if isinstance(denorm.get("skills"), list):
        denorm["skills"] = ", ".join(denorm["skills"])
    return render_template("employees/form.html", employee=denorm, stores=stores)


@employees_bp.post("/edit/<path:entity_id>")
def update_employee_form(entity_id: str):
    selector = current_app.extensions["data_selector"]
    if selector.get_entity(entity_id):
        data = extract_payload(request)
        data.pop("id", None)
        raw_skills = data.get("skills", "")
        data["skills"] = [skill.strip() for skill in str(raw_skills).split(",") if skill.strip()]
        try:
            payload = normalize_ngsi_payload(data, "Employee", partial=True)
            selector.update_entity(entity_id, payload)
        except ValueError:
            pass
    return redirect(url_for("employees.list_employees"))


@employees_bp.post("/delete/<path:entity_id>")
def delete_employee_form(entity_id: str):
    current_app.extensions["data_selector"].delete_entity(entity_id)
    return redirect(url_for("employees.list_employees"))


@employees_bp.get("/<path:entity_id>")
def get_employee(entity_id: str):
    employee = current_app.extensions["data_selector"].get_entity(entity_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    if wants_json(request):
        return jsonify(employee)
    return render_template("employees/detail.html", employee=maybe_denormalize_for_view(employee))


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
    try:
        payload = normalize_ngsi_payload(extract_payload(request), "Employee", partial=True)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
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
