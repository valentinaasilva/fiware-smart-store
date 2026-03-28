from routes.utils import (
    denormalize_ngsi_entity,
    extract_payload,
    normalize_ngsi_payload,
    wants_json,
)


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


def test_normalize_store_payload_wraps_image():
    payload = normalize_ngsi_payload(
        {
            "id": "urn:ngsi-ld:Store:001",
            "name": "Store 1",
            "image": "https://example.com/store.png",
        },
        "Store",
    )
    assert payload["name"]["type"] == "Text"
    assert payload["image"]["value"] == "https://example.com/store.png"


def test_normalize_product_payload_wraps_origin_country_and_price():
    payload = normalize_ngsi_payload(
        {
            "id": "urn:ngsi-ld:Product:001",
            "name": "Product 1",
            "price": 9.99,
            "size": "M",
            "color": "#FF00AA",
            "originCountry": "ES",
        },
        "Product",
    )
    assert payload["price"]["type"] == "Float"
    assert payload["originCountry"]["value"] == "ES"


def test_normalize_product_payload_accepts_legacy_origin_field():
    payload = normalize_ngsi_payload(
        {
            "id": "urn:ngsi-ld:Product:001",
            "name": "Product 1",
            "price": 1.0,
            "size": "S",
            "color": "#FFFFFF",
            "origin": "DE",
        },
        "Product",
    )
    assert payload["originCountry"]["value"] == "DE"


def test_normalize_product_payload_rejects_invalid_color():
    try:
        normalize_ngsi_payload(
            {
                "id": "urn:ngsi-ld:Product:001",
                "name": "Product 1",
                "price": 1.0,
                "size": "S",
                "color": "red",
            },
            "Product",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "color" in str(exc)


def test_denormalize_ngsi_entity_unwraps_attributes():
    entity = {
        "id": "urn:ngsi-ld:Product:001",
        "type": "Product",
        "name": {"type": "Text", "value": "Product 1"},
        "price": {"type": "Float", "value": 2.5},
    }
    denormalized = denormalize_ngsi_entity(entity)
    assert denormalized["name"] == "Product 1"
    assert denormalized["price"] == 2.5


def test_normalize_employee_payload_wraps_required_attributes():
    payload = normalize_ngsi_payload(
        {
            "id": "urn:ngsi-ld:Employee:001",
            "name": "Employee 1",
            "image": "https://example.com/employee.png",
            "salary": 2000,
            "role": "Cashier",
            "refStore": "urn:ngsi-ld:Store:001",
        },
        "Employee",
    )
    assert payload["image"]["type"] == "Text"
    assert payload["salary"]["type"] == "Float"
    assert payload["refStore"]["type"] == "Relationship"


def test_normalize_employee_payload_rejects_invalid_ref_store():
    try:
        normalize_ngsi_payload(
            {
                "id": "urn:ngsi-ld:Employee:001",
                "name": "Employee 1",
                "image": "https://example.com/employee.png",
                "salary": 2000,
                "role": "Cashier",
                "refStore": "Store:001",
            },
            "Employee",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "refStore" in str(exc)


def test_normalize_employee_payload_rejects_negative_salary():
    try:
        normalize_ngsi_payload(
            {
                "id": "urn:ngsi-ld:Employee:001",
                "name": "Employee 1",
                "image": "https://example.com/employee.png",
                "salary": -1,
                "role": "Cashier",
                "refStore": "urn:ngsi-ld:Store:001",
            },
            "Employee",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "salary" in str(exc)


def test_normalize_employee_payload_rejects_invalid_image():
    try:
        normalize_ngsi_payload(
            {
                "id": "urn:ngsi-ld:Employee:001",
                "name": "Employee 1",
                "image": "image.png",
                "salary": 1000,
                "role": "Cashier",
                "refStore": "urn:ngsi-ld:Store:001",
            },
            "Employee",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "image" in str(exc)
