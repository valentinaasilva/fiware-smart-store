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
