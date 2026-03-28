def test_end_to_end_store_product_inventory_flow(client, sample_store, sample_product, sample_inventory_item):
    # Create store and product entities first.
    store_resp = client.post("/stores/", json=sample_store)
    product_resp = client.post("/products/", json=sample_product)

    assert store_resp.status_code == 201
    assert product_resp.status_code == 201

    create_inventory = client.post("/inventory", json=sample_inventory_item)
    assert create_inventory.status_code == 201

    dashboard = client.get("/")
    assert dashboard.status_code == 200

    list_inventory = client.get("/inventory")
    assert list_inventory.status_code == 200
    assert any(item["id"] == sample_inventory_item["id"] for item in list_inventory.get_json())

    update_inventory = client.put(
        f"/inventory/{sample_inventory_item['id']}",
        json={"stockCount": {"type": "Integer", "value": 15}},
    )
    assert update_inventory.status_code == 200

    delete_inventory = client.delete(f"/inventory/{sample_inventory_item['id']}")
    assert delete_inventory.status_code == 204
