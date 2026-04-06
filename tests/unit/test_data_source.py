from pathlib import Path

from models.data_source import DataSourceSelector


def test_bootstrap_uses_sqlite_when_orion_down(tmp_path: Path):
    selector = DataSourceSelector("http://127.0.0.1:9", str(tmp_path / "ds.db"))
    selector.bootstrap()
    assert selector.mode == "SQLITE"


def test_bootstrap_uses_orion_when_healthy(tmp_path: Path):
    selector = DataSourceSelector("http://dummy", str(tmp_path / "ds2.db"))
    provider_calls = []
    subscription_calls = []

    selector.orion.health_check = lambda: True
    selector.orion.list_entities = lambda entity_type=None: [
        {"id": "urn:ngsi-ld:Store:S001", "type": "Store"},
        {"id": "urn:ngsi-ld:Store:S002", "type": "Store"},
    ]
    selector.orion.register_provider = lambda payload: provider_calls.append(payload) or True
    selector.orion.register_subscription = lambda payload: subscription_calls.append(payload) or True

    selector.bootstrap()

    assert selector.mode == "ORION"
    assert len(provider_calls) == 4
    assert len(subscription_calls) == 2

    attrs_sets = [tuple(call["dataProvided"]["attrs"]) for call in provider_calls]
    assert ("temperature", "relativeHumidity") in attrs_sets
    assert ("tweets",) in attrs_sets
    entity_ids = [call["dataProvided"]["entities"][0]["id"] for call in provider_calls]
    assert "urn:ngsi-ld:Store:S001" in entity_ids
    assert "urn:ngsi-ld:Store:S002" in entity_ids


def test_bootstrap_uses_provider_urls_from_environment(tmp_path: Path, monkeypatch):
    selector = DataSourceSelector("http://dummy", str(tmp_path / "ds4.db"))
    provider_calls = []

    monkeypatch.setenv("WEATHER_PROVIDER_URL", "http://providers/weather")
    monkeypatch.setenv("TWEETS_PROVIDER_URL", "http://providers/tweets")

    selector.orion.health_check = lambda: True
    selector.orion.list_entities = lambda entity_type=None: [
        {"id": "urn:ngsi-ld:Store:S001", "type": "Store"}
    ]
    selector.orion.register_provider = lambda payload: provider_calls.append(payload) or True
    selector.orion.register_subscription = lambda payload: True

    selector.bootstrap()

    urls = [call["provider"]["http"]["url"] for call in provider_calls]
    assert "http://providers/weather" in urls
    assert "http://providers/tweets" in urls


def test_bootstrap_does_not_crash_when_integrations_fail(tmp_path: Path):
    selector = DataSourceSelector("http://dummy", str(tmp_path / "ds6.db"))

    selector.orion.health_check = lambda: True
    selector.orion.list_entities = lambda entity_type=None: (_ for _ in ()).throw(RuntimeError("orion busy"))

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


def test_create_store_registers_context_providers_in_orion_mode(tmp_path: Path):
    selector = DataSourceSelector("http://dummy", str(tmp_path / "ds5.db"))
    selector.mode = "ORION"

    provider_calls = []

    selector.orion.create_entity = lambda entity: entity
    selector.orion.register_provider = lambda payload: provider_calls.append(payload) or True

    created = selector.create_entity({"id": "urn:ngsi-ld:Store:S010", "type": "Store", "name": "Store 10"})

    assert created["id"] == "urn:ngsi-ld:Store:S010"
    assert len(provider_calls) == 2
    attrs_sets = [tuple(call["dataProvided"]["attrs"]) for call in provider_calls]
    assert ("temperature", "relativeHumidity") in attrs_sets
    assert ("tweets",) in attrs_sets
