import json
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteRepository:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = self._normalize_sqlite_path(sqlite_path)
        db_parent = Path(self.sqlite_path).parent
        db_parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _normalize_sqlite_path(self, sqlite_path: str) -> str:
        path = Path(sqlite_path)

        # If a directory is provided, place the database file inside it.
        if path.exists() and path.is_dir():
            return str(path / "fiware.db")

        parent = path.parent
        # If parent points to an existing file (e.g., ./services script), fallback safely.
        if parent.exists() and not parent.is_dir():
            fallback = Path.cwd() / "instance" / "fiware.db"
            return str(fallback)

        # If path has no extension and does not exist yet, treat it as a directory path.
        if not path.suffix and not path.exists():
            return str(path / "fiware.db")

        return str(path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS entities_updated_at
                AFTER UPDATE ON entities
                BEGIN
                    UPDATE entities SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
                """
            )

    def list_entities(self, entity_type: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT payload FROM entities"
        args: tuple[Any, ...] = ()
        if entity_type:
            query += " WHERE type = ?"
            args = (entity_type,)
        query += " ORDER BY id"
        with self._connect() as conn:
            rows = conn.execute(query, args).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            return None
        return json.loads(row["payload"])

    def create_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO entities (id, type, payload) VALUES (?, ?, ?)",
                (entity["id"], entity["type"], json.dumps(entity)),
            )
        return entity

    def update_entity(self, entity_id: str, attrs: dict[str, Any]) -> dict[str, Any] | None:
        current = self.get_entity(entity_id)
        if not current:
            return None
        current.update(attrs)
        with self._connect() as conn:
            conn.execute(
                "UPDATE entities SET payload = ?, type = ? WHERE id = ?",
                (json.dumps(current), current.get("type", "Unknown"), entity_id),
            )
        return current

    @staticmethod
    def _attr_int_value(value: Any, default: int = 0) -> int:
        raw = value
        if isinstance(value, dict) and "value" in value:
            raw = value.get("value")
        try:
            return int(raw)
        except (TypeError, ValueError):
            return default

    def increment_entity_attrs(self, entity_id: str, increments: dict[str, int]) -> dict[str, Any] | None:
        current = self.get_entity(entity_id)
        if not current:
            return None

        updated = dict(current)
        for field, delta in increments.items():
            previous = updated.get(field)
            next_value = self._attr_int_value(previous, default=0) + int(delta)
            if isinstance(previous, dict):
                next_attr = dict(previous)
                next_attr["value"] = next_value
            else:
                next_attr = {"type": "Integer", "value": next_value}
            updated[field] = next_attr

        with self._connect() as conn:
            conn.execute(
                "UPDATE entities SET payload = ?, type = ? WHERE id = ?",
                (json.dumps(updated), updated.get("type", "Unknown"), entity_id),
            )
        return updated

    def delete_entity(self, entity_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            return cur.rowcount > 0

    def get_dashboard_stats(self) -> dict[str, int]:
        stats = {
            "stores": 0,
            "products": 0,
            "employees": 0,
            "inventory_items": 0,
        }
        mapping = {
            "Store": "stores",
            "Product": "products",
            "Employee": "employees",
            "InventoryItem": "inventory_items",
        }
        with self._connect() as conn:
            rows = conn.execute("SELECT type, COUNT(*) as total FROM entities GROUP BY type").fetchall()
        for row in rows:
            key = mapping.get(row["type"])
            if key:
                stats[key] = int(row["total"])
        return stats
