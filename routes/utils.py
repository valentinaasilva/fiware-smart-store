from __future__ import annotations

from flask import Request


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


def normalize_ngsi_payload(data: dict, entity_type: str) -> dict:
    payload = data.copy()
    payload.setdefault("type", entity_type)
    if "id" not in payload or not payload["id"]:
        raise ValueError("Field 'id' is required")
    return payload
