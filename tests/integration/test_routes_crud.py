import html as html_lib
import json
import re


def test_stores_crud(client, sample_store):
    create = client.post("/stores/", json=sample_store)
    assert create.status_code == 201
    assert create.get_json()["image"]["value"] == sample_store["image"]

    list_resp = client.get("/stores/?format=json")
    assert list_resp.status_code == 200
    assert any(e["id"] == sample_store["id"] for e in list_resp.get_json())

    detail = client.get(f"/stores/{sample_store['id']}?format=json")
    assert detail.status_code == 200

    update = client.put(f"/stores/{sample_store['id']}", json={"name": "Updated Store"})
    assert update.status_code == 200
    assert update.get_json()["name"]["value"] == "Updated Store"

    delete = client.delete(f"/stores/{sample_store['id']}")
    assert delete.status_code == 204

    missing = client.get(f"/stores/{sample_store['id']}?format=json")
    assert missing.status_code == 404


def test_products_crud(client, sample_product):
    create = client.post("/products/", json=sample_product)
    assert create.status_code == 201
    assert create.get_json()["originCountry"]["value"] == sample_product["originCountry"]

    list_resp = client.get("/products/?format=json")
    assert list_resp.status_code == 200
    assert any(e["id"] == sample_product["id"] for e in list_resp.get_json())

    detail = client.get(f"/products/{sample_product['id']}?format=json")
    assert detail.status_code == 200

    update = client.put(f"/products/{sample_product['id']}", json={"price": 12.5})
    assert update.status_code == 200
    assert update.get_json()["price"]["value"] == 12.5

    delete = client.delete(f"/products/{sample_product['id']}")
    assert delete.status_code == 204


def test_employees_crud(client, sample_employee):
    create = client.post("/employees/", json=sample_employee)
    assert create.status_code == 201
    assert create.get_json()["image"]["value"] == sample_employee["image"]
    assert create.get_json()["role"]["value"] == sample_employee["role"]
    assert create.get_json()["salary"]["value"] == sample_employee["salary"]
    assert create.get_json()["refStore"]["value"] == sample_employee["refStore"]

    list_resp = client.get("/employees/?format=json")
    assert list_resp.status_code == 200
    assert any(e["id"] == sample_employee["id"] for e in list_resp.get_json())

    detail = client.get(f"/employees/{sample_employee['id']}?format=json")
    assert detail.status_code == 200

    update = client.put(f"/employees/{sample_employee['id']}", json={"category": "Manager"})
    assert update.status_code == 200
    assert update.get_json()["category"]["value"] == "Manager"

    delete = client.delete(f"/employees/{sample_employee['id']}")
    assert delete.status_code == 204


def test_inventory_crud(client, sample_store, sample_product, sample_inventory_item):
    client.post("/stores/", json=sample_store)
    client.post("/products/", json=sample_product)

    create = client.post("/inventory/", json=sample_inventory_item)
    assert create.status_code == 201

    list_resp = client.get("/inventory/")
    assert list_resp.status_code == 200
    data = list_resp.get_json()
    assert any(e["id"] == sample_inventory_item["id"] for e in data)

    update = client.put(f"/inventory/{sample_inventory_item['id']}", json={"stockCount": {"type": "Integer", "value": 20}})
    assert update.status_code == 200

    delete = client.delete(f"/inventory/{sample_inventory_item['id']}")
    assert delete.status_code == 204


def test_inventory_create_requires_id(client):
    resp = client.post("/inventory/", json={"type": "InventoryItem"})
    assert resp.status_code == 400


def test_products_create_rejects_invalid_origin_country(client, sample_product):
    invalid = dict(sample_product)
    invalid["id"] = "urn:ngsi-ld:Product:TEST002"
    invalid["originCountry"] = "ESP"
    resp = client.post("/products/", json=invalid)
    assert resp.status_code == 400


def test_products_create_accepts_legacy_origin_field(client, sample_product):
    legacy = dict(sample_product)
    legacy["id"] = "urn:ngsi-ld:Product:TEST003"
    legacy["origin"] = legacy.pop("originCountry")
    resp = client.post("/products/", json=legacy)
    assert resp.status_code == 201
    assert resp.get_json()["originCountry"]["value"] == "ES"


