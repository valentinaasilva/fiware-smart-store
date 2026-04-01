from app import create_app
import re


def _raw_or_ngsi_value(value):
    if isinstance(value, dict) and "value" in value:
        return value.get("value")
    return value


def test_dashboard_loads():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"fiware-smart-store" in response.data


def test_main_navigation_has_five_primary_views():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    body = response.data
    assert b'href="/"' in body
    assert b'href="/stores' in body
    assert b'href="/products' in body
    assert b'href="/employees' in body
    assert b'href="/stores-map"' in body


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


def test_stores_map_page_loads():
    app = create_app()
    client = app.test_client()

    response = client.get("/stores-map")

    assert response.status_code == 200
    assert b'id="stores-map-page"' in response.data


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


def test_list_and_detail_views_show_simplified_ids_refstore_and_country_names():
    app = create_app()
    client = app.test_client()

    stores_json = client.get("/stores?format=json")
    products_json = client.get("/products?format=json")
    employees_json = client.get("/employees?format=json")
    assert stores_json.status_code == 200
    assert products_json.status_code == 200
    assert employees_json.status_code == 200

    country_names = {
        "ES": "Spain",
        "DE": "Germany",
        "FR": "France",
        "EC": "Ecuador",
    }

    first_store = (stores_json.get_json() or [])[0]
    first_product = (products_json.get_json() or [])[0]
    first_employee = (employees_json.get_json() or [])[0]
    store_id = first_store["id"]
    product_id = first_product["id"]
    employee_id = first_employee["id"]
    store_country_code = _raw_or_ngsi_value(first_store.get("countryCode"))
    product_country_code = _raw_or_ngsi_value(first_product.get("originCountry"))
    expected_store_country = country_names.get(store_country_code, store_country_code or "-")
    expected_product_country = country_names.get(product_country_code, product_country_code or "-")

    stores_list = client.get("/stores")
    products_list = client.get("/products")
    employees_list = client.get("/employees")
    product_detail = client.get(f"/products/{product_id}")
    employee_detail = client.get(f"/employees/{employee_id}")

    assert stores_list.status_code == 200
    assert products_list.status_code == 200
    assert employees_list.status_code == 200
    assert product_detail.status_code == 200
    assert employee_detail.status_code == 200

    stores_body = stores_list.data.decode("utf-8")
    products_body = products_list.data.decode("utf-8")
    employees_body = employees_list.data.decode("utf-8")
    product_detail_body = product_detail.data.decode("utf-8")
    employee_detail_body = employee_detail.data.decode("utf-8")

    assert store_id.split(":")[-1] in stores_body
    assert expected_store_country in stores_body

    assert product_id.split(":")[-1] in products_body
    assert expected_product_country in products_body
    assert re.search(rf"<dt>\s*ID\s*</dt>\s*<dd class=\"mono\">\s*{re.escape(product_id.split(':')[-1])}\s*</dd>", product_detail_body)
    assert expected_product_country in product_detail_body
    assert "<dt>Type</dt>" not in product_detail_body

    assert employee_id.split(":")[-1] in employees_body
    assert "urn:ngsi-ld:Store:" not in employees_body
    assert "urn:ngsi-ld:Store:" not in employee_detail_body
    assert "<dt>Type</dt>" not in employee_detail_body


def test_store_and_product_detail_render_crud_sections():
    app = create_app()
    client = app.test_client()

    stores_json = client.get("/stores?format=json")
    products_json = client.get("/products?format=json")
    assert stores_json.status_code == 200
    assert products_json.status_code == 200

    store_id = (stores_json.get_json() or [])[0]["id"]
    product_id = (products_json.get_json() or [])[0]["id"]

    store_detail = client.get(f"/stores/{store_id}")
    product_detail = client.get(f"/products/{product_id}")

    assert store_detail.status_code == 200
    assert product_detail.status_code == 200

    store_body = store_detail.data.decode("utf-8")
    product_body = product_detail.data.decode("utf-8")

    assert "Products in Store" in store_body
    assert "Shelves" in store_body
    assert "Add Shelf" in store_body
    assert "Add Inventory Item" in store_body

    assert "Available in Stores" in product_body
    assert "Inventory" in product_body
    assert "Add Inventory Item" in product_body
