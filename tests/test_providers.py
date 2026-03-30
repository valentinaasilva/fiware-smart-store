from __future__ import annotations


def test_weather_provider_query_context(client):
    payload = {
        "entities": [{"type": "Store", "isPattern": "false", "id": "urn:ngsi-ld:Store:S001"}],
        "attributes": ["temperature", "relativeHumidity"],
    }

    response = client.post("/providers/weather/queryContext", json=payload)
    assert response.status_code == 200

    data = response.get_json()
    context = data["contextResponses"][0]["contextElement"]
    attrs = {attr["name"]: attr["value"] for attr in context["attributes"]}

    assert context["id"] == "urn:ngsi-ld:Store:S001"
    assert "temperature" in attrs
    assert "relativeHumidity" in attrs


def test_tweets_provider_query_context(client):
    payload = {
        "entities": [{"type": "Store", "isPattern": "false", "id": "urn:ngsi-ld:Store:S001"}],
        "attributes": ["tweets"],
    }

    response = client.post("/providers/tweets/queryContext", json=payload)
    assert response.status_code == 200

    data = response.get_json()
    context = data["contextResponses"][0]["contextElement"]
    attrs = {attr["name"]: attr["value"] for attr in context["attributes"]}

    assert context["id"] == "urn:ngsi-ld:Store:S001"
    assert "tweets" in attrs
    assert isinstance(attrs["tweets"], list)
    assert len(attrs["tweets"]) > 0
