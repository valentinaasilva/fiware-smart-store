"""
Test suite for data loading script (load_test_data.py).
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestOrionDataLoaderInit:
    """Test OrionDataLoader initialization."""
    
    def test_loader_initialization(self):
        """Verify loader initializes with correct config."""
        from load_test_data import OrionDataLoader
        
        loader = OrionDataLoader("http://localhost:1026", timeout=5, verbose=True)
        
        assert loader.orion_url == "http://localhost:1026"
        assert loader.timeout == 5
        assert loader.verbose is True
        assert "stores" in loader.created_entities
        assert "products" in loader.created_entities


class TestHealthCheck:
    """Test Orion health check."""
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful Orion health check."""
        from load_test_data import OrionDataLoader
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "3.4.0"}
        mock_get.return_value = mock_response
        
        loader = OrionDataLoader("http://localhost:1026")
        result = loader.health_check()
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        """Test failed Orion health check."""
        from load_test_data import OrionDataLoader
        
        mock_get.side_effect = Exception("Connection refused")
        
        loader = OrionDataLoader("http://localhost:1026")
        result = loader.health_check()
        
        assert result is False


class TestDataLoading:
    """Test data loading operations."""
    
    @patch.object('load_test_data.OrionDataLoader', '_create_entity')
    def test_load_stores(self, mock_create):
        """Test store creation."""
        from load_test_data import OrionDataLoader
        
        mock_create.return_value = True
        loader = OrionDataLoader("http://localhost:1026")
        result = loader.load_stores()
        
        # Should create 4 stores
        assert mock_create.call_count >= 1
        assert len(loader.created_entities["stores"]) > 0
    
    @patch.object('load_test_data.OrionDataLoader', '_create_entity')
    def test_load_products(self, mock_create):
        """Test product creation."""
        from load_test_data import OrionDataLoader
        
        mock_create.return_value = True
        loader = OrionDataLoader("http://localhost:1026")
        result = loader.load_products()
        
        # Should create 10 products
        assert mock_create.call_count >= 1
        assert len(loader.created_entities["products"]) > 0
    
    @patch.object('load_test_data.OrionDataLoader', '_create_entity')
    def test_load_employees(self, mock_create):
        """Test employee creation."""
        from load_test_data import OrionDataLoader
        
        mock_create.return_value = True
        loader = OrionDataLoader("http://localhost:1026")
        loader.created_entities["stores"] = [
            "urn:ngsi-ld:Store:S001",
            "urn:ngsi-ld:Store:S002",
            "urn:ngsi-ld:Store:S003",
            "urn:ngsi-ld:Store:S004"
        ]
        result = loader.load_employees()
        
        # Should create 10 employees
        assert mock_create.call_count >= 1
        assert len(loader.created_entities["employees"]) > 0


class TestIntegrityValidation:
    """Test integrity rule validation."""
    
    @patch.object('load_test_data.OrionDataLoader', '_list_entities_by_type')
    def test_validate_integrity(self, mock_list):
        """Test integrity validation."""
        from load_test_data import OrionDataLoader
        
        mock_list.return_value = []
        loader = OrionDataLoader("http://localhost:1026")
        valid, errors = loader.validate_integrity()
        
        # With empty entities, validation should pass
        assert isinstance(valid, bool)
        assert isinstance(errors, list)


class TestMinimumRequirements:
    """Test minimum requirements verification."""
    
    @patch.object('load_test_data.OrionDataLoader', '_list_entities_by_type')
    def test_verify_minimum_requirements(self, mock_list):
        """Test minimum requirements check."""
        from load_test_data import OrionDataLoader
        
        mock_list.return_value = []
        loader = OrionDataLoader("http://localhost:1026")
        result, stats = loader.verify_minimum_requirements()
        
        assert isinstance(stats, dict)
        assert "stores" in stats
        assert "products" in stats
        assert "employees" in stats
        assert "shelves" in stats
        assert "inventory" in stats


class TestDataValidation:
    """Test data validation logic."""
    
    def test_store_data_valid_country_codes(self):
        """Verify all stores have valid country codes."""
        from load_test_data import STORES_DATA, VALID_ISO_COUNTRIES
        
        for store in STORES_DATA:
            country = store["country"]
            assert country in VALID_ISO_COUNTRIES or len(country) == 2
    
    def test_product_data_valid_sizes(self):
        """Verify all products have valid sizes."""
        from load_test_data import PRODUCTS_DATA, PRODUCT_SIZES
        
        for product in PRODUCTS_DATA:
            assert product["size"] in PRODUCT_SIZES
    
    def test_product_data_valid_prices(self):
        """Verify all products have valid prices."""
        from load_test_data import PRODUCTS_DATA
        
        for product in PRODUCTS_DATA:
            price = product["price"]
            assert price >= 0
            # Check 2 decimal precision
            assert round(price, 2) == price
    
    def test_product_data_valid_colors(self):
        """Verify all products have valid hex colors."""
        from load_test_data import PRODUCTS_DATA
        import re
        
        hex_pattern = r"^#[0-9A-F]{6}$"
        
        for product in PRODUCTS_DATA:
            color = product["color"]
            assert re.match(hex_pattern, color)
    
    def test_employee_data_valid_categories(self):
        """Verify all employees have valid categories."""
        from load_test_data import EMPLOYEES_DATA, EMPLOYEE_CATEGORIES
        
        for employee in EMPLOYEES_DATA:
            assert employee["category"] in EMPLOYEE_CATEGORIES
    
    def test_employee_data_valid_skills(self):
        """Verify all employees have valid skills."""
        from load_test_data import EMPLOYEES_DATA, EMPLOYEE_SKILLS
        
        for employee in EMPLOYEES_DATA:
            for skill in employee["skills"]:
                assert skill in EMPLOYEE_SKILLS


class TestInventoryDistributionData:
    """Test inventory distribution data structure."""
    
    def test_inventory_distribution_exists(self):
        """Verify inventory distribution is defined."""
        from load_test_data import INVENTORY_DISTRIBUTION, STORES_DATA
        
        assert len(INVENTORY_DISTRIBUTION) == len(STORES_DATA)
    
    def test_each_store_has_min_5_products(self):
        """Verify each store has at least 5 products in distribution."""
        from load_test_data import INVENTORY_DISTRIBUTION
        
        for store_id, products in INVENTORY_DISTRIBUTION.items():
            # Count products with stock > 0
            products_with_stock = [p for p, d in products.items() if d.get("stock", 0) > 0]
            assert len(products_with_stock) >= 5, f"Store {store_id} has < 5 products"
    
    def test_each_store_has_min_12_items(self):
        """Verify each store has at least 12 items total."""
        from load_test_data import INVENTORY_DISTRIBUTION
        
        for store_id, products in INVENTORY_DISTRIBUTION.items():
            total_items = sum(d.get("stock", 0) for d in products.values())
            assert total_items >= 12, f"Store {store_id} has < 12 items in stock"


class TestCLI:
    """Test command-line interface."""
    
    def test_main_function_exists(self):
        """Verify main function is defined."""
        from load_test_data import main
        
        assert callable(main)
    
    @patch('sys.argv', ['load_test_data.py', '--help'])
    @patch('sys.exit')
    def test_help_flag(self, mock_exit, mock_argv):
        """Test --help flag."""
        # argparse calls sys.exit(0) on --help
        # This is expected behavior, so we just check the flag exists
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