def test_employees_create_rejects_invalid_ref_store(client, sample_employee):
    invalid = dict(sample_employee)
    invalid["id"] = "urn:ngsi-ld:Employee:TEST002"
    invalid["refStore"] = "Store:S001"
    resp = client.post("/employees/", json=invalid)
    assert resp.status_code == 400


def test_employees_create_rejects_invalid_image(client, sample_employee):
    invalid = dict(sample_employee)
    invalid["id"] = "urn:ngsi-ld:Employee:TEST003"
    invalid["image"] = "ftp://example.com/employee.png"
    resp = client.post("/employees/", json=invalid)
    assert resp.status_code == 400


def test_store_nested_shelf_and_inventory_crud(client, sample_store, sample_product, sample_shelf):
    client.post("/stores/", json=sample_store)
    client.post("/products/", json=sample_product)

    shelf_create = client.post(f"/stores/{sample_store['id']}/shelves", json=sample_shelf)
    assert shelf_create.status_code == 201

    shelf_update = client.put(
        f"/stores/{sample_store['id']}/shelves/{sample_shelf['id']}",
        json={"name": "Shelf Updated", "maxCapacity": 60},
    )
    assert shelf_update.status_code == 200

    inv_payload = {
        "id": "urn:ngsi-ld:InventoryItem:TESTSTORE001",
        "type": "InventoryItem",
        "refProduct": {"type": "Relationship", "value": sample_product["id"]},
        "refShelf": {"type": "Relationship", "value": sample_shelf["id"]},
        "stockCount": {"type": "Integer", "value": 20},
        "shelfCount": {"type": "Integer", "value": 10},
    }
    inv_create = client.post(f"/stores/{sample_store['id']}/inventory", json=inv_payload)
    assert inv_create.status_code == 201

    inv_update = client.put(
        f"/stores/{sample_store['id']}/inventory/{inv_payload['id']}",
        json={"stockCount": {"type": "Integer", "value": 25}, "shelfCount": {"type": "Integer", "value": 12}},
    )
    assert inv_update.status_code == 200

    blocked_delete = client.delete(f"/stores/{sample_store['id']}/shelves/{sample_shelf['id']}")
    assert blocked_delete.status_code == 409

    inv_delete = client.delete(f"/stores/{sample_store['id']}/inventory/{inv_payload['id']}")
    assert inv_delete.status_code == 204

    shelf_delete = client.delete(f"/stores/{sample_store['id']}/shelves/{sample_shelf['id']}")
    assert shelf_delete.status_code == 204


def test_product_nested_inventory_crud(client, sample_store, sample_product, sample_shelf):
    client.post("/stores/", json=sample_store)
    client.post("/products/", json=sample_product)
    client.post(f"/stores/{sample_store['id']}/shelves", json=sample_shelf)

    inv_payload = {
        "id": "urn:ngsi-ld:InventoryItem:TESTPROD001",
        "type": "InventoryItem",
        "refStore": {"type": "Relationship", "value": sample_store["id"]},
        "refShelf": {"type": "Relationship", "value": sample_shelf["id"]},
        "stockCount": {"type": "Integer", "value": 18},
        "shelfCount": {"type": "Integer", "value": 8},
    }
    created = client.post(f"/products/{sample_product['id']}/inventory", json=inv_payload)
    assert created.status_code == 201

    listed = client.get(f"/products/{sample_product['id']}/inventory")
    assert listed.status_code == 200
    assert any(item["id"] == inv_payload["id"] for item in listed.get_json())

    updated = client.put(
        f"/products/{sample_product['id']}/inventory/{inv_payload['id']}",
        json={"stockCount": {"type": "Integer", "value": 30}, "shelfCount": {"type": "Integer", "value": 9}},
    )
    assert updated.status_code == 200

    deleted = client.delete(f"/products/{sample_product['id']}/inventory/{inv_payload['id']}")
    assert deleted.status_code == 204


def test_product_inventory_create_without_id_generates_urn(client, sample_store, sample_product, sample_shelf):
    client.post("/stores/", json=sample_store)
    client.post("/products/", json=sample_product)
    client.post(f"/stores/{sample_store['id']}/shelves", json=sample_shelf)

    inv_payload = {
        "type": "InventoryItem",
        "refStore": {"type": "Relationship", "value": sample_store["id"]},
        "refShelf": {"type": "Relationship", "value": sample_shelf["id"]},
        "stockCount": {"type": "Integer", "value": 2},
        "shelfCount": {"type": "Integer", "value": 1},
    }
    created = client.post(f"/products/{sample_product['id']}/inventory", json=inv_payload)

    assert created.status_code == 201
    entity_id = created.get_json().get("id", "")
    assert entity_id.startswith("urn:ngsi-ld:InventoryItem:")


