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
