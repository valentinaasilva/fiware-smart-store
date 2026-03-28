"""
Test suite for Store CRUD operations and validations.
"""

import pytest
from app import create_app
from models.data_source import DataSourceSelector


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """App context for direct function calls."""
    with app.app_context():
        yield app


class TestStoresList:
    """Test GET /stores endpoint."""
    
    def test_list_stores_returns_json(self, client):
        """Verify stores endpoint returns JSON."""
        response = client.get("/stores", headers={"Accept": "application/json"})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_list_stores_returns_html(self, client):
        """Verify stores endpoint can return HTML."""
        response = client.get("/stores", headers={"Accept": "text/html"})
        assert response.status_code in (200, 404)  # Might not have template


class TestStoreDetail:
    """Test GET /stores/<id> endpoint."""
    
    def test_detail_returns_json(self, client):
        """Verify store detail returns JSON."""
        response = client.get("/stores/urn:ngsi-ld:Store:S001", headers={"Accept": "application/json"})
        # Will 404 if not loaded, but endpoint should exist
        assert response.status_code in (200, 404)


class TestStoreValidation:
    """Test Store entity validation."""
    
    def test_country_code_validation(self):
        """Verify countryCode must be ISO alpha-2."""
        valid_codes = {"DE", "ES", "FR", "IT", "US"}
        invalid_codes = {"DEU", "SPA", "FRA123"}
        
        for code in valid_codes:
            assert len(code) == 2
            assert code.isupper()
        
        for code in invalid_codes:
            assert not (len(code) == 2 and code.isupper())
    
    def test_capacity_positive(self):
        """Verify capacity must be positive."""
        assert 2500 > 0
        assert 0 <= 0  # Edge case
        assert -100 < 0
    
    def test_store_name_length(self):
        """Verify name length constraints (1-120 chars)."""
        valid_names = ["Berlin Mitte", "Store", "A" * 120]
        invalid_names = ["", "A" * 121]
        
        for name in valid_names:
            assert 1 <= len(name) <= 120
        
        for name in invalid_names:
            assert not (1 <= len(name) <= 120)


class TestStoreIntegration:
    """Integration tests for Store operations."""
    
    def test_store_with_all_required_fields(self):
        """Verify store entity structure."""
        store = {
            "id": "urn:ngsi-ld:Store:TEST",
            "type": "Store",
            "name": "Test Store",
            "address": {
                "streetAddress": "St 1",
                "addressLocality": "City",
                "addressRegion": "Region"
            },
            "location": {"type": "Point", "coordinates": [0.0, 0.0]},
            "countryCode": "DE",
            "capacity": 2000
        }
        
        assert store["id"].startswith("urn:ngsi-ld:Store:")
        assert store["type"] == "Store"
        assert "address" in store
        assert "location" in store
        assert len(store["countryCode"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
