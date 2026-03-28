# Issue #1: Test Data Loading Guide

## Overview

This directory contains the test data loading infrastructure for the fiware-smart-store project. The `load_test_data.py` script creates a complete dataset with:

- **4 Stores** (Berlin, Madrid, Barcelona, Paris)
- **10 Products** (fruits, vegetables, dairy, bakery, beverages)
- **10 Employees** (distributed across stores)
- **12 Shelves** (3 per store)
- **55+ Inventory Items** (min 5 products per store)

## Quick Start

### Prerequisites

Before running the script, ensure:

1. **Orion Context Broker** is running:
   ```bash
   cd /path/to/docker-compose
   docker-compose up orion  # Opens port 1026
   ```

2. **MongoDB** is available (required by Orion):
   ```bash
   docker-compose up mongo  # Opens port 27017
   ```

3. **Python dependencies** are installed:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

#### Load Test Data

```bash
# Load data with default settings (http://localhost:1026)
python scripts/load_test_data.py

# Load with verbose output
python scripts/load_test_data.py --verbose

# Clean old data before loading (caution: deletes all entities)
python scripts/load_test_data.py --clean --verbose

# Validate without creating (dry-run mode)
python scripts/load_test_data.py --dry-run

# Custom Orion URL
python scripts/load_test_data.py --orion-url http://orion.example.com:1026
```

### CLI Options

| Flag | Description | Example |
|------|-------------|---------|
| `--orion-url URL` | Orion Context Broker endpoint | `--orion-url http://localhost:1026` |
| `--clean` | Delete old data before loading | `--clean` |
| `--dry-run` | Validate without creating entities | `--dry-run` |
| `--verbose` | Show detailed operation logs | `--verbose` |

### Expected Output

```
======================================================================
FIWARE Smart Store - Test Data Loader
Orion URL: http://localhost:1026 | Started: 2026-03-28 10:15:42
======================================================================
[2026-03-28 10:15:43] INFO: ✓ Orion health check passed (version 3.4.0)
[2026-03-28 10:15:44] INFO: START: Creating 4 stores...
[2026-03-28 10:15:45] INFO: ✓ Store urn:ngsi-ld:Store:S001 (Berlin Mitte)
[2026-03-28 10:15:45] INFO: ✓ Store urn:ngsi-ld:Store:S002 (Madrid Centro)
[2026-03-28 10:15:46] INFO: ✓ Store urn:ngsi-ld:Store:S003 (Barcelona Eixample)
[2026-03-28 10:15:46] INFO: ✓ Store urn:ngsi-ld:Store:S004 (Paris Marais)
[2026-03-28 10:15:47] INFO: SUCCESS: Created 4/4 stores
[2026-03-28 10:15:48] INFO: START: Creating 10 products...
...
[2026-03-28 10:16:15] INFO: SUMMARY: 4 stores, 10 products, 10 employees, 12 shelves, 55 items
[2026-03-28 10:16:16] INFO: ✓ All integrity rules passed (IR-001..IR-007)
======================================================================
✓ DATA LOAD COMPLETED SUCCESSFULLY
Completed: 2026-03-28 10:16:17
======================================================================
```

## Data Structure

### Stores (4 total)

| Store ID | Name | Country | City | 
|----------|------|---------|------|
| S001 | Berlin Mitte | DE | Berlin |
| S002 | Madrid Centro | ES | Madrid |
| S003 | Barcelona Eixample | ES | Barcelona |
| S004 | Paris Marais | FR | Paris |

### Products (10 total)

| Product ID | Name | Size | Price |
|------------|------|------|-------|
| P001 | Banana | M | €2.99 |
| P002 | Red Apple | M | €1.49 |
| P003 | Orange | L | €3.99 |
| P004 | Lettuce | L | €1.99 |
| P005 | Tomato | M | €2.49 |
| P006 | Milk 1L | S | €1.29 |
| P007 | Cheese | S | €4.99 |
| P008 | Bread | M | €2.49 |
| P009 | Water 2L | L | €0.99 |
| P010 | Coffee | S | €5.99 |

### Employees (10 total, distributed across 4 stores)

3 employees in Berlin (S001), 3 in Madrid (S002), 2 in Barcelona (S003), 2 in Paris (S004).

### Shelves (12 total)

3 shelves per store with 50-unit capacity each.

### Inventory Items (55+ total)

Each store has:
- Minimum 5 different products
- Minimum 12 inventory items
- Proper shelf allocation respecting capacity constraints

## Validation & Integrity Rules

The script validates all cross-entity integrity rules (IR-001 through IR-007):

- **IR-001**: InventoryItem.refShelf belongs to InventoryItem.refStore
- **IR-002**: No duplicate InventoryItems (store, shelf, product)
- **IR-003**: sum(shelfCount) per shelf ≤ shelf.maxCapacity
- **IR-004**: Employee.refStore exists
- **IR-005**: Store deletion blocked if related entities exist
- **IR-006**: Product deletion blocked if inventory items exist
- **IR-007**: Valid ISO alpha-2 country codes

## Testing

Run the test suites to verify data and functionality:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_data_loading.py -v

# Run with coverage
pytest tests/ --cov=scripts --cov=routes --cov=models

# Run only data loading validation tests
pytest tests/test_data_loading.py::TestDataValidation -v
```

### Test Coverage

- **test_stores.py**: Store CRUD, validation, country codes
- **test_products.py**: Product validation (size, price, color)
- **test_employees.py**: Employee validation (email, category, skills)
- **test_inventory.py**: Inventory integrity rules, distribution
- **test_data_loading.py**: Script logic, data structure validation

## Troubleshooting

### Orion Connection Failed

```
ERROR: Cannot connect to Orion at http://localhost:1026
```

**Solution**: Ensure Orion is running:
```bash
docker-compose ps  # Check Orion container
docker-compose logs orion  # View Orion logs
```

### Health Check Failed

```
ERROR: Orion health check failed (status 500)
```

**Solution**: Check MongoDB connection or Orion logs:
```bash
docker-compose logs orion
docker-compose logs mongo
```

### Script Hangs on Entity Creation

**Solution**: Use timeout or Ctrl+C and increase timeout:
```bash
timeout 60 python scripts/load_test_data.py --verbose
```

## Integration with Flask App

Once data is loaded into Orion, the Flask app can:

1. Query entities via `/stores`, `/products`, `/employees`, `/inventory`
2. Display dashboard metrics with accurate counts
3. Receive real-time notifications from subscriptions
4. Emit SocketIO events for connected clients

## Environment Variables

Configure via `.env` file or command-line:

```bash
ORION_URL=http://localhost:1026
FLASK_SECRET_KEY=your-secret-key
SQLITE_PATH=instance/fiware.db
FLASK_PORT=5000
```

## References

- [ISSUE_1.md](../ISSUE_1.md) - Issue specification
- [PRD.md](../PRD.md) - Product requirements
- [architecture.md](../architecture.md) - System architecture
- [data_model.md](../data_model.md) - NGSIv2 data model

---

**Author**: Issue #1 Implementation  
**Date**: 2026-03-28  
**Status**: Complete
