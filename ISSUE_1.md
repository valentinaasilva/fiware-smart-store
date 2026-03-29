# Issue #1: Crear aplicación base de gestión de cadena de supermercados con datos de prueba

## 🎯 Descripción

Implementar la aplicación base con datos de prueba para una cadena de supermercados: **4 tiendas, 10 productos, mínimo 5 productos por tienda**, incluyendo script de carga automatizado para inicializar Orion Context Broker.

## 📋 Especificación de datos de prueba

### Stores (4 tiendas)

| Store ID | Name | Country | City | Coordinates | Capacity | Employees |
|----------|------|---------|------|-------------|----------|-----------|
| urn:ngsi-ld:Store:S001 | Berlin Mitte | DE | Berlin | [13.405, 52.520] | 2500 m² | 3 |
| urn:ngsi-ld:Store:S002 | Madrid Centro | ES | Madrid | [-3.703, 40.415] | 3000 m² | 3 |
| urn:ngsi-ld:Store:S003 | Barcelona Eixample | ES | Barcelona | [2.165, 41.385] | 2800 m² | 2 |
| urn:ngsi-ld:Store:S004 | Paris Marais | FR | Paris | [2.362, 48.859] | 2200 m² | 2 |

**Atributos requeridos:**
- `name`, `address` (streetAddress, addressLocality, addressRegion), `location` (GeoJSON Point)
- `countryCode` (DE, ES, ES, FR)
- `capacity` (m²)
- `telephone`, `url`, `image` (URLs válidas)
- `description` (opcional)

---

### Products (10 productos)

| Product ID | Name | Size | Color | Price | Origin |
|------------|------|------|-------|-------|--------|
| urn:ngsi-ld:Product:P001 | Banana | M | #FFE135 | €2.99 | EC |
| urn:ngsi-ld:Product:P002 | Red Apple | M | #DC143C | €1.49 | ES |
| urn:ngsi-ld:Product:P003 | Orange | L | #FF8C00 | €3.99 | ES |
| urn:ngsi-ld:Product:P004 | Lettuce | L | #228B22 | €1.99 | DE |
| urn:ngsi-ld:Product:P005 | Tomato | M | #FF4500 | €2.49 | ES |
| urn:ngsi-ld:Product:P006 | Milk 1L | S | #FFFFFF | €1.29 | FR |
| urn:ngsi-ld:Product:P007 | Cheese | S | #FFD700 | €4.99 | FR |
| urn:ngsi-ld:Product:P008 | Bread | M | #8B4513 | €2.49 | DE |
| urn:ngsi-ld:Product:P009 | Water 2L | L | #87CEEB | €0.99 | ES |
| urn:ngsi-ld:Product:P010 | Coffee | S | #6F4E37 | €5.99 | BR |

