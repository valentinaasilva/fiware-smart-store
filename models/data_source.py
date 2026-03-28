import os
from typing import Any

from models.database import SQLiteRepository
from models.orion_client import OrionClient


class DataSourceSelector:
    def __init__(self, orion_url: str, sqlite_path: str):
        self.orion = OrionClient(orion_url)
        self.sqlite = SQLiteRepository(sqlite_path)
        self.mode = "SQLITE"

    def bootstrap(self) -> None:
        self.mode = "ORION" if self.orion.health_check() else "SQLITE"
        if self.mode == "ORION":
            self._register_external_integrations()

    def _active(self):
        return self.orion if self.mode == "ORION" else self.sqlite

    def _register_external_integrations(self) -> None:
        callback_base = os.getenv("CALLBACK_BASE_URL", "http://host.docker.internal:5000")
        subscriptions = [
            {
                "description": "Notify product price change",
                "subject": {
                    "entities": [{"idPattern": "urn:ngsi-ld:Product:.*", "type": "Product"}],
                    "condition": {"attrs": ["price"]},
                },
                "notification": {
                    "http": {"url": f"{callback_base}/notifications/price-change"},
                    "attrs": ["name", "price", "size", "color"],
                },
            },
            {
                "description": "Notify inventory low stock",
                "subject": {
                    "entities": [{"idPattern": "urn:ngsi-ld:InventoryItem:.*", "type": "InventoryItem"}],
                    "condition": {"attrs": ["stockCount", "shelfCount"]},
                },
                "notification": {
                    "http": {"url": f"{callback_base}/notifications/low-stock"},
                    "attrs": ["refStore", "refShelf", "refProduct", "stockCount", "shelfCount"],
                },
            },
        ]

        provider = {
            "description": "External store context provider",
            "dataProvided": {
                "entities": [{"idPattern": "urn:ngsi-ld:Store:.*", "type": "Store"}],
                "attrs": ["temperature", "relativeHumidity", "tweets"],
            },
            "provider": {"http": {"url": os.getenv("TUTORIAL_PROVIDER_URL", "http://localhost:3000")}},
        }

        self.orion.register_provider(provider)
        for subscription in subscriptions:
            self.orion.register_subscription(subscription)

    def list_entities(self, entity_type: str | None = None) -> list[dict[str, Any]]:
        try:
            return self._active().list_entities(entity_type)
        except Exception:
            self.mode = "SQLITE"
            return self.sqlite.list_entities(entity_type)

    @staticmethod
    def _extract_attr_value(value: Any) -> Any:
        if isinstance(value, dict) and "value" in value:
            return value.get("value")
        return value

    def list_entities_filtered(self, entity_type: str, field: str, expected_value: Any) -> list[dict[str, Any]]:
        entities = self.list_entities(entity_type)
        return [
            entity
            for entity in entities
            if self._extract_attr_value(entity.get(field)) == expected_value
        ]

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        try:
            return self._active().get_entity(entity_id)
        except Exception:
            self.mode = "SQLITE"
            return self.sqlite.get_entity(entity_id)

    def create_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._active().create_entity(entity)
        except Exception:
            self.mode = "SQLITE"
            return self.sqlite.create_entity(entity)

    def update_entity(self, entity_id: str, attrs: dict[str, Any]) -> dict[str, Any] | None:
        try:
            return self._active().update_entity(entity_id, attrs)
        except Exception:
            self.mode = "SQLITE"
            return self.sqlite.update_entity(entity_id, attrs)

    def delete_entity(self, entity_id: str) -> bool:
        try:
            return self._active().delete_entity(entity_id)
        except Exception:
            self.mode = "SQLITE"
            return self.sqlite.delete_entity(entity_id)

    def get_dashboard_stats(self) -> dict[str, int]:
        if self.mode == "ORION":
            entities = self.list_entities()
            stats = {
                "stores": 0,
                "products": 0,
                "employees": 0,
                "inventory_items": 0,
            }
            for entity in entities:
                if entity.get("type") == "Store":
                    stats["stores"] += 1
                elif entity.get("type") == "Product":
                    stats["products"] += 1
                elif entity.get("type") == "Employee":
                    stats["employees"] += 1
                elif entity.get("type") == "InventoryItem":
                    stats["inventory_items"] += 1
            return stats
        return self.sqlite.get_dashboard_stats()
