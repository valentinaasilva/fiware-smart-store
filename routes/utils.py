from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urlparse

from flask import Request


NGSI_ATTR_TYPES: dict[str, dict[str, str]] = {
    "Store": {
        "name": "Text",
        "address": "PostalAddress",
        "location": "geo:json",
        "countryCode": "Text",
        "capacity": "Integer",
        "telephone": "Text",
        "url": "Text",
        "image": "Text",
        "description": "Text",
    },
    "Product": {
        "name": "Text",
        "size": "Text",
        "category": "Text",
        "price": "Float",
        "color": "Text",
        "originCountry": "Text",
        "image": "Text",
    },
    "Employee": {
        "name": "Text",
        "image": "Text",
        "salary": "Float",
        "role": "Text",
        "refStore": "Relationship",
        "category": "Text",
        "email": "Text",
        "skills": "Array",
        "dateOfContract": "DateTime",
        "username": "Text",
        "password": "Text",
    },
    "Shelf": {
        "name": "Text",
        "location": "geo:json",
        "maxCapacity": "Integer",
        "refStore": "Relationship",
    },
    "InventoryItem": {
        "refStore": "Relationship",
        "refShelf": "Relationship",
        "refProduct": "Relationship",
        "stockCount": "Integer",
        "shelfCount": "Integer",
    },
}

PRODUCT_SIZES = {"S", "M", "L", "XL"}
PRODUCT_CATEGORIES = {"Lacteos", "Despensa", "Frescos", "Limpieza", "Bebidas", "Panaderia"}
EMPLOYEE_SKILLS_ENUM = {"MachineryDriving", "WritingReports", "CustomerRelationships"}
EMPLOYEE_USERNAME_MIN = 4
EMPLOYEE_USERNAME_MAX = 32
STORE_DESCRIPTION_MAX = 2000
STORE_TEMPERATURE_MIN = -30.0
STORE_TEMPERATURE_MAX = 60.0
STORE_HUMIDITY_MIN = 0.0
STORE_HUMIDITY_MAX = 100.0

HEX_COLOR_RE = re.compile(r"^#[0-9A-F]{6}$")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def wants_json(request: Request) -> bool:
    if request.args.get("format") == "json":
        return True
    accept = request.headers.get("Accept", "")
    return "application/json" in accept


def extract_payload(request: Request) -> dict:
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict(flat=True)
    return data


def _is_ngsi_attr(value: object) -> bool:
    return isinstance(value, dict) and "type" in value and "value" in value


def _unwrap_value(value: object) -> object:
    if _is_ngsi_attr(value):
        return value["value"]
    return value


def _to_ngsi_attr(entity_type: str, field: str, value: object) -> object:
    if _is_ngsi_attr(value):
        return value
    ngsi_type = NGSI_ATTR_TYPES.get(entity_type, {}).get(field)
    if not ngsi_type:
        return value
    return {"type": ngsi_type, "value": value}


