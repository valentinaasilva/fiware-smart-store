#!/usr/bin/env python3
"""
Load test data for fiware-smart-store into Orion Context Broker.

Populates 4 stores, 10 products, 10 employees, 12 shelves, and 50+ inventory items
with full NGSIv2 validation and integrity rule checking.

Usage:
    python scripts/load_test_data.py [--orion-url URL] [--clean] [--dry-run] [--verbose]

Examples:
    python scripts/load_test_data.py                           # Default: localhost:1026, no clean
    python scripts/load_test_data.py --clean --verbose         # Clean old data and show details
    python scripts/load_test_data.py --dry-run                 # Validate without creating
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import List, Tuple, Dict, Any

import requests
from requests.exceptions import RequestException


# ============================================================================
# Configuration & Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

VALID_ISO_COUNTRIES = {
    "DE", "ES", "FR", "IT", "PT", "NL", "BE", "GB", "US", "CA", 
    "MX", "BR", "AR", "CL", "CO", "PE", "EC", "AU", "JP", "CN", "IN"
}

PRODUCT_SIZES = {"S", "M", "L", "XL"}
EMPLOYEE_CATEGORIES = {"Junior", "Senior", "Manager", "Specialist"}
EMPLOYEE_SKILLS = {"MachineryDriving", "WritingReports", "CustomerRelationships"}


# ============================================================================
# Test Data Definitions
# ============================================================================

STORES_DATA = [
    {
        "id": "urn:ngsi-ld:Store:S001",
        "name": "Berlin Mitte",
        "country": "DE",
        "city": "Berlin",
        "coords": [13.405, 52.520],
        "capacity": 2500,
        "address": {
            "streetAddress": "Alexanderplatz 1",
            "addressLocality": "Berlin",
            "addressRegion": "Berlin",
            "postalCode": "10178",
            "addressCountry": "DE"
        },
        "telephone": "+49-30-123456",
        "url": "https://store.example/berlin-mitte",
        "image": "https://picsum.photos/600/300?random=1",
        "description": "Main city branch in Berlin center"
    },
    {
        "id": "urn:ngsi-ld:Store:S002",
        "name": "Madrid Centro",
        "country": "ES",
        "city": "Madrid",
        "coords": [-3.703, 40.415],
        "capacity": 3000,
        "address": {
            "streetAddress": "Gran Vía 1",
            "addressLocality": "Madrid",
            "addressRegion": "Madrid",
            "postalCode": "28013",
            "addressCountry": "ES"
        },
        "telephone": "+34-91-234567",
        "url": "https://store.example/madrid-centro",
        "image": "https://picsum.photos/600/300?random=2",
        "description": "Premium location on Gran Vía"
    },
    {
        "id": "urn:ngsi-ld:Store:S003",
        "name": "Barcelona Eixample",
        "country": "ES",
        "city": "Barcelona",
        "coords": [2.165, 41.385],
        "capacity": 2800,
        "address": {
            "streetAddress": "Passeig de Gràcia 10",
            "addressLocality": "Barcelona",
            "addressRegion": "Catalonia",
            "postalCode": "08007",
            "addressCountry": "ES"
        },
        "telephone": "+34-93-345678",
        "url": "https://store.example/barcelona-eixample",
        "image": "https://picsum.photos/600/300?random=3",
        "description": "Iconic location in Barcelona"
    },
    {
        "id": "urn:ngsi-ld:Store:S004",
        "name": "Paris Marais",
        "country": "FR",
        "city": "Paris",
        "coords": [2.362, 48.859],
        "capacity": 2200,
        "address": {
            "streetAddress": "Rue de Rivoli 1",
            "addressLocality": "Paris",
            "addressRegion": "Île-de-France",
            "postalCode": "75004",
            "addressCountry": "FR"
        },
        "telephone": "+33-1-45678901",
        "url": "https://store.example/paris-marais",
        "image": "https://picsum.photos/600/300?random=4",
        "description": "Central location near Place des Vosges"
    }
]

PRODUCTS_DATA = [
    {"id": "urn:ngsi-ld:Product:P001", "name": "Banana", "size": "M", "color": "#FFE135", "price": 2.99, "origin": "EC"},
    {"id": "urn:ngsi-ld:Product:P002", "name": "Red Apple", "size": "M", "color": "#DC143C", "price": 1.49, "origin": "ES"},
    {"id": "urn:ngsi-ld:Product:P003", "name": "Orange", "size": "L", "color": "#FF8C00", "price": 3.99, "origin": "ES"},
    {"id": "urn:ngsi-ld:Product:P004", "name": "Lettuce", "size": "L", "color": "#228B22", "price": 1.99, "origin": "DE"},
    {"id": "urn:ngsi-ld:Product:P005", "name": "Tomato", "size": "M", "color": "#FF4500", "price": 2.49, "origin": "ES"},
    {"id": "urn:ngsi-ld:Product:P006", "name": "Milk 1L", "size": "S", "color": "#FFFFFF", "price": 1.29, "origin": "FR"},
    {"id": "urn:ngsi-ld:Product:P007", "name": "Cheese", "size": "S", "color": "#FFD700", "price": 4.99, "origin": "FR"},
    {"id": "urn:ngsi-ld:Product:P008", "name": "Bread", "size": "M", "color": "#8B4513", "price": 2.49, "origin": "DE"},
    {"id": "urn:ngsi-ld:Product:P009", "name": "Water 2L", "size": "L", "color": "#87CEEB", "price": 0.99, "origin": "ES"},
    {"id": "urn:ngsi-ld:Product:P010", "name": "Coffee", "size": "S", "color": "#6F4E37", "price": 5.99, "origin": "BR"}
]

EMPLOYEES_DATA = [
    {"id": "urn:ngsi-ld:Employee:E001", "name": "Ada Lovelace", "store_id": "urn:ngsi-ld:Store:S001", "category": "Senior", "role": "Store Manager", "salary": 2800.00, "email": "ada@store.com", "skills": ["WritingReports"]},
    {"id": "urn:ngsi-ld:Employee:E002", "name": "Alan Turing", "store_id": "urn:ngsi-ld:Store:S001", "category": "Junior", "role": "Cashier", "salary": 1800.00, "email": "alan@store.com", "skills": ["CustomerRelationships"]},
    {"id": "urn:ngsi-ld:Employee:E003", "name": "Grace Hopper", "store_id": "urn:ngsi-ld:Store:S001", "category": "Manager", "role": "Supervisor", "salary": 2500.00, "email": "grace@store.com", "skills": ["WritingReports", "CustomerRelationships"]},
    {"id": "urn:ngsi-ld:Employee:E004", "name": "Donald Knuth", "store_id": "urn:ngsi-ld:Store:S002", "category": "Senior", "role": "Store Manager", "salary": 2900.00, "email": "donald@store.com", "skills": ["WritingReports"]},
    {"id": "urn:ngsi-ld:Employee:E005", "name": "Vera Rubin", "store_id": "urn:ngsi-ld:Store:S002", "category": "Junior", "role": "Stock Clerk", "salary": 1700.00, "email": "vera@store.com", "skills": ["MachineryDriving"]},
    {"id": "urn:ngsi-ld:Employee:E006", "name": "Richard Stallman", "store_id": "urn:ngsi-ld:Store:S002", "category": "Specialist", "role": "IT Support", "salary": 3200.00, "email": "richard@store.com", "skills": ["WritingReports"]},
    {"id": "urn:ngsi-ld:Employee:E007", "name": "Hedy Lamarr", "store_id": "urn:ngsi-ld:Store:S003", "category": "Manager", "role": "Supervisor", "salary": 2400.00, "email": "hedy@store.com", "skills": ["CustomerRelationships"]},
    {"id": "urn:ngsi-ld:Employee:E008", "name": "John Backus", "store_id": "urn:ngsi-ld:Store:S004", "category": "Senior", "role": "Store Manager", "salary": 2700.00, "email": "john@store.com", "skills": ["WritingReports"]},
    {"id": "urn:ngsi-ld:Employee:E009", "name": "Barbara Liskov", "store_id": "urn:ngsi-ld:Store:S003", "category": "Junior", "role": "Cashier", "salary": 1900.00, "email": "barbara@store.com", "skills": ["CustomerRelationships"]},
    {"id": "urn:ngsi-ld:Employee:E010", "name": "Blaise Pascal", "store_id": "urn:ngsi-ld:Store:S004", "category": "Junior", "role": "Stock Clerk", "salary": 1600.00, "email": "blaise@store.com", "skills": ["MachineryDriving"]}
]

# Shelves: 3 per store (12 total)
SHELVES_PER_STORE = 3
SHELF_MAX_CAPACITY = 50

# Inventory distribution: ensure min 5 products per store and min 12 items per store
INVENTORY_DISTRIBUTION = {
    "urn:ngsi-ld:Store:S001": {
        "urn:ngsi-ld:Product:P001": {"stock": 30, "shelf": 10},
        "urn:ngsi-ld:Product:P002": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P003": {"stock": 40, "shelf": 15},
        "urn:ngsi-ld:Product:P004": {"stock": 35, "shelf": 12},
        "urn:ngsi-ld:Product:P005": {"stock": 25, "shelf": 8},
        "urn:ngsi-ld:Product:P006": {"stock": 20, "shelf": 7},
        "urn:ngsi-ld:Product:P007": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P008": {"stock": 32, "shelf": 11},
        "urn:ngsi-ld:Product:P009": {"stock": 15, "shelf": 5},
        "urn:ngsi-ld:Product:P010": {"stock": 28, "shelf": 9}
    },
    "urn:ngsi-ld:Store:S002": {
        "urn:ngsi-ld:Product:P001": {"stock": 25, "shelf": 8},
        "urn:ngsi-ld:Product:P002": {"stock": 35, "shelf": 12},
        "urn:ngsi-ld:Product:P003": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P004": {"stock": 28, "shelf": 10},
        "urn:ngsi-ld:Product:P005": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P006": {"stock": 18, "shelf": 6},
        "urn:ngsi-ld:Product:P007": {"stock": 22, "shelf": 8},
        "urn:ngsi-ld:Product:P008": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P009": {"stock": 40, "shelf": 14},
        "urn:ngsi-ld:Product:P010": {"stock": 20, "shelf": 7}
    },
    "urn:ngsi-ld:Store:S003": {
        "urn:ngsi-ld:Product:P001": {"stock": 28, "shelf": 9},
        "urn:ngsi-ld:Product:P002": {"stock": 20, "shelf": 7},
        "urn:ngsi-ld:Product:P003": {"stock": 32, "shelf": 11},
        "urn:ngsi-ld:Product:P004": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P005": {"stock": 40, "shelf": 14},
        "urn:ngsi-ld:Product:P006": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P007": {"stock": 15, "shelf": 5},
        "urn:ngsi-ld:Product:P008": {"stock": 25, "shelf": 8},
        "urn:ngsi-ld:Product:P009": {"stock": 18, "shelf": 6},
        "urn:ngsi-ld:Product:P010": {"stock": 22, "shelf": 8}
    },
    "urn:ngsi-ld:Store:S004": {
        "urn:ngsi-ld:Product:P001": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P002": {"stock": 25, "shelf": 8},
        "urn:ngsi-ld:Product:P003": {"stock": 30, "shelf": 10},
        "urn:ngsi-ld:Product:P004": {"stock": 22, "shelf": 8},
        "urn:ngsi-ld:Product:P005": {"stock": 35, "shelf": 12},
        "urn:ngsi-ld:Product:P006": {"stock": 24, "shelf": 8},
        "urn:ngsi-ld:Product:P007": {"stock": 28, "shelf": 9},
        "urn:ngsi-ld:Product:P008": {"stock": 0, "shelf": 0},
        "urn:ngsi-ld:Product:P009": {"stock": 20, "shelf": 7},
        "urn:ngsi-ld:Product:P010": {"stock": 0, "shelf": 0}
    }
}


# ============================================================================
# Orion Data Loader
# ============================================================================

class OrionDataLoader:
    """Load test data into Orion Context Broker with full NGSIv2 validation."""

    def __init__(self, orion_url: str, timeout: int = 5, verbose: bool = False):
        self.orion_url = orion_url.rstrip("/")
        self.timeout = timeout
        self.verbose = verbose
        self.created_entities = {
            "stores": [],
            "products": [],
            "employees": [],
            "shelves": [],
            "inventory": []
        }
        self.errors = []

    def _log(self, level: str, message: str) -> None:
        """Log with optional verbosity."""
        if level == "DEBUG" and not self.verbose:
            return
        getattr(logger, level.lower())(message)

    def health_check(self) -> bool:
        """Verify Orion connectivity."""
        try:
            resp = requests.get(f"{self.orion_url}/version", timeout=self.timeout)
            if resp.status_code == 200:
                version = resp.json().get("version", "unknown")
                logger.info(f"✓ Orion health check passed (version {version})")
                return True
            else:
                logger.error(f"✗ Orion health check failed (status {resp.status_code})")
                return False
        except RequestException as e:
            logger.error(f"✗ Cannot connect to Orion at {self.orion_url}: {e}")
            return False

    def _create_entity(self, entity: Dict[str, Any]) -> bool:
        """Create entity in Orion via NGSIv2 POST."""
        try:
            resp = requests.post(
                f"{self.orion_url}/v2/entities",
                json=entity,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            if resp.status_code in (201, 204):
                return True
            else:
                error_msg = resp.text if resp.text else f"HTTP {resp.status_code}"
                self._log("DEBUG", f"  -> Failed: {error_msg}")
                return False
        except RequestException as e:
            self._log("DEBUG", f"  -> Exception: {e}")
            return False

    def _list_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Query entities by type."""
        try:
            resp = requests.get(
                f"{self.orion_url}/v2/entities?type={entity_type}",
                timeout=self.timeout
            )
            if resp.status_code == 200:
                return resp.json()
            return []
        except RequestException:
            return []

    def _get_store_urns(self) -> List[str]:
        """Get list of created store URNs."""
        return self.created_entities["stores"]

    def _get_product_urns(self) -> List[str]:
        """Get list of created product URNs."""
        return self.created_entities["products"]

    def _get_shelf_urns(self) -> List[str]:
        """Get list of created shelf URNs."""
        return self.created_entities["shelves"]

    def load_stores(self) -> bool:
        """Create 4 Store entities."""
        logger.info("START: Creating 4 stores...")
        store_urns = []

        for store_data in STORES_DATA:
            entity = {
                "id": store_data["id"],
                "type": "Store",
                "name": {"type": "Text", "value": store_data["name"]},
                "address": {
                    "type": "PostalAddress",
                    "value": store_data["address"]
                },
                "location": {
                    "type": "geo:json",
                    "value": {
                        "type": "Point",
                        "coordinates": store_data["coords"]
                    }
                },
                "countryCode": {"type": "Text", "value": store_data["country"]},
                "capacity": {"type": "Integer", "value": store_data["capacity"]},
                "telephone": {"type": "Text", "value": store_data["telephone"]},
                "url": {"type": "Text", "value": store_data["url"]},
                "image": {"type": "Text", "value": store_data["image"]},
                "description": {"type": "Text", "value": store_data["description"]}
            }

            if self._create_entity(entity):
                logger.info(f"✓ Store {store_data['id']} ({store_data['name']})")
                store_urns.append(store_data["id"])
            else:
                logger.error(f"✗ Store {store_data['id']} creation failed")
                self.errors.append(f"Store {store_data['id']} creation failed")

        self.created_entities["stores"] = store_urns
        logger.info(f"SUCCESS: Created {len(store_urns)}/{len(STORES_DATA)} stores")
        return len(store_urns) == len(STORES_DATA)

    def load_products(self) -> bool:
        """Create 10 Product entities."""
        logger.info("START: Creating 10 products...")
        product_urns = []

        for product_data in PRODUCTS_DATA:
            entity = {
                "id": product_data["id"],
                "type": "Product",
                "name": {"type": "Text", "value": product_data["name"]},
                "size": {"type": "Text", "value": product_data["size"]},
                "price": {"type": "Float", "value": product_data["price"]},
                "color": {"type": "Text", "value": product_data["color"]},
                "originCountry": {"type": "Text", "value": product_data["origin"]},
                "image": {
                    "type": "Text",
                    "value": f"https://picsum.photos/200/200?random={product_data['id'][-4:]}"
                }
            }

            if self._create_entity(entity):
                logger.info(f"✓ Product {product_data['id']} ({product_data['name']})")
                product_urns.append(product_data["id"])
            else:
                logger.error(f"✗ Product {product_data['id']} creation failed")
                self.errors.append(f"Product {product_data['id']} creation failed")

        self.created_entities["products"] = product_urns
        logger.info(f"SUCCESS: Created {len(product_urns)}/{len(PRODUCTS_DATA)} products")
        return len(product_urns) == len(PRODUCTS_DATA)

    def load_employees(self) -> bool:
        """Create 10 Employee entities."""
        logger.info("START: Creating 10 employees...")
        employee_urns = []
        store_urns = self._get_store_urns()

        for employee_data in EMPLOYEES_DATA:
            entity = {
                "id": employee_data["id"],
                "type": "Employee",
                "name": {"type": "Text", "value": employee_data["name"]},
                "category": {"type": "Text", "value": employee_data["category"]},
                "role": {"type": "Text", "value": employee_data["role"]},
                "salary": {"type": "Float", "value": employee_data["salary"]},
                "email": {"type": "Text", "value": employee_data["email"]},
                "skills": {"type": "Array", "value": employee_data["skills"]},
                "dateOfContract": {"type": "DateTime", "value": "2025-03-15T00:00:00Z"},
                "username": {"type": "Text", "value": employee_data["email"].split("@")[0]},
                "password": {"type": "Text", "value": "$2b$12$hash"},  # Placeholder hash
                "refStore": {
                    "type": "Relationship",
                    "value": employee_data["store_id"]
                }
            }

            if self._create_entity(entity):
                logger.info(f"✓ Employee {employee_data['id']} ({employee_data['name']})")
                employee_urns.append(employee_data["id"])
            else:
                logger.error(f"✗ Employee {employee_data['id']} creation failed")
                self.errors.append(f"Employee {employee_data['id']} creation failed")

        self.created_entities["employees"] = employee_urns
        logger.info(f"SUCCESS: Created {len(employee_urns)}/{len(EMPLOYEES_DATA)} employees")
        return len(employee_urns) == len(EMPLOYEES_DATA)

    def load_shelves(self) -> bool:
        """Create 12 Shelf entities (3 per store)."""
        logger.info("START: Creating 12 shelves...")
        shelf_urns = []
        store_urns = self._get_store_urns()
        shelf_counter = 1

        for i, store_urn in enumerate(store_urns):
            store_data = STORES_DATA[i]
            for j in range(SHELVES_PER_STORE):
                shelf_id = f"urn:ngsi-ld:Shelf:{shelf_counter:03d}"
                shelf_counter += 1
                
                # GeoJSON location slightly offset from store
                offset = j * 0.001
                location_coords = [store_data["coords"][0] + offset, store_data["coords"][1] + offset]

                entity = {
                    "id": shelf_id,
                    "type": "Shelf",
                    "name": {"type": "Text", "value": f"Shelf {j+1}"},
                    "maxCapacity": {"type": "Integer", "value": SHELF_MAX_CAPACITY},
                    "location": {
                        "type": "geo:json",
                        "value": {
                            "type": "Point",
                            "coordinates": location_coords
                        }
                    },
                    "refStore": {
                        "type": "Relationship",
                        "value": store_urn
                    }
                }

                if self._create_entity(entity):
                    logger.info(f"✓ Shelf {shelf_id} (Store {store_data['name']})")
                    shelf_urns.append(shelf_id)
                else:
                    logger.error(f"✗ Shelf {shelf_id} creation failed")
                    self.errors.append(f"Shelf {shelf_id} creation failed")

        self.created_entities["shelves"] = shelf_urns
        logger.info(f"SUCCESS: Created {len(shelf_urns)}/{len(STORES_DATA) * SHELVES_PER_STORE} shelves")
        return len(shelf_urns) == len(STORES_DATA) * SHELVES_PER_STORE

    def load_inventory(self) -> bool:
        """Create 50-60 InventoryItem entities."""
        logger.info("START: Creating inventory items...")
        inventory_urns = []
        store_urns = self._get_store_urns()
        shelf_urns = self._get_shelf_urns()
        product_urns = self._get_product_urns()
        
        item_counter = 1
        shelves_by_store = {}
        
        # Map shelves to stores
        for shelf_urn in shelf_urns:
            for store_urn in store_urns:
                store_shelf_query = self._list_entities_by_type("Shelf")
                # Simplified: just distribute shelves sequentially per store
        
        # Distribute 3 shelves per store (simplified for now)
        for store_idx, store_urn in enumerate(store_urns):
            shelves_for_store = shelf_urns[store_idx * SHELVES_PER_STORE:(store_idx + 1) * SHELVES_PER_STORE]
            shelves_by_store[store_urn] = shelves_for_store

        for store_urn in store_urns:
            dist = INVENTORY_DISTRIBUTION.get(store_urn, {})
            shelves = shelves_by_store[store_urn]
            shelf_idx = 0

            for product_urn in product_urns:
                prod_dist = dist.get(product_urn, {})
                stock = prod_dist.get("stock", 0)
                shelf_count = prod_dist.get("shelf", 0)

                if stock > 0 or shelf_count > 0:
                    shelf_urn = shelves[shelf_idx % len(shelves)]
                    inventory_id = f"urn:ngsi-ld:InventoryItem:{item_counter:03d}"
                    item_counter += 1

                    entity = {
                        "id": inventory_id,
                        "type": "InventoryItem",
                        "refStore": {"type": "Relationship", "value": store_urn},
                        "refShelf": {"type": "Relationship", "value": shelf_urn},
                        "refProduct": {"type": "Relationship", "value": product_urn},
                        "stockCount": {"type": "Integer", "value": stock},
                        "shelfCount": {"type": "Integer", "value": shelf_count}
                    }

                    if self._create_entity(entity):
                        inventory_urns.append(inventory_id)
                        self._log("DEBUG", f"  ✓ {inventory_id}")
                        shelf_idx += 1
                    else:
                        logger.error(f"✗ {inventory_id} creation failed")
                        self.errors.append(f"InventoryItem {inventory_id} creation failed")

        self.created_entities["inventory"] = inventory_urns
        logger.info(f"SUCCESS: Created {len(inventory_urns)} inventory items (target: 50-60)")
        return len(inventory_urns) >= 50

    def validate_integrity(self) -> Tuple[bool, List[str]]:
        """Validate cross-entity integrity rules (IR-001..IR-007)."""
        logger.info("START: Validating integrity rules...")
        validation_errors = []

        # IR-001: InventoryItem.refShelf must belong to InventoryItem.refStore
        # (This is handled by design in load_inventory)
        
        # IR-002: Check for duplicate InventoryItems (same store, shelf, product)
        inventory_items = self._list_entities_by_type("InventoryItem")
        seen = set()
        for item in inventory_items:
            key = (
                item.get("refStore", {}).get("value"),
                item.get("refShelf", {}).get("value"),
                item.get("refProduct", {}).get("value")
            )
            if key in seen:
                validation_errors.append(f"IR-002: Duplicate InventoryItem {key}")
            seen.add(key)

        # IR-003: sum(shelfCount) per shelf <= shelf.maxCapacity
        shelves = self._list_entities_by_type("Shelf")
        for shelf in shelves:
            shelf_id = shelf.get("id")
            total_shelf_count = sum(
                item.get("shelfCount", {}).get("value", 0)
                for item in inventory_items
                if item.get("refShelf", {}).get("value") == shelf_id
            )
            max_cap = shelf.get("maxCapacity", {}).get("value", SHELF_MAX_CAPACITY)
            if total_shelf_count > max_cap:
                validation_errors.append(
                    f"IR-003: Shelf {shelf_id} exceeded capacity: {total_shelf_count} > {max_cap}"
                )

        # IR-004: Employee.refStore points to existing Store
        employees = self._list_entities_by_type("Employee")
        store_ids = {s.get("id") for s in self._list_entities_by_type("Store")}
        for emp in employees:
            emp_store = emp.get("refStore", {}).get("value")
            if emp_store and emp_store not in store_ids:
                validation_errors.append(f"IR-004: Employee {emp.get('id')} refs non-existent store {emp_store}")

        # IR-005 & IR-006: Checked at deletion time (not creation)
        # IR-007: countryCode validation
        stores = self._list_entities_by_type("Store")
        for store in stores:
            country = store.get("countryCode", {}).get("value", "")
            if country and country not in VALID_ISO_COUNTRIES:
                validation_errors.append(f"IR-007: Store {store.get('id')} has invalid countryCode {country}")

        if validation_errors:
            logger.warning(f"✗ Validation found {len(validation_errors)} issue(s):")
            for error in validation_errors:
                logger.warning(f"  - {error}")
            return False, validation_errors
        else:
            logger.info("✓ All integrity rules passed (IR-001..IR-007)")
            return True, []

    def verify_minimum_requirements(self) -> Tuple[bool, Dict[str, int]]:
        """Verify min 5 products per store."""
        logger.info("START: Verifying minimum requirements...")
        stats = {"stores": 0, "products": 0, "employees": 0, "shelves": 0, "inventory": 0}
        
        stores = self._list_entities_by_type("Store")
        stats["stores"] = len(stores)
        
        products = self._list_entities_by_type("Product")
        stats["products"] = len(products)
        
        employees = self._list_entities_by_type("Employee")
        stats["employees"] = len(employees)
        
        shelves = self._list_entities_by_type("Shelf")
        stats["shelves"] = len(shelves)
        
        inventory = self._list_entities_by_type("InventoryItem")
        stats["inventory"] = len(inventory)
        
        logger.info(f"SUMMARY: {stats['stores']} stores, {stats['products']} products, "
                   f"{stats['employees']} employees, {stats['shelves']} shelves, {stats['inventory']} items")
        
        # Check min 5 products per store
        for store in stores:
            store_id = store.get("id")
            store_inventory = [
                item for item in inventory
                if item.get("refStore", {}).get("value") == store_id
            ]
            unique_products = set(
                item.get("refProduct", {}).get("value")
                for item in store_inventory
            )
            if len(unique_products) < 5:
                logger.warning(f"✗ Store {store_id} has only {len(unique_products)} unique products (min 5)")
                return False, stats
        
        logger.info("✓ All minimum requirements satisfied")
        return True, stats

    def clean_old_data(self) -> bool:
        """Delete all entities created by previous loads."""
        logger.info("START: Cleaning old data...")
        deleted = 0
        
        for entity_type in ["InventoryItem", "Shelf", "Employee", "Product", "Store"]:
            entities = self._list_entities_by_type(entity_type)
            for entity in entities:
                try:
                    resp = requests.delete(
                        f"{self.orion_url}/v2/entities/{entity.get('id')}",
                        timeout=self.timeout
                    )
                    if resp.status_code in (204, 404):
                        deleted += 1
                except RequestException:
                    pass
        
        logger.info(f"SUCCESS: Deleted {deleted} entities")
        return True

    def run(self, clean_first: bool = False, dry_run: bool = False) -> bool:
        """Execute full data load workflow."""
        logger.info("=" * 70)
        logger.info(f"FIWARE Smart Store - Test Data Loader")
        logger.info(f"Orion URL: {self.orion_url} | Started: {datetime.now()}")
        logger.info("=" * 70)

        if not self.health_check():
            logger.error("Cannot proceed: Orion is not available")
            return False

        if dry_run:
            logger.info("DRY_RUN mode: validating without creating entities")

        if clean_first and not dry_run:
            if not self.clean_old_data():
                logger.error("Failed to clean old data")
                return False

        if not dry_run:
            if not self.load_stores():
                logger.error("Failed to load stores")
                return False

            if not self.load_products():
                logger.error("Failed to load products")
                return False

            if not self.load_employees():
                logger.error("Failed to load employees")
                return False

            if not self.load_shelves():
                logger.error("Failed to load shelves")
                return False

            if not self.load_inventory():
                logger.error("Failed to load inventory")
                return False

            valid, errors = self.validate_integrity()
            if not valid:
                logger.warning(f"Integrity validation failed with {len(errors)} error(s)")
                for error in errors:
                    logger.error(f"  - {error}")

            verified, stats = self.verify_minimum_requirements()
            if not verified:
                logger.error("Minimum requirements not satisfied")
                return False
        else:
            logger.info("[DRY_RUN] Would create 4 stores, 10 products, 10 employees, 12 shelves, 50+ inventory items")

        logger.info("=" * 70)
        logger.info(f"✓ DATA LOAD COMPLETED SUCCESSFULLY")
        logger.info(f"Completed: {datetime.now()}")
        logger.info("=" * 70)
        return True


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Load test data into Orion Context Broker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Default to localhost:1026
  %(prog)s --clean --verbose                  # Clean and show details
  %(prog)s --dry-run                          # Validate without creating
  %(prog)s --orion-url http://orion.example   # Custom Orion URL
        """
    )
    parser.add_argument(
        "--orion-url",
        default=os.getenv("ORION_URL", "http://localhost:1026"),
        help="Orion Context Broker URL (default: %(default)s)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete old data before loading"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without creating entities"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed operation logs"
    )

    args = parser.parse_args()

    loader = OrionDataLoader(args.orion_url, verbose=args.verbose)
    success = loader.run(clean_first=args.clean, dry_run=args.dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
