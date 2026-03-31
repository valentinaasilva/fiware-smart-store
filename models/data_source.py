import os
import logging
from typing import Any

from models.database import SQLiteRepository
from models.orion_client import OrionClient


logger = logging.getLogger(__name__)


class DataSourceSelector:
    def __init__(self, orion_url: str, sqlite_path: str):
        orion_timeout = int(os.getenv("ORION_TIMEOUT", "5"))
        self.orion = OrionClient(orion_url, timeout=orion_timeout)
        self.sqlite = SQLiteRepository(sqlite_path)
        self.mode = "SQLITE"

    def bootstrap(self) -> None:
        self.mode = "ORION" if self.orion.health_check() else "SQLITE"
        logger.info("Data source selected at startup: %s", self.mode)
        if self.mode == "ORION":
            try:
                self._register_external_integrations()
                logger.info("Orion integrations registered (providers/subscriptions)")
            except Exception as exc:
                logger.warning("Orion integrations registration skipped: %s", exc)
        else:
            logger.warning("Orion unavailable at startup, running with SQLite fallback")

    def _active(self):
        return self.orion if self.mode == "ORION" else self.sqlite

    @staticmethod
    def _store_provider_payloads(
        store_id: str,
        weather_provider_url: str,
        tweets_provider_url: str,
    ) -> list[dict[str, Any]]:
        return [
            {
                "description": f"External weather context provider for {store_id}",
                "dataProvided": {
                    "entities": [{"id": store_id, "type": "Store"}],
                    "attrs": ["temperature", "relativeHumidity"],
                },
                "provider": {
                    "http": {"url": weather_provider_url},
                    "legacyForwarding": True,
                },
                "status": "active",
            },
            {
                "description": f"External tweets context provider for {store_id}",
                "dataProvided": {
                    "entities": [{"id": store_id, "type": "Store"}],
                    "attrs": ["tweets"],
                },
                "provider": {
                    "http": {"url": tweets_provider_url},
                    "legacyForwarding": True,
                },
                "status": "active",
            },
        ]

    def _register_external_integrations(self) -> None:
        callback_base = os.getenv("CALLBACK_BASE_URL", "http://host.docker.internal:5000")
        provider_base_url = os.getenv("PROVIDER_BASE_URL", callback_base).rstrip("/")
        weather_provider_url = os.getenv(
            "WEATHER_PROVIDER_URL", f"{provider_base_url}/providers/weather"
        )
        tweets_provider_url = os.getenv(
            "TWEETS_PROVIDER_URL", f"{provider_base_url}/providers/tweets"
        )
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

        stores = self.orion.list_entities("Store")
        for store in stores:
            store_id = store.get("id")
            if not isinstance(store_id, str) or not store_id:
                continue

            for provider in self._store_provider_payloads(store_id, weather_provider_url, tweets_provider_url):
                self.orion.register_provider(provider)
        
        for subscription in subscriptions:
            result = self.orion.register_subscription(subscription)
            sub_desc = subscription.get("description", "Unknown")
            logger.info("Subscription '%s' registration result: %s", sub_desc, result)

    def _fallback_to_sqlite(self, reason: str) -> None:
        if self.mode != "SQLITE":
            logger.warning("Switching data source from ORION to SQLITE fallback: %s", reason)
        self.mode = "SQLITE"

    def list_entities(self, entity_type: str | None = None) -> list[dict[str, Any]]:
        try:
            return self._active().list_entities(entity_type)
        except Exception as exc:
            self._fallback_to_sqlite(f"list_entities failed ({exc})")
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
        except Exception as exc:
            self._fallback_to_sqlite(f"get_entity failed ({exc})")
            return self.sqlite.get_entity(entity_id)

    def create_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        try:
            created = self._active().create_entity(entity)
            created_store_id = created.get("id")
            if self.mode == "ORION" and created.get("type") == "Store" and isinstance(created_store_id, str):
                provider_base_url = os.getenv(
                    "PROVIDER_BASE_URL", os.getenv("CALLBACK_BASE_URL", "http://host.docker.internal:5000")
                ).rstrip("/")
                weather_provider_url = os.getenv(
                    "WEATHER_PROVIDER_URL", f"{provider_base_url}/providers/weather"
                )
                tweets_provider_url = os.getenv(
                    "TWEETS_PROVIDER_URL", f"{provider_base_url}/providers/tweets"
                )
                for provider in self._store_provider_payloads(created_store_id, weather_provider_url, tweets_provider_url):
                    self.orion.register_provider(provider)
            return created
        except Exception as exc:
            self._fallback_to_sqlite(f"create_entity failed ({exc})")
            return self.sqlite.create_entity(entity)

    def update_entity(self, entity_id: str, attrs: dict[str, Any]) -> dict[str, Any] | None:
        try:
            return self._active().update_entity(entity_id, attrs)
        except Exception as exc:
            self._fallback_to_sqlite(f"update_entity failed ({exc})")
            return self.sqlite.update_entity(entity_id, attrs)

    def delete_entity(self, entity_id: str) -> bool:
        try:
            return self._active().delete_entity(entity_id)
        except Exception as exc:
            self._fallback_to_sqlite(f"delete_entity failed ({exc})")
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
