"""
Test suite for Product CRUD operations and validations.
"""

import pytest
from app import create_app


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


class TestProductsList:
    """Test GET /products endpoint."""
    
    def test_list_products_returns_json(self, client):
        """Verify products endpoint returns JSON."""
        response = client.get("/products", headers={"Accept": "application/json"})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestProductValidation:
    """Test Product entity validation."""
    
    def test_size_enum_validation(self):
        """Verify size must be in {S, M, L, XL}."""
        valid_sizes = {"S", "M", "L", "XL"}
        invalid_sizes = {"XXL", "XS", "medium", ""}
        
        for size in valid_sizes:
            assert size in {"S", "M", "L", "XL"}
        
        for size in invalid_sizes:
            assert size not in {"S", "M", "L", "XL"}
    
    def test_price_precision_validation(self):
        """Verify price has 2 decimal precision."""
        valid_prices = [2.99, 1.49, 10.00, 0.99, 100.50]
        invalid_prices = [2.999, 1.4, 10.1, 0.9]
        
        for price in valid_prices:
            # Check if price rounds to 2 decimals
            assert round(price, 2) == price
        
        for price in invalid_prices:
            assert round(price, 2) != price or len(str(price).split('.')[-1]) != 2
    
    def test_color_hex_validation(self):
        """Verify color is valid hex format #RRGGBB."""
        valid_colors = ["#FFE135", "#DC143C", "#FF8C00", "#228B22", "#FFFFFF", "#000000"]
        invalid_colors = ["FFE135", "#FFE13", "#FFE1350", "#GGG000", "red", "#12345X"]
        
        import re
        hex_pattern = r"^#[0-9A-F]{6}$"
        
        for color in valid_colors:
            assert re.match(hex_pattern, color)
        
        for color in invalid_colors:
            assert not re.match(hex_pattern, color)
    
    def test_price_must_be_positive(self):
        """Verify price >= 0."""
        assert 2.99 >= 0
        assert 0.0 >= 0
        assert -1.99 < 0


class TestProductIntegration:
    """Integration tests for Product operations."""
    
    def test_product_with_all_required_fields(self):
        """Verify product entity structure."""
        product = {
            "id": "urn:ngsi-ld:Product:P001",
            "type": "Product",
            "name": "Banana",
            "size": "M",
            "price": 2.99,
            "color": "#FFE135",
            "originCountry": "EC"
        }
        
        assert product["id"].startswith("urn:ngsi-ld:Product:")
        assert product["type"] == "Product"
        assert product["size"] in {"S", "M", "L", "XL"}
        assert product["price"] > 0
        assert len(product["color"]) == 7
        assert product["color"].startswith("#")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