def _is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _validate_store(payload: dict, partial: bool) -> None:
    country = _unwrap_value(payload.get("countryCode"))
    if country is not None and (not isinstance(country, str) or len(country) != 2 or country.upper() != country):
        raise ValueError("Store.countryCode must be ISO alpha-2")

    image = _unwrap_value(payload.get("image"))
    if image is not None and (not isinstance(image, str) or not _is_valid_url(image)):
        raise ValueError("Store.image must be a valid http/https URL")

    url = _unwrap_value(payload.get("url"))
    if url is not None and (not isinstance(url, str) or not _is_valid_url(url)):
        raise ValueError("Store.url must be a valid http/https URL")

    telephone = _unwrap_value(payload.get("telephone"))
    if telephone is not None:
        if not isinstance(telephone, str) or not telephone.strip():
            raise ValueError("Store.telephone must be a non-empty string")
        # Basic international phone pattern validation: +XX-XXX-XXXXXX or variations
        if not re.match(r"^\+?[0-9\-\s\(\)]+$", telephone):
            raise ValueError("Store.telephone must be a valid international phone format")

    capacity = _unwrap_value(payload.get("capacity"))
    if capacity is not None:
        try:
            numeric_capacity = float(capacity)
        except (TypeError, ValueError) as exc:
            raise ValueError("Store.capacity must be numeric") from exc
        if numeric_capacity <= 0:
            raise ValueError("Store.capacity must be > 0")

    description = _unwrap_value(payload.get("description"))
    if description is not None:
        if not isinstance(description, str):
            raise ValueError("Store.description must be a string")
        if len(description) > STORE_DESCRIPTION_MAX:
            raise ValueError(f"Store.description must be <= {STORE_DESCRIPTION_MAX} characters")

    temperature = _unwrap_value(payload.get("temperature"))
    if temperature is not None:
        try:
            numeric_temperature = float(temperature)
        except (TypeError, ValueError) as exc:
            raise ValueError("Store.temperature must be numeric") from exc
        if numeric_temperature < STORE_TEMPERATURE_MIN or numeric_temperature > STORE_TEMPERATURE_MAX:
            raise ValueError(f"Store.temperature must be between {STORE_TEMPERATURE_MIN} and {STORE_TEMPERATURE_MAX}")

    humidity = _unwrap_value(payload.get("relativeHumidity"))
    if humidity is not None:
        try:
            numeric_humidity = float(humidity)
        except (TypeError, ValueError) as exc:
            raise ValueError("Store.relativeHumidity must be numeric") from exc
        if numeric_humidity < STORE_HUMIDITY_MIN or numeric_humidity > STORE_HUMIDITY_MAX:
            raise ValueError(f"Store.relativeHumidity must be between {STORE_HUMIDITY_MIN} and {STORE_HUMIDITY_MAX}")


def _validate_product(payload: dict, partial: bool) -> None:
    size = _unwrap_value(payload.get("size"))
    if size is not None and size not in PRODUCT_SIZES:
        raise ValueError("Product.size must be one of S, M, L, XL")

    price = _unwrap_value(payload.get("price"))
    if price is not None:
        try:
            numeric_price = float(price)
        except (TypeError, ValueError) as exc:
            raise ValueError("Product.price must be numeric") from exc
        if numeric_price < 0:
            raise ValueError("Product.price must be >= 0")

    color = _unwrap_value(payload.get("color"))
    if color is not None:
        if not isinstance(color, str) or not HEX_COLOR_RE.match(color):
            raise ValueError("Product.color must match #RRGGBB")

    origin_country = _unwrap_value(payload.get("originCountry"))
    if origin_country is not None:
        if not isinstance(origin_country, str) or len(origin_country) != 2 or origin_country.upper() != origin_country:
            raise ValueError("Product.originCountry must be ISO alpha-2")

    image = _unwrap_value(payload.get("image"))
    if image is not None and (not isinstance(image, str) or not _is_valid_url(image)):
        raise ValueError("Product.image must be a valid http/https URL")

    category = _unwrap_value(payload.get("category"))
    if category is not None and category not in PRODUCT_CATEGORIES:
        raise ValueError("Product.category must be one of Lacteos, Despensa, Frescos, Limpieza, Bebidas, Panaderia")


