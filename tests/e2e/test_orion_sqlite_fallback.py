def test_route_write_falls_back_to_sqlite_when_orion_fails(app, client, sample_store):
    selector = app.extensions["data_selector"]

    selector.mode = "ORION"

    def fail_create(_entity):
        raise RuntimeError("orion unavailable")

    selector.orion.create_entity = fail_create

    response = client.post("/stores/", json=sample_store)
    assert response.status_code == 201
    assert selector.mode == "SQLITE"

    persisted = selector.sqlite.get_entity(sample_store["id"])
    assert persisted is not None


def test_route_read_falls_back_to_sqlite_when_orion_fails(app, client, sample_store):
    selector = app.extensions["data_selector"]
    selector.sqlite.create_entity(sample_store)

    selector.mode = "ORION"

    def fail_list(_entity_type=None):
        raise RuntimeError("orion unavailable")

    selector.orion.list_entities = fail_list

    response = client.get("/stores?format=json")
    assert response.status_code == 200
    assert selector.mode == "SQLITE"

    data = response.get_json()
    assert any(entity["id"] == sample_store["id"] for entity in data)
