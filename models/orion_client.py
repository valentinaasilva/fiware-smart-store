from typing import Any

import requests


class OrionClient:
    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/version", timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_entities(self, entity_type: str | None = None) -> list[dict[str, Any]]:
        params = {}
        if entity_type:
            params["type"] = entity_type
        response = requests.get(
            f"{self.base_url}/v2/entities",
            params=params,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        response = requests.get(
            f"{self.base_url}/v2/entities/{entity_id}",
            headers=self.headers,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def create_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/v2/entities",
            json=entity,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return entity

    def update_entity(self, entity_id: str, attrs: dict[str, Any]) -> dict[str, Any] | None:
        response = requests.patch(
            f"{self.base_url}/v2/entities/{entity_id}/attrs",
            json=attrs,
            headers=self.headers,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        entity = self.get_entity(entity_id)
        return entity

    def delete_entity(self, entity_id: str) -> bool:
        response = requests.delete(
            f"{self.base_url}/v2/entities/{entity_id}",
            headers=self.headers,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    def register_subscription(self, payload: dict[str, Any]) -> bool:
        response = requests.post(
            f"{self.base_url}/v2/subscriptions",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )
        return response.status_code in (201, 409)

    def register_provider(self, payload: dict[str, Any]) -> bool:
        response = requests.post(
            f"{self.base_url}/v2/registrations",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )
        return response.status_code in (201, 409)