def _validate_employee(payload: dict, partial: bool) -> None:
    required_fields = ("name", "image", "salary", "role", "refStore")
    if not partial:
        missing = [field for field in required_fields if field not in payload]
        if missing:
            raise ValueError(f"Employee missing required fields: {', '.join(missing)}")

    name = _unwrap_value(payload.get("name"))
    if name is not None and (not isinstance(name, str) or not name.strip()):
        raise ValueError("Employee.name must be a non-empty string")

    image = _unwrap_value(payload.get("image"))
    if image is not None and (not isinstance(image, str) or not _is_valid_url(image)):
        raise ValueError("Employee.image must be a valid http/https URL")

    salary = _unwrap_value(payload.get("salary"))
    if salary is not None:
        try:
            numeric_salary = float(salary)
        except (TypeError, ValueError) as exc:
            raise ValueError("Employee.salary must be numeric") from exc
        if numeric_salary < 0:
            raise ValueError("Employee.salary must be >= 0")

    role = _unwrap_value(payload.get("role"))
    if role is not None and (not isinstance(role, str) or not role.strip()):
        raise ValueError("Employee.role must be a non-empty string")

    ref_store = payload.get("refStore")
    if ref_store is not None:
        if _is_ngsi_attr(ref_store):
            if ref_store.get("type") != "Relationship":
                raise ValueError("Employee.refStore must be a Relationship")
            ref_store_value = ref_store.get("value")
        else:
            ref_store_value = ref_store

        if not isinstance(ref_store_value, str) or not ref_store_value.startswith("urn:ngsi-ld:Store:"):
            raise ValueError("Employee.refStore must point to a Store URN")

    email = _unwrap_value(payload.get("email"))
    if email is not None:
        if not isinstance(email, str):
            raise ValueError("Employee.email must be a string")
        if not EMAIL_RE.match(email):
            raise ValueError("Employee.email must be a valid email format")

    date_of_contract = _unwrap_value(payload.get("dateOfContract"))
    if date_of_contract is not None:
        if isinstance(date_of_contract, str):
            try:
                # Accept ISO-8601 format with or without timezone
                if date_of_contract.endswith("Z"):
                    datetime.fromisoformat(date_of_contract.replace("Z", "+00:00"))
                else:
                    datetime.fromisoformat(date_of_contract)
            except (ValueError, TypeError) as exc:
                raise ValueError("Employee.dateOfContract must be ISO-8601 format") from exc
        else:
            raise ValueError("Employee.dateOfContract must be a string in ISO-8601 format")

    skills = _unwrap_value(payload.get("skills"))
    if skills is not None:
        if not isinstance(skills, list) or not skills:
            raise ValueError("Employee.skills must be a non-empty array")
        for skill in skills:
            if not isinstance(skill, str) or skill not in EMPLOYEE_SKILLS_ENUM:
                raise ValueError(f"Employee.skills must only contain: {', '.join(EMPLOYEE_SKILLS_ENUM)}")

    username = _unwrap_value(payload.get("username"))
    if username is not None:
        if not isinstance(username, str):
            raise ValueError("Employee.username must be a string")
        if len(username) < EMPLOYEE_USERNAME_MIN or len(username) > EMPLOYEE_USERNAME_MAX:
            raise ValueError(f"Employee.username must be between {EMPLOYEE_USERNAME_MIN} and {EMPLOYEE_USERNAME_MAX} characters")

    password = _unwrap_value(payload.get("password"))
    if password is not None:
        if not isinstance(password, str) or not password:
            raise ValueError("Employee.password must be a non-empty string")


def _extract_relationship_urn(value: object, field_name: str, expected_prefix: str) -> str | None:
    if value is None:
        return None
    if _is_ngsi_attr(value):
        if value.get("type") != "Relationship":
            raise ValueError(f"{field_name} must be a Relationship")
        rel_value = value.get("value")
    else:
        rel_value = value
    if not isinstance(rel_value, str) or not rel_value.startswith(expected_prefix):
        raise ValueError(f"{field_name} must point to a valid URN")
    return rel_value


def _validate_shelf(payload: dict, partial: bool) -> None:
    if not partial and "refStore" not in payload:
        raise ValueError("Shelf.refStore is required")

    _extract_relationship_urn(payload.get("refStore"), "Shelf.refStore", "urn:ngsi-ld:Store:")

    max_capacity = _unwrap_value(payload.get("maxCapacity"))
    if max_capacity is not None:
        try:
            parsed = int(max_capacity)
        except (TypeError, ValueError) as exc:
            raise ValueError("Shelf.maxCapacity must be an integer") from exc
        if parsed <= 0:
            raise ValueError("Shelf.maxCapacity must be > 0")


