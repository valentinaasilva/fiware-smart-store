from pathlib import Path

from models.database import SQLiteRepository


def test_sqlite_repository_crud_and_stats(tmp_path: Path):
    repo = SQLiteRepository(str(tmp_path / "unit.db"))

    store = {"id": "urn:ngsi-ld:Store:001", "type": "Store", "name": "S1"}
    product = {"id": "urn:ngsi-ld:Product:001", "type": "Product", "name": "P1"}

    repo.create_entity(store)
    repo.create_entity(product)

    assert repo.get_entity(store["id"]) is not None
    assert len(repo.list_entities("Store")) == 1

    updated = repo.update_entity(store["id"], {"name": "S2"})
    assert updated is not None
    assert updated["name"] == "S2"

    stats = repo.get_dashboard_stats()
    assert stats["stores"] == 1
    assert stats["products"] == 1

    assert repo.delete_entity(product["id"]) is True
    assert repo.get_entity(product["id"]) is None


def test_sqlite_path_normalization_directory(tmp_path: Path):
    repo = SQLiteRepository(str(tmp_path))
    assert repo.sqlite_path.endswith("fiware.db")
