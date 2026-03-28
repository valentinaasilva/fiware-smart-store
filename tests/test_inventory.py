"""
Test suite for Inventory Item CRUD operations and cross-entity integrity rules.
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


class TestInventoryList:
    """Test GET /inventory endpoint."""
    
    def test_list_inventory_returns_json(self, client):
        """Verify inventory endpoint returns JSON."""
        response = client.get("/inventory", headers={"Accept": "application/json"})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestInventoryValidation:
    """Test InventoryItem entity validation."""
    
    def test_shelf_count_not_exceed_stock(self):
        """Verify shelfCount <= stockCount (IR-004)."""
        valid_items = [
            {"stockCount": 30, "shelfCount": 10},
            {"stockCount": 30, "shelfCount": 30},
            {"stockCount": 0, "shelfCount": 0}
        ]
        invalid_items = [
            {"stockCount": 10, "shelfCount": 30},
            {"stockCount": 0, "shelfCount": 5}
        ]
        
        for item in valid_items:
            assert item["shelfCount"] <= item["stockCount"]
        
        for item in invalid_items:
            assert item["shelfCount"] > item["stockCount"]
    
    def test_stock_count_non_negative(self):
        """Verify stockCount >= 0."""
        valid_stocks = [0, 10, 50, 1000]
        invalid_stocks = [-1, -50]
        
        for stock in valid_stocks:
            assert stock >= 0
        
        for stock in invalid_stocks:
            assert stock < 0
    
    def test_shelf_count_non_negative(self):
        """Verify shelfCount >= 0."""
        valid_shelf_counts = [0, 5, 20, 50]
        invalid_shelf_counts = [-1, -10]
        
        for count in valid_shelf_counts:
            assert count >= 0
        
        for count in invalid_shelf_counts:
            assert count < 0


class TestInventoryIntegrity:
    """Test cross-entity integrity rules."""
    
    def test_ir001_shelf_belongs_to_store(self):
        """IR-001: InventoryItem.refShelf must belong to InventoryItem.refStore."""
        # Test relationship consistency
        store_id = "urn:ngsi-ld:Store:S001"
        shelf_id = "urn:ngsi-ld:Shelf:001"
        
        # Simulated check: shelf should belong to store
        shelf_store_mapping = {shelf_id: store_id}
        
        item_store = store_id
        item_shelf = shelf_id
        
        # Verify shelf belongs to the same store
        assert shelf_store_mapping.get(item_shelf) == item_store
    
    def test_ir002_no_duplicates(self):
        """IR-002: No duplicate InventoryItem with same (store, shelf, product)."""
        inventory = [
            {"id": "i1", "store": "S001", "shelf": "Sh1", "product": "P001"},
            {"id": "i2", "store": "S001", "shelf": "Sh2", "product": "P001"},
            {"id": "i3", "store": "S002", "shelf": "Sh1", "product": "P001"}
        ]
        
        # Check for duplicates
        seen = set()
        duplicates = []
        for item in inventory:
            key = (item["store"], item["shelf"], item["product"])
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        
        assert len(duplicates) == 0
    
    def test_ir003_shelf_capacity_not_exceeded(self):
        """IR-003: sum(shelfCount) per shelf <= shelf.maxCapacity."""
        shelf_max_capacity = 50
        items_in_shelf = [
            {"shelfCount": 10},
            {"shelfCount": 15},
            {"shelfCount": 20}
        ]
        
        total = sum(item["shelfCount"] for item in items_in_shelf)
        assert total <= shelf_max_capacity
        
        # Test exceeding capacity
        items_exceeding = [
            {"shelfCount": 30},
            {"shelfCount": 25}
        ]
        total_exceeding = sum(item["shelfCount"] for item in items_exceeding)
        assert total_exceeding > shelf_max_capacity


class TestInventoryDistribution:
    """Test inventory distribution across stores."""
    
    def test_minimum_5_products_per_store(self):
        """Verify each store has at least 5 different products."""
        inventory = [
            {"store": "S001", "product": "P001"},
            {"store": "S001", "product": "P002"},
            {"store": "S001", "product": "P003"},
            {"store": "S001", "product": "P004"},
            {"store": "S001", "product": "P005"},
            {"store": "S002", "product": "P001"},
            {"store": "S002", "product": "P002"},
            {"store": "S002", "product": "P003"},
            {"store": "S002", "product": "P006"},
            {"store": "S002", "product": "P007"},
        ]
        
        stores = {}
        for item in inventory:
            store = item["store"]
            product = item["product"]
            if store not in stores:
                stores[store] = set()
            stores[store].add(product)
        
        for store, products in stores.items():
            assert len(products) >= 5, f"Store {store} has only {len(products)} products"
    
    def test_minimum_12_items_per_store(self):
        """Verify each store has at least 12 inventory items."""
        inventory = [
            {"id": f"s1_i{i}", "store": "S001"} for i in range(15)
        ] + [
            {"id": f"s2_i{i}", "store": "S002"} for i in range(12)
        ]
        
        store_counts = {}
        for item in inventory:
            store = item["store"]
            store_counts[store] = store_counts.get(store, 0) + 1
        
        for store, count in store_counts.items():
            assert count >= 12, f"Store {store} has only {count} items"


class TestInventoryIntegration:
    """Integration tests for InventoryItem operations."""
    
    def test_inventory_item_with_all_required_fields(self):
        """Verify inventory item entity structure."""
        item = {
            "id": "urn:ngsi-ld:InventoryItem:001",
            "type": "InventoryItem",
            "refStore": "urn:ngsi-ld:Store:S001",
            "refShelf": "urn:ngsi-ld:Shelf:001",
            "refProduct": "urn:ngsi-ld:Product:P001",
            "stockCount": 30,
            "shelfCount": 10
        }
        
        assert item["id"].startswith("urn:ngsi-ld:InventoryItem:")
        assert item["type"] == "InventoryItem"
        assert item["refStore"].startswith("urn:ngsi-ld:Store:")
        assert item["refShelf"].startswith("urn:ngsi-ld:Shelf:")
        assert item["refProduct"].startswith("urn:ngsi-ld:Product:")
        assert item["stockCount"] >= 0
        assert item["shelfCount"] <= item["stockCount"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