def test_product_detail_groups_inventory_by_store_with_available_shelves(client, sample_store, sample_product):
    store_id = sample_store["id"]
    product_id = sample_product["id"]

    client.post("/stores/", json=sample_store)
    client.post("/products/", json=sample_product)

    shelf_1 = {
        "id": "urn:ngsi-ld:Shelf:TEST001-A",
        "type": "Shelf",
        "name": "Shelf A",
        "maxCapacity": 50,
        "refStore": {"type": "Relationship", "value": store_id},
    }
    shelf_2 = {
        "id": "urn:ngsi-ld:Shelf:TEST001-B",
        "type": "Shelf",
        "name": "Shelf B",
        "maxCapacity": 50,
        "refStore": {"type": "Relationship", "value": store_id},
    }
    shelf_3 = {
        "id": "urn:ngsi-ld:Shelf:TEST001-C",
        "type": "Shelf",
        "name": "Shelf C",
        "maxCapacity": 50,
        "refStore": {"type": "Relationship", "value": store_id},
    }

    client.post(f"/stores/{store_id}/shelves", json=shelf_1)
    client.post(f"/stores/{store_id}/shelves", json=shelf_2)
    client.post(f"/stores/{store_id}/shelves", json=shelf_3)

    inv_1 = {
        "id": "urn:ngsi-ld:InventoryItem:TEST-GRP-1",
        "type": "InventoryItem",
        "refStore": {"type": "Relationship", "value": store_id},
        "refShelf": {"type": "Relationship", "value": shelf_1["id"]},
        "stockCount": {"type": "Integer", "value": 8},
        "shelfCount": {"type": "Integer", "value": 3},
    }
    inv_2 = {
        "id": "urn:ngsi-ld:InventoryItem:TEST-GRP-2",
        "type": "InventoryItem",
        "refStore": {"type": "Relationship", "value": store_id},
        "refShelf": {"type": "Relationship", "value": shelf_2["id"]},
        "stockCount": {"type": "Integer", "value": 4},
        "shelfCount": {"type": "Integer", "value": 2},
    }

    client.post(f"/products/{product_id}/inventory", json=inv_1)
    client.post(f"/products/{product_id}/inventory", json=inv_2)

    detail = client.get(f"/products/{product_id}")
    assert detail.status_code == 200

    html = detail.get_data(as_text=True)
    assert "inventory-store-group-row" in html
    assert "Shelf A" in html
    assert "Shelf B" in html

    matches = re.findall(r"data-available-shelves='([^']*)'", html)
    assert matches
    available_shelves = [json.loads(html_lib.unescape(payload)) for payload in matches]
    flat_ids = {shelf.get("id") for shelves in available_shelves for shelf in shelves}
    assert shelf_3["id"] in flat_ids


def test_store_inventory_buy_decrements_counts(client, sample_store, sample_product, sample_shelf):
    client.post("/stores/", json=sample_store)
    client.post("/products/", json=sample_product)
    client.post(f"/stores/{sample_store['id']}/shelves", json=sample_shelf)

    inv_payload = {
        "id": "urn:ngsi-ld:InventoryItem:TESTBUY001",
        "type": "InventoryItem",
        "refProduct": {"type": "Relationship", "value": sample_product["id"]},
        "refShelf": {"type": "Relationship", "value": sample_shelf["id"]},
        "stockCount": {"type": "Integer", "value": 6},
        "shelfCount": {"type": "Integer", "value": 3},
    }
    created = client.post(f"/stores/{sample_store['id']}/inventory", json=inv_payload)
    assert created.status_code == 201

    buy = client.post(f"/stores/{sample_store['id']}/inventory/{inv_payload['id']}/buy", json={})
    assert buy.status_code == 200

    detail = client.get(f"/stores/{sample_store['id']}/inventory")
    assert detail.status_code == 200
    rows = detail.get_json()
    bought = next(item for item in rows if item["id"] == inv_payload["id"])
    assert bought["stockCount"]["value"] == 5
    assert bought["shelfCount"]["value"] == 2
