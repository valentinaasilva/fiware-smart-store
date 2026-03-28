from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Create app configured for isolated SQLite tests."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SQLITE_PATH", str(db_path))
    monkeypatch.setenv("ORION_URL", "http://127.0.0.1:9")

    from app import create_app

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_store() -> dict:
    return {
        "id": "urn:ngsi-ld:Store:TEST001",
        "type": "Store",
        "name": "Test Store",
        "countryCode": "ES",
        "capacity": 100,
        "image": "https://example.com/store.png",
    }


@pytest.fixture
def sample_product() -> dict:
    return {
        "id": "urn:ngsi-ld:Product:TEST001",
        "type": "Product",
        "name": "Test Product",
        "price": 9.99,
        "size": "M",
        "color": "#FF0000",
        "originCountry": "ES",
        "image": "https://example.com/product.png",
    }


@pytest.fixture
def sample_employee() -> dict:
    return {
        "id": "urn:ngsi-ld:Employee:TEST001",
        "type": "Employee",
        "name": "Test Employee",
        "image": "https://example.com/employee.png",
        "salary": 2300.0,
        "role": "Cashier",
        "refStore": "urn:ngsi-ld:Store:TEST001",
        "category": "Senior",
        "email": "test@example.com",
    }


@pytest.fixture
def sample_inventory_item() -> dict:
    return {
        "id": "urn:ngsi-ld:InventoryItem:TEST001",
        "type": "InventoryItem",
        "refStore": {"type": "Relationship", "value": "urn:ngsi-ld:Store:TEST001"},
        "refProduct": {"type": "Relationship", "value": "urn:ngsi-ld:Product:TEST001"},
        "refShelf": {"type": "Relationship", "value": "urn:ngsi-ld:Shelf:001"},
        "stockCount": {"type": "Integer", "value": 10},
        "shelfCount": {"type": "Integer", "value": 5},
    }