def _validate_inventory_item(payload: dict, partial: bool) -> None:
    required_fields = ("refStore", "refShelf", "refProduct", "stockCount", "shelfCount")
    if not partial:
        missing = [field for field in required_fields if field not in payload]
        if missing:
            raise ValueError(f"InventoryItem missing required fields: {', '.join(missing)}")

    _extract_relationship_urn(payload.get("refStore"), "InventoryItem.refStore", "urn:ngsi-ld:Store:")
    _extract_relationship_urn(payload.get("refShelf"), "InventoryItem.refShelf", "urn:ngsi-ld:Shelf:")
    _extract_relationship_urn(payload.get("refProduct"), "InventoryItem.refProduct", "urn:ngsi-ld:Product:")

    stock_count = _unwrap_value(payload.get("stockCount"))
    shelf_count = _unwrap_value(payload.get("shelfCount"))

    parsed_stock = None
    parsed_shelf = None
    if stock_count is not None:
        try:
            parsed_stock = int(stock_count)
        except (TypeError, ValueError) as exc:
            raise ValueError("InventoryItem.stockCount must be an integer") from exc
        if parsed_stock < 0:
            raise ValueError("InventoryItem.stockCount must be >= 0")

    if shelf_count is not None:
        try:
            parsed_shelf = int(shelf_count)
        except (TypeError, ValueError) as exc:
            raise ValueError("InventoryItem.shelfCount must be an integer") from exc
        if parsed_shelf < 0:
            raise ValueError("InventoryItem.shelfCount must be >= 0")

    if parsed_stock is not None and parsed_shelf is not None and parsed_shelf > parsed_stock:
        raise ValueError("InventoryItem.shelfCount must be <= InventoryItem.stockCount")


def normalize_ngsi_payload(data: dict, entity_type: str, partial: bool = False) -> dict:
    payload = data.copy()
    if not partial:
        payload.setdefault("type", entity_type)

    if not partial and ("id" not in payload or not payload["id"]):
        raise ValueError("Field 'id' is required")

    if not partial and not str(payload["id"]).startswith(f"urn:ngsi-ld:{entity_type}:"):
        raise ValueError(f"{entity_type}.id must start with urn:ngsi-ld:{entity_type}:")

    if payload.get("type") and payload["type"] != entity_type:
        raise ValueError(f"Field 'type' must be '{entity_type}'")

    # Backward compatibility for legacy product payloads.
    if entity_type == "Product" and "origin" in payload and "originCountry" not in payload:
        payload["originCountry"] = payload.pop("origin")

    normalized: dict = {}
    for key, value in payload.items():
        if key in {"id", "type"}:
            normalized[key] = value
            continue
        normalized[key] = _to_ngsi_attr(entity_type, key, value)

    if entity_type == "Store":
        _validate_store(normalized, partial)
    elif entity_type == "Product":
        _validate_product(normalized, partial)
    elif entity_type == "Employee":
        _validate_employee(normalized, partial)
    elif entity_type == "Shelf":
        _validate_shelf(normalized, partial)
    elif entity_type == "InventoryItem":
        _validate_inventory_item(normalized, partial)

    if not partial:
        normalized.setdefault("type", entity_type)
        normalized.setdefault("id", payload.get("id"))

    return normalized


def denormalize_ngsi_entity(entity: dict) -> dict:
    denormalized = {}
    for key, value in entity.items():
        if key in {"id", "type"}:
            denormalized[key] = value
        else:
            denormalized[key] = _unwrap_value(value)
    return denormalized


def denormalize_ngsi_entities(entities: list[dict]) -> list[dict]:
    return [denormalize_ngsi_entity(entity) for entity in entities]


def is_ngsi_entity(entity: dict) -> bool:
    for key, value in entity.items():
        if key in {"id", "type"}:
            continue
        if _is_ngsi_attr(value):
            return True
    return False


def maybe_denormalize_for_view(entity: dict) -> dict:
    if is_ngsi_entity(entity):
        return denormalize_ngsi_entity(entity)
    return entity
