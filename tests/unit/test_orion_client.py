from __future__ import annotations

import requests

from models.orion_client import OrionClient


class DummyResponse:
    def __init__(self, status_code: int = 200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def test_health_check_success(monkeypatch):
    def fake_get(url, timeout):
        assert url.endswith("/version")
        return DummyResponse(200, {"version": "3.4.0"})

    monkeypatch.setattr(requests, "get", fake_get)

    client = OrionClient("http://orion")
    assert client.health_check() is True


def test_health_check_request_exception(monkeypatch):
    def fake_get(url, timeout):
        raise requests.RequestException("down")

    monkeypatch.setattr(requests, "get", fake_get)

    client = OrionClient("http://orion")
    assert client.health_check() is False


def test_list_entities_by_type(monkeypatch):
    def fake_get(url, params, headers, timeout):
        assert url.endswith("/v2/entities")
        assert params["type"] == "Store"
        assert params["limit"] == 1000
        assert params["offset"] == 0
        return DummyResponse(200, [{"id": "urn:ngsi-ld:Store:001", "type": "Store"}])

    monkeypatch.setattr(requests, "get", fake_get)

    client = OrionClient("http://orion")
    entities = client.list_entities("Store")
    assert len(entities) == 1


def test_get_entity_not_found(monkeypatch):
    def fake_get(url, headers, timeout):
        return DummyResponse(404)

    monkeypatch.setattr(requests, "get", fake_get)

    client = OrionClient("http://orion")
    assert client.get_entity("urn:ngsi-ld:Store:404") is None


def test_create_entity_returns_input_payload(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResponse(201)

    monkeypatch.setattr(requests, "post", fake_post)

    payload = {"id": "urn:ngsi-ld:Store:001", "type": "Store", "name": "S1"}
    client = OrionClient("http://orion")
    created = client.create_entity(payload)
    assert created == payload


def test_update_entity_returns_none_on_404(monkeypatch):
    def fake_patch(url, json, headers, timeout):
        return DummyResponse(404)

    monkeypatch.setattr(requests, "patch", fake_patch)

    client = OrionClient("http://orion")
    updated = client.update_entity("urn:ngsi-ld:Store:404", {"name": "S2"})
    assert updated is None


def test_update_entity_fetches_current_entity(monkeypatch):
    calls = {"patch": 0, "get": 0}

    def fake_patch(url, json, headers, timeout):
        calls["patch"] += 1
        return DummyResponse(204)

    def fake_get(url, headers, timeout):
        calls["get"] += 1
        return DummyResponse(200, {"id": "urn:ngsi-ld:Store:001", "name": "S2"})

    monkeypatch.setattr(requests, "patch", fake_patch)
    monkeypatch.setattr(requests, "get", fake_get)

    client = OrionClient("http://orion")
    updated = client.update_entity("urn:ngsi-ld:Store:001", {"name": "S2"})
    assert updated["name"] == "S2"
    assert calls["patch"] == 1
    assert calls["get"] == 1


def test_delete_entity_not_found(monkeypatch):
    def fake_delete(url, headers, timeout):
        return DummyResponse(404)

    monkeypatch.setattr(requests, "delete", fake_delete)

    client = OrionClient("http://orion")
    assert client.delete_entity("urn:ngsi-ld:Store:404") is False


def test_delete_entity_success(monkeypatch):
    def fake_delete(url, headers, timeout):
        return DummyResponse(204)

    monkeypatch.setattr(requests, "delete", fake_delete)

    client = OrionClient("http://orion")
    assert client.delete_entity("urn:ngsi-ld:Store:001") is True


def test_register_subscription_accepts_conflict(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResponse(409)

    monkeypatch.setattr(requests, "post", fake_post)

    client = OrionClient("http://orion")
    assert client.register_subscription({"description": "test"}) is True


def test_register_provider_accepts_created(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResponse(201)

    monkeypatch.setattr(requests, "post", fake_post)

    client = OrionClient("http://orion")
    assert client.register_provider({"description": "provider"}) is True


def test_increment_entity_attrs_uses_inc_payload(monkeypatch):
    captured = {}

    def fake_patch(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        return DummyResponse(204)

    def fake_get(url, headers, timeout):
        return DummyResponse(200, {"id": "urn:ngsi-ld:InventoryItem:001", "stockCount": {"type": "Integer", "value": 6}})

    monkeypatch.setattr(requests, "patch", fake_patch)
    monkeypatch.setattr(requests, "get", fake_get)

    client = OrionClient("http://orion")
    updated = client.increment_entity_attrs("urn:ngsi-ld:InventoryItem:001", {"stockCount": -1, "shelfCount": -1})

    assert updated is not None
    assert captured["url"].endswith("/v2/entities/urn:ngsi-ld:InventoryItem:001/attrs")
    assert captured["json"]["stockCount"]["value"]["$inc"] == -1
    assert captured["json"]["shelfCount"]["value"]["$inc"] == -1
