from pathlib import Path

from models.data_source import DataSourceSelector


def test_bootstrap_uses_sqlite_when_orion_down(tmp_path: Path):
    selector = DataSourceSelector("http://127.0.0.1:9", str(tmp_path / "ds.db"))
    selector.bootstrap()
    assert selector.mode == "SQLITE"


def test_bootstrap_uses_orion_when_healthy(tmp_path: Path):
    selector = DataSourceSelector("http://dummy", str(tmp_path / "ds2.db"))
    selector.orion.health_check = lambda: True
    selector.orion.register_provider = lambda payload: True
    selector.orion.register_subscription = lambda payload: True

    selector.bootstrap()
    assert selector.mode == "ORION"


def test_fallback_to_sqlite_on_orion_error(tmp_path: Path):
    selector = DataSourceSelector("http://dummy", str(tmp_path / "ds3.db"))
    selector.mode = "ORION"

    selector.sqlite.create_entity({"id": "urn:ngsi-ld:Store:001", "type": "Store", "name": "S1"})

    def raise_error(*_args, **_kwargs):
        raise RuntimeError("orion down")

    selector.orion.list_entities = raise_error

    entities = selector.list_entities("Store")
    assert selector.mode == "SQLITE"
    assert len(entities) == 1
