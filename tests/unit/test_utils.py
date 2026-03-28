from routes.utils import extract_payload, normalize_ngsi_payload, wants_json


def test_wants_json_from_query(app):
    with app.test_request_context("/stores?format=json") as request_ctx:
        assert wants_json(request_ctx.request) is True


def test_wants_json_from_accept_header(app):
    with app.test_request_context("/stores", headers={"Accept": "application/json"}) as request_ctx:
        assert wants_json(request_ctx.request) is True


def test_wants_json_default_false(app):
    with app.test_request_context("/stores") as request_ctx:
        assert wants_json(request_ctx.request) is False


def test_extract_payload_json(app):
    with app.test_request_context("/stores", method="POST", json={"id": "s1"}) as request_ctx:
        assert extract_payload(request_ctx.request) == {"id": "s1"}


def test_extract_payload_form(app):
    with app.test_request_context("/stores", method="POST", data={"id": "s1"}) as request_ctx:
        assert extract_payload(request_ctx.request) == {"id": "s1"}


def test_normalize_ngsi_payload_sets_type():
    payload = normalize_ngsi_payload({"id": "urn:ngsi-ld:Store:001"}, "Store")
    assert payload["type"] == "Store"


def test_normalize_ngsi_payload_requires_id():
    try:
        normalize_ngsi_payload({}, "Store")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "id" in str(exc)
