from __future__ import annotations

from hashlib import sha256

from flask import Blueprint, jsonify, request

providers_bp = Blueprint("providers", __name__, url_prefix="/providers")


def _extract_requested_attrs(payload: dict, default_attrs: list[str]) -> list[str]:
    attrs = payload.get("attributes")
    if isinstance(attrs, list) and attrs:
        return [attr for attr in attrs if isinstance(attr, str)]
    return default_attrs


def _extract_entity_id(payload: dict) -> str:
    entities = payload.get("entities")
    if isinstance(entities, list) and entities:
        first = entities[0]
        if isinstance(first, dict):
            entity_id = first.get("id")
            if isinstance(entity_id, str) and entity_id:
                return entity_id
    return "urn:ngsi-ld:Store:UNKNOWN"


def _store_seed(store_id: str) -> int:
    digest = sha256(store_id.encode("utf-8")).digest()
    return digest[0]


def _weather_values(store_id: str) -> tuple[float, float]:
    seed = _store_seed(store_id)
    temperature = round(18.0 + (seed % 150) / 10.0, 1)
    humidity = round(35.0 + (seed % 550) / 10.0, 1)
    return temperature, humidity


def _tweets_values(store_id: str) -> list[str]:
    suffix = store_id.split(":")[-1]
    return [
        f"Store {suffix}: oferta destacada del dia",
        f"Store {suffix}: reposicion de frescos completada",
    ]


def _ngsi_query_response(store_id: str, attributes: list[dict]) -> dict:
    return {
        "contextResponses": [
            {
                "contextElement": {
                    "type": "Store",
                    "isPattern": "false",
                    "id": store_id,
                    "attributes": attributes,
                },
                "statusCode": {"code": "200", "reasonPhrase": "OK"},
            }
        ]
    }


@providers_bp.post("/weather/queryContext")
def weather_query_context():
    payload = request.get_json(silent=True) or {}
    store_id = _extract_entity_id(payload)
    requested = set(_extract_requested_attrs(payload, ["temperature", "relativeHumidity"]))
    temperature, humidity = _weather_values(store_id)

    attrs = []
    if "temperature" in requested:
        attrs.append({"name": "temperature", "type": "Number", "value": temperature})
    if "relativeHumidity" in requested:
        attrs.append({"name": "relativeHumidity", "type": "Number", "value": humidity})

    return jsonify(_ngsi_query_response(store_id, attrs))


@providers_bp.post("/tweets/queryContext")
def tweets_query_context():
    payload = request.get_json(silent=True) or {}
    store_id = _extract_entity_id(payload)
    requested = set(_extract_requested_attrs(payload, ["tweets"]))

    attrs = []
    if "tweets" in requested:
        attrs.append({"name": "tweets", "type": "StructuredValue", "value": _tweets_values(store_id)})

    return jsonify(_ngsi_query_response(store_id, attrs))


@providers_bp.get("/weather/v2/entities/<path:entity_id>")
def weather_ngsiv2(entity_id: str):
    temperature, humidity = _weather_values(entity_id)
    return jsonify(
        {
            "id": entity_id,
            "type": "Store",
            "temperature": {"type": "Float", "value": temperature},
            "relativeHumidity": {"type": "Float", "value": humidity},
        }
    )


@providers_bp.get("/tweets/v2/entities/<path:entity_id>")
def tweets_ngsiv2(entity_id: str):
    return jsonify(
        {
            "id": entity_id,
            "type": "Store",
            "tweets": {"type": "Array", "value": _tweets_values(entity_id)},
        }
    )
