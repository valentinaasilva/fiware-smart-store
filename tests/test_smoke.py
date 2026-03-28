from app import create_app
import re


def test_dashboard_loads():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"fiware-smart-store" in response.data


def test_main_navigation_has_four_primary_views():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    body = response.data
    assert b'href="/"' in body
    assert b'href="/stores' in body
    assert b'href="/products' in body
    assert b'href="/employees' in body


def test_stores_endpoint_json():
    app = create_app()
    client = app.test_client()

    response = client.get("/stores/?format=json")

    assert response.status_code == 200
    assert response.is_json


def test_primary_navigation_links_resolve_successfully():
    app = create_app()
    client = app.test_client()

    for path in ("/", "/stores", "/products", "/employees"):
        response = client.get(path)
        assert response.status_code == 200


def test_store_detail_contains_leaflet_map_container():
    app = create_app()
    client = app.test_client()

    stores = client.get("/stores?format=json")
    assert stores.status_code == 200
    store_entities = stores.get_json() or []
    assert len(store_entities) > 0

    store_id = store_entities[0]["id"]
    detail = client.get(f"/stores/{store_id}")
    assert detail.status_code == 200
    assert b'id="store-map"' in detail.data


def test_language_toggle_spanish_persists_in_session():
    app = create_app()
    client = app.test_client()

    response = client.get("/language/es?next=/", follow_redirects=True)

    assert response.status_code == 200
    assert "Panel".encode("utf-8") in response.data
    assert "Idioma".encode("utf-8") in response.data

    second = client.get("/")
    assert second.status_code == 200
    assert "Panel".encode("utf-8") in second.data


def test_language_toggle_back_to_english():
    app = create_app()
    client = app.test_client()

    client.get("/language/es?next=/", follow_redirects=True)
    response = client.get("/language/en?next=/", follow_redirects=True)

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Language" in response.data


def test_store_detail_shows_simplified_id_country_name_address_and_hides_type():
    app = create_app()
    client = app.test_client()

    stores = client.get("/stores?format=json")
    assert stores.status_code == 200
    store_entities = stores.get_json() or []
    assert len(store_entities) > 0

    store_id = store_entities[0]["id"]
    detail = client.get(f"/stores/{store_id}")

    assert detail.status_code == 200
    expected_simple_id = store_id.split(":")[-1]
    body = detail.data.decode("utf-8")
    assert re.search(rf"<dt>\s*ID\s*</dt>\s*<dd class=\"mono\">\s*{re.escape(expected_simple_id)}\s*</dd>", body)
    assert b"Spain" in detail.data
    assert "Oviedo".encode("utf-8") in detail.data
    assert "Asturias".encode("utf-8") in detail.data
    assert b"Type" not in detail.data
