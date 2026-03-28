def test_price_change_webhook_emits(client):
    response = client.post("/notifications/price-change", json={"id": "urn:ngsi-ld:Product:001"})
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json().get("status") == "ok"


def test_low_stock_webhook_emits(client):
    response = client.post("/notifications/low-stock", json={"id": "urn:ngsi-ld:InventoryItem:001"})
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json().get("status") == "ok"
