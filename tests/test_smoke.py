from app import create_app


def test_dashboard_loads():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"fiware-smart-store" in response.data


def test_stores_endpoint_json():
    app = create_app()
    client = app.test_client()

    response = client.get("/stores/?format=json")

    assert response.status_code == 200
    assert response.is_json


def test_language_toggle_spanish_persists_in_session():
    app = create_app()
    client = app.test_client()

    response = client.get("/language/es?next=/", follow_redirects=True)

    assert response.status_code == 200
    assert "Inicio".encode("utf-8") in response.data
    assert "Idioma".encode("utf-8") in response.data

    second = client.get("/")
    assert second.status_code == 200
    assert "Inicio".encode("utf-8") in second.data


def test_language_toggle_back_to_english():
    app = create_app()
    client = app.test_client()

    client.get("/language/es?next=/", follow_redirects=True)
    response = client.get("/language/en?next=/", follow_redirects=True)

    assert response.status_code == 200
    assert b"Home" in response.data
    assert b"Language" in response.data