**Atributos requeridos:**
- `name`, `size` (S/M/L/XL), `price` (2 decimales), `color` (#RRGGBB)
- `originCountry` (ISO alpha-2)
- `image` (URL)

---

### Employees (8 empleados distribuidos en 4 tiendas)

| Employee ID | Name | Store | Category | Role | Salary | Email |
|------------|------|-------|----------|------|--------|-------|
| urn:ngsi-ld:Employee:E001 | Ángel Vilariño García | S001 | Specialist | Inventory Specialist | €2350 | angel.vilarino@xantadis.com |
| urn:ngsi-ld:Employee:E002 | Alejandro Rodríguez Expósito | S002 | Senior | Store Supervisor | €2550 | alejandro.rodriguez.exposito@xantadis.com |
| urn:ngsi-ld:Employee:E003 | Soraya Rodriguez Campos | S003 | Manager | Customer Service Lead | €2480 | soraya.rodriguez.campos@xantadis.com |
| urn:ngsi-ld:Employee:E004 | Sara Paredes Bascoy | S004 | Senior | Operations Analyst | €2420 | sara.paredes.bascoy@xantadis.com |
| urn:ngsi-ld:Employee:E005 | Alejandro Varela Vázquez | S001 | Junior | Cashier | €1820 | alejandro.varela.vazquez@xantadis.com |
| urn:ngsi-ld:Employee:E006 | Daniel Martínez Martínez | S002 | Specialist | Logistics Coordinator | €2380 | daniel.martinez@xantadis.com |
| urn:ngsi-ld:Employee:E007 | Pablo Armenteros Lobato | S003 | Junior | Stock Assistant | €1760 | pablo.armenteros@xantadis.com |
| urn:ngsi-ld:Employee:E008 | Verónica Vila Viveiro | S004 | Manager | Store Manager | €2950 | veronica.vila@xantadis.com |

**Validaciones:**
- `email` formato válido Y único
- `category` ∈ {Junior, Senior, Manager, Specialist}
- `skills` no vacío (enums: MachineryDriving, WritingReports, CustomerRelationships)
- `refStore` apunta a Store existente

---

### Shelves (12 estanterías)

- Berlin (S001): 3 shelves
- Madrid (S002): 3 shelves
- Barcelona (S003): 3 shelves
- Paris (S004): 3 shelves

**Atributos:**
- `name`, `maxCapacity` (50 items típicamente)
- `location` (GeoJSON Point)
- `refStore` (Relationship)

---

### InventoryItems (50-60 items total)

**Requisitos:**
- Cada tienda tiene **mínimo 5 productos diferentes**
- Cada tienda tiene **mínimo 12-15 items de inventario**
- Distribución de 10 productos entre 4 tiendas: cada producto aparece en 2-3 tiendas

**Validaciones:**
- `refShelf.refStore == refStore` (IR-001)
- No duplicados (refStore, refShelf, refProduct) (IR-002)
- `sum(shelfCount)` por shelf ≤ shelf.maxCapacity (IR-003)
- `shelfCount ≤ stockCount` (IR-004)

---

## 📁 Estructura de archivos a crear

```
scripts/
└── load_test_data.py          # Script principal de carga
tests/
├── test_smoke.py               # Ya existe (verificar)
├── test_stores.py              # CRUD stores
├── test_products.py            # CRUD products
├── test_employees.py           # CRUD employees
├── test_inventory.py           # CRUD inventory items
└── test_data_loading.py        # Tests del script de carga
data/
└── test_data.json              # Definición de datos (opcional)
```

---

## 🔧 Script de carga: `load_test_data.py`

### Responsabilidades

1. Conectar a Orion con reintentos exponenciales (max 3 intentos)
2. Crear 4 Stores with NGSIv2 validation
3. Crear 10 Products with color, price, size validation
4. Crear 10 Employees with email unique constraint, relations to Stores
5. Crear 12 Shelves with Relationship to Stores
6. Crear 50-60 InventoryItems with triple relation validation (Store, Shelf, Product)
7. Validar integridad de relaciones (IR-001..IR-007)
8. Reportar status de cada creación
9. Limpiar datos previos (opcional --clean flag)
10. Generar log de auditoría

### Interface CLI

```bash
# Ejecutar carga completa
python scripts/load_test_data.py

# Con opciones
python scripts/load_test_data.py --orion-url http://localhost:1026 --clean --verbose

# Modo simulación (valida sin crear)
python scripts/load_test_data.py --dry-run

# Output esperado
[2026-03-28 10:15:42] INFO: Connecting to Orion at http://localhost:1026...
[2026-03-28 10:15:43] SUCCESS: Orion health check passed (version 3.4.0)
[2026-03-28 10:15:44] START: Creating 4 stores...
[2026-03-28 10:15:45] ✓ Store urn:ngsi-ld:Store:S001 (Berlin Mitte)
[2026-03-28 10:15:46] ✓ Store urn:ngsi-ld:Store:S002 (Madrid Centro)
...
[2026-03-28 10:16:15] SUMMARY: Created 4 stores, 10 products, 10 employees, 12 shelves, 55 inventory items
[2026-03-28 10:16:16] VALIDATION: All integrity rules passed (IR-001..IR-007)
```

### Estructura interna requerida

```python
class OrionDataLoader:
    def health_check(self) -> bool: ...
    def load_stores(self) -> List[str]: ...
    def load_products(self) -> List[str]: ...
    def load_employees(self, store_urns: List[str]) -> List[str]: ...
    def load_shelves(self, store_urns: List[str]) -> List[str]: ...
    def load_inventory(self, store_urns: List[str], shelf_urns: List[str], product_urns: List[str]) -> List[str]: ...
    def validate_integrity(self) -> Tuple[bool, List[str]]: ...
    def run(self, clean_first=False): ...
```

---

## ✅ Test Suites a crear

### test_stores.py
```python
def test_list_stores_returns_4_items(): ...
def test_get_store_detail(): ...
def test_create_store_with_validation(): ...
def test_update_store_price(): ...
def test_delete_store_checks_integrity(): ...
def test_store_with_invalid_country_code_fails(): ...
```

### test_products.py
```python
def test_list_products_returns_10_items(): ...
def test_product_size_enum_validation(): ...
def test_product_price_precision_2_decimals(): ...
def test_product_color_hex_validation(): ...
def test_create_product_with_valid_data(): ...
def test_update_product_stock_impact(): ...
```

### test_employees.py
```python
def test_list_employees_returns_10_items(): ...
def test_employee_email_unique_constraint(): ...
def test_employee_category_enum(): ...
def test_employee_skills_non_empty(): ...
def test_employee_refstore_must_exist(): ...
```

### test_inventory.py
```python
def test_list_inventory_items_50_plus(): ...
def test_inventory_relation_consistency_ir001(): ...
def test_inventory_no_duplicates_ir002(): ...
def test_shelf_capacity_limit_ir003(): ...
def test_inventory_shelf_count_validation(): ...
def test_each_store_has_5_plus_products(): ...
```

### test_data_loading.py
```python
def test_load_script_creates_4_stores(): ...
def test_load_script_creates_10_products(): ...
def test_load_script_creates_10_employees(): ...
def test_load_script_creates_50_plus_inventory(): ...
def test_load_script_validates_all_integrity_rules(): ...
def test_load_script_idempotent_on_rerun(): ...
def test_load_script_with_clean_flag_removes_old_data(): ...
```

---

## 📋 Criterios de Aceptación

- [ ] AC-1.1: 4 Stores creadas con datos válidos en Orion
- [ ] AC-1.2: 10 Products creados con size, price, color válidos
- [ ] AC-1.3: 10 Employees distribuidos entre stores
- [ ] AC-1.4: 12 Shelves de soporte (3 por tienda en promedio)
- [ ] AC-1.5: 50-60 InventoryItems con mínimo 5 productos por tienda
- [ ] AC-1.6: Script `load_test_data.py` ejecutable desde línea de comandos
- [ ] AC-1.7: Flag `--clean` elimina datos previos
- [ ] AC-1.8: Flag `--dry-run` valida sin crear
- [ ] AC-1.9: Flag `--verbose` reporta detalle de operaciones
- [ ] AC-1.10: Validación IR-001..IR-007 en script con reporte de status
- [ ] AC-1.11: Tests en `test_data_loading.py` pasan 100%
- [ ] AC-1.12: Dashboard muestra conteos correctos (4, 10, 10, 50+)
- [ ] AC-1.13: PRD.md, architecture.md, data_model.md actualizados con progreso

---

## 📚 Dependencias

- Flask app factory (ya existe en app.py)
- Orion Context Broker en `localhost:1026` (docker-compose)
- requests library para HTTP calls
- pytest para test execution

---

## ⏱️ Línea de tiempo estimada

| Tarea | Horas Est. |
|-------|-----------|
| Definir matriz de datos | 0.5 |
| Implementar load_test_data.py | 3-4 |
| Implementar validaciones NGSIv2 | 2 |
| Crear test suites | 2 |
| Ejecutar contra Orion local | 1 |
| Actualizar docs (PRD/architecture/data_model) | 1 |
| **TOTAL** | **9.5-11 horas** |

---

## 📌 Notas

- Basado en PRD.md, architecture.md, data_model.md
- Mantener trazabilidad entre specs y criterios de aceptación
- Al finalizar, actualizar obligatoriamente PRD.md, architecture.md, data_model.md (requisito AGENTS.md)
- Script debe ser idempotente (safe to rerun)
- Validar todas las reglas de integridad (IR-001..IR-007)

---

## 🔗 Referencias

- [PRD.md](PRD.md)
- [architecture.md](architecture.md)
- [data_model.md](data_model.md)
- [AGENTS.md](AGENTS.md)
