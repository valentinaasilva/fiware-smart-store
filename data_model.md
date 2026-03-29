# Data Model - fiware-smart-store (NGSIv2)

## 1. Document control

### ES
- Version: 1.0
- Fecha: 2026-03-28
- Estado: Especificacion de modelo de datos objetivo
- Estandar: FIWARE NGSIv2

### EN
- Version: 1.0
- Date: 2026-03-28
- Status: Target data model specification
- Standard: FIWARE NGSIv2

## 1.1 Change log

### ES
- 2026-03-29: Sin cambios estructurales en entidades NGSIv2 por el rediseño UI. Se documenta metrica derivada de dashboard `low_stock_count` como agregacion de `InventoryItem`.

### EN
- 2026-03-29: No structural changes to NGSIv2 entities due to the UI redesign. Dashboard derived metric `low_stock_count` is documented as an `InventoryItem` aggregation.

## 2. Modeling conventions

### ES
- Identificadores: URN con formato urn:ngsi-ld:<EntityType>:<Code>
- type de entidad coincide con nombre canonico: Store, Product, Employee, Shelf, InventoryItem
- Atributos NGSIv2 usan estructura: {"type": "<DataType>", "value": <value>}
- Relaciones usan type Relationship y value con URN de la entidad objetivo
- Fechas en DateTime ISO-8601 con zona horaria (ejemplo: 2026-03-28T09:00:00Z)
- Color hexadecimal en mayusculas y formato #RRGGBB
- countryCode en ISO 3166-1 alpha-2 (2 caracteres)
- location en GeoJSON Point

### EN
- Identifiers: URN format urn:ngsi-ld:<EntityType>:<Code>
- Entity type matches canonical name: Store, Product, Employee, Shelf, InventoryItem
- NGSIv2 attributes use shape: {"type": "<DataType>", "value": <value>}
- Relationships use type Relationship and value with target entity URN
- Dates in ISO-8601 DateTime with timezone (example: 2026-03-28T09:00:00Z)
- Hex color in uppercase and #RRGGBB format
- countryCode in ISO 3166-1 alpha-2 (2 chars)
- location in GeoJSON Point

## 3. Entity relationship summary

### ES
Relaciones principales:
- Store 1..N Shelf
- Store 1..N InventoryItem
- Shelf 1..N InventoryItem
- Product 1..N InventoryItem
- Store 1..N Employee

Restricciones:
- Cada Shelf pertenece a una sola Store.
- Cada InventoryItem referencia exactamente 1 Store, 1 Shelf y 1 Product.
- refShelf y refStore en InventoryItem deben ser consistentes (la shelf debe pertenecer a la store referenciada).

### EN
Main relationships:
- Store 1..N Shelf
- Store 1..N InventoryItem
- Shelf 1..N InventoryItem
- Product 1..N InventoryItem
- Store 1..N Employee

Constraints:
- Each Shelf belongs to exactly one Store.
- Each InventoryItem references exactly 1 Store, 1 Shelf, and 1 Product.
- refShelf and refStore in InventoryItem must be consistent (shelf must belong to referenced store).

## 4. Catalogs and enums

### ES
- Product.size permitido: S, M, L, XL
- Employee.skills permitido:
  - MachineryDriving
  - WritingReports
  - CustomerRelationships
- Employee.category (propuesta base): Junior, Senior, Manager, Specialist

### EN
- Allowed Product.size: S, M, L, XL
- Allowed Employee.skills:
  - MachineryDriving
  - WritingReports
  - CustomerRelationships
- Employee.category (baseline proposal): Junior, Senior, Manager, Specialist

## 5. Entity specifications

### 5.1 Store

#### ES
| Atributo | NGSI type | Obligatorio | Cardinalidad | Validacion | Ejemplo | Origen |
|---|---|---|---|---|---|---|
| id | n/a | Si | 1 | URN Store unico | urn:ngsi-ld:Store:001 | Interno |
| type | n/a | Si | 1 | Valor fijo Store | Store | Interno |
| name | Text | Si | 1 | 1..120 chars | Berlin Mitte | Interno |
| address | PostalAddress | Si | 1 | Debe incluir streetAddress, addressLocality, addressRegion | {...} | Interno |
| location | geo:json | Si | 1 | GeoJSON Point valido | {"type":"Point","coordinates":[13.40,52.53]} | Interno |
| image | Text | No | 0..1 | URL valida (http/https) | https://images... | Interno |
| url | Text | No | 0..1 | URL valida | https://store.example | Interno |
| telephone | Text | No | 0..1 | Patron telefono internacional | +49-30-123456 | Interno |
| countryCode | Text | Si | 1 | ISO alpha-2 | DE | Interno |
| capacity | Integer | Si | 1 | > 0 | 2000 | Interno |
| description | Text | No | 0..1 | <= 2000 chars | Main branch... | Interno |
| temperature | Float | No | 0..1 | -30.0..60.0 | 21.4 | Provider externo |
| relativeHumidity | Float | No | 0..1 | 0.0..100.0 | 44.2 | Provider externo |
| tweets | Array | No | 0..1 | Array de textos o objetos tweet | ["Promo 2x1"] | Provider externo |

#### EN
| Attribute | NGSI type | Required | Cardinality | Validation | Example | Source |
|---|---|---|---|---|---|---|
| id | n/a | Yes | 1 | Unique Store URN | urn:ngsi-ld:Store:001 | Internal |
| type | n/a | Yes | 1 | Fixed value Store | Store | Internal |
| name | Text | Yes | 1 | 1..120 chars | Berlin Mitte | Internal |
| address | PostalAddress | Yes | 1 | Must include streetAddress, addressLocality, addressRegion | {...} | Internal |
| location | geo:json | Yes | 1 | Valid GeoJSON Point | {"type":"Point","coordinates":[13.40,52.53]} | Internal |
| image | Text | No | 0..1 | Valid URL (http/https) | https://images... | Internal |
| url | Text | No | 0..1 | Valid URL | https://store.example | Internal |
| telephone | Text | No | 0..1 | International phone pattern | +49-30-123456 | Internal |
| countryCode | Text | Yes | 1 | ISO alpha-2 | DE | Internal |
| capacity | Integer | Yes | 1 | > 0 | 2000 | Internal |
| description | Text | No | 0..1 | <= 2000 chars | Main branch... | Internal |
| temperature | Float | No | 0..1 | -30.0..60.0 | 21.4 | External provider |
| relativeHumidity | Float | No | 0..1 | 0.0..100.0 | 44.2 | External provider |
| tweets | Array | No | 0..1 | Array of tweet strings/objects | ["Promo 2x1"] | External provider |

### 5.2 Product

#### ES
| Atributo | NGSI type | Obligatorio | Cardinalidad | Validacion | Ejemplo |
|---|---|---|---|---|---|
| id | n/a | Si | 1 | URN Product unico | urn:ngsi-ld:Product:001 |
| type | n/a | Si | 1 | Valor fijo Product | Product |
| name | Text | Si | 1 | 1..120 chars | Banana |
| size | Text | Si | 1 | Enum S/M/L/XL | M |
| price | Float | Si | 1 | >= 0 y precision 2 decimales | 2.99 |
| image | Text | No | 0..1 | URL valida | https://images... |
| originCountry | Text | No | 0..1 | ISO alpha-2 recomendado | ES |
| color | Text | Si | 1 | Regex ^#[0-9A-F]{6}$ | #FF5733 |

#### EN
| Attribute | NGSI type | Required | Cardinality | Validation | Example |
|---|---|---|---|---|---|
| id | n/a | Yes | 1 | Unique Product URN | urn:ngsi-ld:Product:001 |
| type | n/a | Yes | 1 | Fixed value Product | Product |
| name | Text | Yes | 1 | 1..120 chars | Banana |
| size | Text | Yes | 1 | Enum S/M/L/XL | M |
| price | Float | Yes | 1 | >= 0 and 2-dec precision | 2.99 |
| image | Text | No | 0..1 | Valid URL | https://images... |
| originCountry | Text | No | 0..1 | ISO alpha-2 recommended | ES |
| color | Text | Yes | 1 | Regex ^#[0-9A-F]{6}$ | #FF5733 |

### 5.3 Employee

#### ES
| Atributo | NGSI type | Obligatorio | Cardinalidad | Validacion | Ejemplo |
|---|---|---|---|---|---|
| id | n/a | Si | 1 | URN Employee unico | urn:ngsi-ld:Employee:001 |
| type | n/a | Si | 1 | Valor fijo Employee | Employee |
| name | Text | Si | 1 | 1..140 chars | Ada Lovelace |
| image | Text | No | 0..1 | URL valida | https://images... |
| salary | Float | Si | 1 | > 0 | 2400.00 |
| role | Text | Si | 1 | 1..80 chars | Store Manager |
| category | Text | Si | 1 | Enum definido por negocio | Senior |
| skills | Array | Si | 1 | Lista no vacia con enums permitidos | ["WritingReports"] |
| email | Text | Si | 1 | Formato email valido y unico | ada@store.com |
| dateOfContract | DateTime | Si | 1 | ISO-8601 | 2025-03-15T00:00:00Z |
| username | Text | Si | 1 | 4..32 chars, unico | adal |
| password | Text | Si | 1 | Hash, nunca texto plano | $2b$12$... |
| refStore | Relationship | Si | 1 | Debe apuntar a Store existente | urn:ngsi-ld:Store:001 |

#### EN
| Attribute | NGSI type | Required | Cardinality | Validation | Example |
|---|---|---|---|---|---|
| id | n/a | Yes | 1 | Unique Employee URN | urn:ngsi-ld:Employee:001 |
| type | n/a | Yes | 1 | Fixed value Employee | Employee |
| name | Text | Yes | 1 | 1..140 chars | Ada Lovelace |
| image | Text | No | 0..1 | Valid URL | https://images... |
| salary | Float | Yes | 1 | > 0 | 2400.00 |
| role | Text | Yes | 1 | 1..80 chars | Store Manager |
| category | Text | Yes | 1 | Business-defined enum | Senior |
| skills | Array | Yes | 1 | Non-empty list of allowed enums | ["WritingReports"] |
| email | Text | Yes | 1 | Valid and unique email format | ada@store.com |
| dateOfContract | DateTime | Yes | 1 | ISO-8601 | 2025-03-15T00:00:00Z |
| username | Text | Yes | 1 | 4..32 chars, unique | adal |
| password | Text | Yes | 1 | Hash only, never plain text | $2b$12$... |
| refStore | Relationship | Yes | 1 | Must reference existing Store | urn:ngsi-ld:Store:001 |

### 5.4 Shelf

#### ES
| Atributo | NGSI type | Obligatorio | Cardinalidad | Validacion | Ejemplo |
|---|---|---|---|---|---|
| id | n/a | Si | 1 | URN Shelf unico | urn:ngsi-ld:Shelf:001 |
| type | n/a | Si | 1 | Valor fijo Shelf | Shelf |
| name | Text | Si | 1 | 1..80 chars | Shelf 1 |
| location | geo:json | Si | 1 | GeoJSON Point valido | {"type":"Point","coordinates":[13.401,52.531]} |
| maxCapacity | Integer | Si | 1 | >= 1 | 50 |
| refStore | Relationship | Si | 1 | Debe apuntar a Store existente | urn:ngsi-ld:Store:001 |

#### EN
| Attribute | NGSI type | Required | Cardinality | Validation | Example |
|---|---|---|---|---|---|
| id | n/a | Yes | 1 | Unique Shelf URN | urn:ngsi-ld:Shelf:001 |
| type | n/a | Yes | 1 | Fixed value Shelf | Shelf |
| name | Text | Yes | 1 | 1..80 chars | Shelf 1 |
| location | geo:json | Yes | 1 | Valid GeoJSON Point | {"type":"Point","coordinates":[13.401,52.531]} |
| maxCapacity | Integer | Yes | 1 | >= 1 | 50 |
| refStore | Relationship | Yes | 1 | Must reference existing Store | urn:ngsi-ld:Store:001 |

### 5.5 InventoryItem

#### ES
| Atributo | NGSI type | Obligatorio | Cardinalidad | Validacion | Ejemplo |
|---|---|---|---|---|---|
| id | n/a | Si | 1 | URN InventoryItem unico | urn:ngsi-ld:InventoryItem:001 |
| type | n/a | Si | 1 | Valor fijo InventoryItem | InventoryItem |
| refStore | Relationship | Si | 1 | Store existente | urn:ngsi-ld:Store:001 |
| refShelf | Relationship | Si | 1 | Shelf existente de la misma Store | urn:ngsi-ld:Shelf:001 |
| refProduct | Relationship | Si | 1 | Product existente | urn:ngsi-ld:Product:001 |
| stockCount | Integer | Si | 1 | >= 0 | 120 |
| shelfCount | Integer | Si | 1 | >= 0 y <= stockCount y <= maxCapacity shelf | 20 |

#### EN
| Attribute | NGSI type | Required | Cardinality | Validation | Example |
|---|---|---|---|---|---|
| id | n/a | Yes | 1 | Unique InventoryItem URN | urn:ngsi-ld:InventoryItem:001 |
| type | n/a | Yes | 1 | Fixed value InventoryItem | InventoryItem |
| refStore | Relationship | Yes | 1 | Existing Store | urn:ngsi-ld:Store:001 |
| refShelf | Relationship | Yes | 1 | Existing Shelf in same Store | urn:ngsi-ld:Shelf:001 |
| refProduct | Relationship | Yes | 1 | Existing Product | urn:ngsi-ld:Product:001 |
| stockCount | Integer | Yes | 1 | >= 0 | 120 |
| shelfCount | Integer | Yes | 1 | >= 0 and <= stockCount and <= shelf maxCapacity | 20 |

## 6. Cross-entity integrity rules

### ES
- IR-001: InventoryItem(refShelf) debe pertenecer a InventoryItem(refStore).
- IR-002: No puede existir InventoryItem duplicado con misma tripleta (refStore, refShelf, refProduct).
- IR-003: sum(shelfCount) por Shelf no puede superar maxCapacity.
- IR-004: Employee(refStore) debe referenciar Store existente activa.
- IR-005: Al borrar Store se debe impedir borrado si existen Shelf/Employee/InventoryItem relacionados, salvo borrado en cascada explicitamente habilitado.
- IR-006: Al borrar Product se debe impedir borrado si existen InventoryItem asociados, salvo reasignacion previa.
- IR-007: countryCode debe mapear a bandera valida en frontend.

### EN
- IR-001: InventoryItem(refShelf) must belong to InventoryItem(refStore).
- IR-002: Duplicate InventoryItem with same tuple (refStore, refShelf, refProduct) is not allowed.
- IR-003: sum(shelfCount) by Shelf cannot exceed maxCapacity.
- IR-004: Employee(refStore) must reference an existing active Store.
- IR-005: Deleting Store must be blocked if related Shelf/Employee/InventoryItem exist, unless cascade delete is explicitly enabled.
- IR-006: Deleting Product must be blocked when related InventoryItem records exist, unless reassigned first.
- IR-007: countryCode must map to a valid frontend flag.

## 6.1 Derived dashboard metrics

### ES
- DM-001: `low_stock_count` es una metrica derivada no persistida.
- DM-002: Se calcula contando `InventoryItem` con `stockCount <= 10` o `shelfCount <= 3`.
- DM-003: La metrica se usa para visualizacion operativa en dashboard y no modifica payload NGSIv2.

### EN
- DM-001: `low_stock_count` is a non-persisted derived metric.
- DM-002: It is computed as the count of `InventoryItem` where `stockCount <= 10` or `shelfCount <= 3`.
- DM-003: The metric is used for dashboard operational visualization and does not modify NGSIv2 payloads.

## 7. NGSIv2 payload examples

### 7.1 Create Store

```json
{
  "id": "urn:ngsi-ld:Store:001",
  "type": "Store",
  "name": {"type": "Text", "value": "Berlin Mitte"},
  "address": {
    "type": "PostalAddress",
    "value": {
      "streetAddress": "Alexanderplatz 1",
      "addressLocality": "Berlin",
      "addressRegion": "Berlin"
    }
  },
  "location": {
    "type": "geo:json",
    "value": {"type": "Point", "coordinates": [13.405, 52.52]}
  },
  "image": {"type": "Text", "value": "https://picsum.photos/600/300"},
  "url": {"type": "Text", "value": "https://store.example/berlin-mitte"},
  "telephone": {"type": "Text", "value": "+49-30-123456"},
  "countryCode": {"type": "Text", "value": "DE"},
  "capacity": {"type": "Integer", "value": 2000},
  "description": {"type": "Text", "value": "Main city branch"}
}
```

### 7.2 Create Product

```json
{
  "id": "urn:ngsi-ld:Product:001",
  "type": "Product",
  "name": {"type": "Text", "value": "Banana"},
  "size": {"type": "Text", "value": "M"},
  "price": {"type": "Float", "value": 2.99},
  "image": {"type": "Text", "value": "https://picsum.photos/200/200"},
  "originCountry": {"type": "Text", "value": "EC"},
  "color": {"type": "Text", "value": "#FFE135"}
}
```

### 7.3 Create Employee

```json
{
  "id": "urn:ngsi-ld:Employee:001",
  "type": "Employee",
  "name": {"type": "Text", "value": "Ada Lovelace"},
  "image": {"type": "Text", "value": "https://picsum.photos/250/250"},
  "salary": {"type": "Float", "value": 2400.0},
  "role": {"type": "Text", "value": "Store Manager"},
  "category": {"type": "Text", "value": "Senior"},
  "skills": {"type": "Array", "value": ["WritingReports", "CustomerRelationships"]},
  "email": {"type": "Text", "value": "ada@store.example"},
  "dateOfContract": {"type": "DateTime", "value": "2025-03-15T00:00:00Z"},
  "username": {"type": "Text", "value": "adal"},
  "password": {"type": "Text", "value": "$2b$12$REPLACE_WITH_HASH"},
  "refStore": {"type": "Relationship", "value": "urn:ngsi-ld:Store:001"}
}
```

### 7.4 Create Shelf

```json
{
  "id": "urn:ngsi-ld:Shelf:001",
  "type": "Shelf",
  "name": {"type": "Text", "value": "Shelf A1"},
  "location": {
    "type": "geo:json",
    "value": {"type": "Point", "coordinates": [13.406, 52.521]}
  },
  "maxCapacity": {"type": "Integer", "value": 50},
  "refStore": {"type": "Relationship", "value": "urn:ngsi-ld:Store:001"}
}
```

### 7.5 Create InventoryItem

```json
{
  "id": "urn:ngsi-ld:InventoryItem:001",
  "type": "InventoryItem",
  "refStore": {"type": "Relationship", "value": "urn:ngsi-ld:Store:001"},
  "refShelf": {"type": "Relationship", "value": "urn:ngsi-ld:Shelf:001"},
  "refProduct": {"type": "Relationship", "value": "urn:ngsi-ld:Product:001"},
  "stockCount": {"type": "Integer", "value": 120},
  "shelfCount": {"type": "Integer", "value": 20}
}
```

### 7.6 Partial update Product price (for subscription trigger)

```json
{
  "price": {"type": "Float", "value": 3.49}
}
```

### 7.7 Partial update InventoryItem counts (for low stock trigger)

```json
{
  "stockCount": {"type": "Integer", "value": 8},
  "shelfCount": {"type": "Integer", "value": 2}
}
```

## 8. Subscription contracts (NGSIv2)

### ES

#### 8.1 Price change subscription
Condicion: cambios en Product.price

Payload de alta ejemplo:
```json
{
  "description": "Notify product price change",
  "subject": {
    "entities": [{"idPattern": "urn:ngsi-ld:Product:.*", "type": "Product"}],
    "condition": {"attrs": ["price"]}
  },
  "notification": {
    "http": {"url": "http://host.docker.internal:5000/notifications/price-change"},
    "attrs": ["name", "price", "color", "size"]
  },
  "throttling": 1
}
```

#### 8.2 Low stock subscription
Condicion: cambios en InventoryItem.stockCount o InventoryItem.shelfCount

Payload de alta ejemplo:
```json
{
  "description": "Notify low stock",
  "subject": {
    "entities": [{"idPattern": "urn:ngsi-ld:InventoryItem:.*", "type": "InventoryItem"}],
    "condition": {"attrs": ["stockCount", "shelfCount"]}
  },
  "notification": {
    "http": {"url": "http://host.docker.internal:5000/notifications/low-stock"},
    "attrs": ["refStore", "refShelf", "refProduct", "stockCount", "shelfCount"]
  },
  "throttling": 1
}
```

Regla de negocio sugerida para low stock:
- lowStock = stockCount <= 10 OR shelfCount <= 3

### EN

#### 8.1 Price change subscription
Condition: changes in Product.price

#### 8.2 Low stock subscription
Condition: changes in InventoryItem.stockCount or InventoryItem.shelfCount

Suggested business rule for low stock:
- lowStock = stockCount <= 10 OR shelfCount <= 3

## 9. Validation matrix by input field

### ES
| Campo | Tipo input sugerido | Regla cliente | Regla servidor |
|---|---|---|---|
| email | email | formato HTML5 email | regex + unicidad |
| price | number step=0.01 min=0 | no negativos | decimal(10,2) >= 0 |
| salary | number step=0.01 min=0 | no negativos | > 0 |
| dateOfContract | date | fecha valida | ISO-8601 DateTime |
| color | color | selector nativo | regex #RRGGBB |
| countryCode | text maxlength=2 | longitud 2 | ISO alpha-2 |
| stockCount | number min=0 | entero no negativo | entero >= 0 |
| shelfCount | number min=0 | <= stockCount | <= stockCount y <= maxCapacity |

### EN
| Field | Suggested input type | Client rule | Server rule |
|---|---|---|---|
| email | email | HTML5 email format | regex + uniqueness |
| price | number step=0.01 min=0 | non-negative | decimal(10,2) >= 0 |
| salary | number step=0.01 min=0 | non-negative | > 0 |
| dateOfContract | date | valid date | ISO-8601 DateTime |
| color | color | native picker | regex #RRGGBB |
| countryCode | text maxlength=2 | length 2 | ISO alpha-2 |
| stockCount | number min=0 | non-negative integer | integer >= 0 |
| shelfCount | number min=0 | <= stockCount | <= stockCount and <= maxCapacity |

## 10. Read models for UI

### ES
Modelos de consulta recomendados:
- StoreListItem
  - id, name, image, countryCode, temperature, relativeHumidity
- StoreDetailView
  - Store base + shelves + inventory agrupado + tweets + notifications
- ProductListItem
  - id, name, image, size, color
- ProductDetailView
  - Product base + inventory agrupado por store/shelf
- EmployeeListItem
  - id, name, image, category, skills

### EN
Recommended query models:
- StoreListItem
  - id, name, image, countryCode, temperature, relativeHumidity
- StoreDetailView
  - base Store + shelves + grouped inventory + tweets + notifications
- ProductListItem
  - id, name, image, size, color
- ProductDetailView
  - base Product + inventory grouped by store/shelf
- EmployeeListItem
  - id, name, image, category, skills

## 11. Migration and backward compatibility

### ES
- Versionar cambios de esquema con etiqueta de version de documento.
- Evitar renombrar atributos NGSIv2 ya consumidos por frontend sin capa de compatibilidad.
- Si se introduce atributo nuevo obligatorio, definir valor por defecto o migracion.

### EN
- Version schema changes with document version tag.
- Avoid renaming NGSIv2 attributes already consumed by frontend without compatibility layer.
- If a new required attribute is introduced, define default value or migration path.

## 12. Open questions

### ES
1. Se necesita normalizar tweets como objetos estructurados (id, author, text, createdAt) o basta array de strings?
2. capacity de Store representa volumen total fisico o capacidad operativa configurable?
3. Se requiere historico temporal para price y stock (timeseries) en fase posterior?

### EN
1. Should tweets be normalized as structured objects (id, author, text, createdAt) or is string array enough?
2. Does Store capacity represent total physical volume or configurable operational capacity?
3. Is temporal history for price and stock (timeseries) required in a future phase?

## 13. Implementation alignment progress (Issue #1)

### ES
- Estado actual:
  - Se implemento un repositorio generico de entidades JSON para acelerar la primera iteracion.
  - Se mantiene la nomenclatura `id` + `type` compatible con NGSIv2 en operaciones base.
- Alineado ya en codigo:
  - Entidades operativas base: Store, Product, Employee, InventoryItem.
  - Flujo CRUD uniforme create/list/get/update/delete.
  - Contratos de subscription iniciales para cambios de `price` y bajo stock.
- Alineado y completado para cierre de Issue #1:
  - Dataset de prueba implementado y verificable con 4 stores, 10 products, 10 employees, 12 shelves y 55+ inventory items.
  - Script de carga dedicado `scripts/load_test_data.py` para provisionar entidades NGSIv2 de forma repetible.
  - Validaciones aplicadas en datos de prueba para enums, formatos, cardinalidades y relaciones esenciales.
  - Ajuste operativo: el script permite carga directa en SQLite para garantizar datos visibles en dashboard cuando Orion no es la fuente activa.
  - Ajuste de alcance minimo aplicado en ejecucion por defecto: 4 stores, 10 products y cobertura de al menos 5 productos por tienda.
- Pendiente para convergencia completa del modelo:
  - Validaciones campo a campo (rangos, regex, enums obligatorios).
  - Enforcement estricto de relaciones y reglas IR-001..IR-007.
  - Soporte completo de atributos complejos (`PostalAddress`, `geo:json`, `Array`) en UI y validacion server-side.
  - Modelado formal de Shelf en vistas y operaciones vinculadas por Store.
- Nota de estado:
  - El cierre de Issue #1 cubre el objetivo de aplicacion base y carga inicial de cadena de supermercados; la convergencia completa del modelo se mantiene como trabajo incremental.

### EN
- Current state:
  - A generic JSON-entity repository was implemented to accelerate the first iteration.
  - `id` + `type` naming compatible with NGSIv2 is preserved in baseline operations.
- Already aligned in code:
  - Baseline operational entities: Store, Product, Employee, InventoryItem.
  - Uniform CRUD flow create/list/get/update/delete.
  - Initial subscription contracts for `price` changes and low stock.
- Aligned and completed for Issue #1 closure:
  - Test dataset implemented and verifiable with 4 stores, 10 products, 10 employees, 12 shelves, and 55+ inventory items.
  - Dedicated loader script `scripts/load_test_data.py` to provision NGSIv2 entities in a repeatable way.
  - Validation applied in test data for enums, formats, cardinalities, and essential relationships.
  - Operational adjustment: the script supports direct SQLite loading to guarantee visible dashboard data when Orion is not the active source.
  - Minimum-scope adjustment applied in default execution: 4 stores, 10 products, and at least 5 products per store coverage.
- Pending for full model convergence:
  - Field-level validations (ranges, regex, required enums).
  - Strict relationship enforcement and IR-001..IR-007 rules.
  - Full support for complex attributes (`PostalAddress`, `geo:json`, `Array`) in UI and server-side validation.
  - Formal Shelf modeling in views and linked Store operations.
- Persistence note:
  - SQLite fallback storage path is now `instance/fiware.db`, preventing path collisions with non-directory entries in the project root.
- Status note:
  - Issue #1 closure covers the baseline app objective and supermarket-chain initial load; full model convergence remains incremental follow-up work.

## 14. Implementation alignment progress (Issue #2)

### ES
- Estado: Alineado e implementado para capa de presentacion.
- Cambios relevantes:
  - Se incorpora soporte ES/EN en UI sin modificar entidades NGSIv2 ni atributos de dominio.
  - El cambio de idioma afecta solo labels, titulos y textos de interfaz.
  - La persistencia del idioma se realiza en sesion HTTP.
- Impacto en modelo de datos:
  - Sin cambios de esquema para Store, Product, Employee, Shelf o InventoryItem.
  - Sin cambios en reglas IR-001..IR-007.

### EN
- Status: Aligned and implemented at presentation layer.
- Relevant changes:
  - ES/EN UI support is added without modifying NGSIv2 entities or domain attributes.
  - Language switch affects only labels, titles, and interface text.
  - Language persistence is handled through HTTP session.
- Data model impact:
  - No schema changes for Store, Product, Employee, Shelf, or InventoryItem.
  - No changes to IR-001..IR-007 rules.

## 15. Implementation alignment progress (Issue #3)

### ES
- Estado: Avance implementado y validado por pruebas automatizadas.
- Alineacion de modelo validada en esta iteracion:
  - Validaciones de payload y normalizacion NGSIv2 para entidades CRUD principales.
  - Reglas base de inventario verificadas en tests (conteos no negativos y consistencia de relaciones esperadas).
  - Cobertura de respuestas de endpoints para operaciones create/update/delete y manejo de errores de entrada.
  - Pruebas de integridad de distribucion minima en datos de prueba (productos por tienda y stock minimo agregado).
  - Escenario e2e validado para conmutacion Orion -> SQLite sin romper contratos de datos CRUD.
- Reglas de integridad con evidencia de test en esta iteracion:
  - IR-001: consistencia esperada entre `refShelf` y `refStore` cubierta por tests de integridad.
  - IR-002: no duplicidad por tripleta (store, shelf, product) cubierta por tests de integridad.
  - IR-003: capacidad de shelf no excedida cubierta por tests de integridad.

### EN
- Status: Implemented progress validated through automated tests.
- Model alignment validated in this iteration:
  - Payload validation and NGSIv2 normalization checks for core CRUD entities.
  - Baseline inventory rules verified by tests (non-negative counters and expected relationship consistency).
  - Endpoint response coverage for create/update/delete operations and input-error handling.
  - Minimum distribution integrity checks in seed data (products per store and minimum aggregate stock).
  - End-to-end scenario validated for Orion -> SQLite switch without breaking CRUD data contracts.
- Integrity rules with test evidence in this iteration:
  - IR-001: expected consistency between `refShelf` and `refStore` covered by integrity tests.
  - IR-002: no duplicate tuple (store, shelf, product) covered by integrity tests.
  - IR-003: shelf capacity not exceeded covered by integrity tests.

## 16. Implementation alignment progress (Issue #4)

### ES
- Estado: Alineacion implementada y cerrada para operaciones CRUD Store/Product bajo contrato NGSIv2.
- Alineacion de modelo aplicada:
  - Atributos de Store/Product se normalizan a estructura NGSIv2 (`type` + `value`) en create/update.
  - `Store.image` y `Product.image` quedan soportados de extremo a extremo (API, persistencia y vistas).
  - `Product.originCountry` queda soportado de extremo a extremo con validacion ISO alpha-2.
  - Se mantiene compatibilidad de entrada para `origin` legacy, mapeandolo a `originCountry`.
  - Dataset de referencia actualizado para usar URLs fijas curadas (Unsplash/Picsum) coherentes con la entidad representada.
  - Ajuste final aplicado en dataset: Stores alineadas a URLs concretas provistas con naming final Xantadis (Norte/Sur/Este/Oeste) y productos clave con URL explicita (manzana roja, leche).
- Reglas/validaciones con evidencia de test:
  - `Product.size` en enum `S|M|L|XL`.
  - `Product.color` con regex `#RRGGBB`.
  - `Product.price >= 0`.
  - `image` de Store/Product como URL valida `http/https`.

### EN
- Status: Alignment implemented and closed for Store/Product CRUD operations under NGSIv2 contract.
- Applied model alignment:
  - Store/Product attributes are normalized to NGSIv2 structure (`type` + `value`) on create/update.
  - `Store.image` and `Product.image` are supported end-to-end (API, persistence, and views).
  - `Product.originCountry` is supported end-to-end with ISO alpha-2 validation.
  - Backward-compatible input is preserved for legacy `origin`, mapped to `originCountry`.
  - Reference seed dataset now uses curated fixed image URLs (Unsplash/Picsum) that match the represented entity.
  - Final dataset refinement applied: Stores aligned to specific provided URLs with final Xantadis naming (North/South/East/West) and key products with explicit URLs (red apple, milk).
- Validation rules with test evidence:
  - `Product.size` in enum `S|M|L|XL`.
  - `Product.color` regex `#RRGGBB`.
  - `Product.price >= 0`.
  - Store/Product `image` must be a valid `http/https` URL.

## 17. Implementation alignment progress (Issue #5)

### ES
- Estado: Alineacion implementada y cerrada para contrato CRUD de Employee bajo NGSIv2.
- Alineacion de modelo aplicada:
  - Employee se normaliza a estructura NGSIv2 (`type` + `value`) para `name`, `image`, `salary`, `role` y `refStore`.
  - `refStore` se tipa como `Relationship` y se valida con URN de Store (`urn:ngsi-ld:Store:*`).
  - Se mantienen como opcionales los campos de compatibilidad (`category`, `email`, `skills`, `dateOfContract`, `username`, `password`).
  - Dataset de referencia de Employee incorpora `image` para soporte visual end-to-end.
- Reglas/validaciones con evidencia de test:
  - `Employee.image` URL valida `http/https`.
  - `Employee.salary` numerico y `>= 0`.
  - `Employee.role` no vacio.
  - `Employee.refStore` con URN valida de Store.

### EN
- Status: Alignment implemented and closed for Employee CRUD contract under NGSIv2.
- Applied model alignment:
  - Employee is normalized to NGSIv2 structure (`type` + `value`) for `name`, `image`, `salary`, `role`, and `refStore`.
  - `refStore` is typed as `Relationship` and validated against Store URN format (`urn:ngsi-ld:Store:*`).
  - Compatibility fields remain optional (`category`, `email`, `skills`, `dateOfContract`, `username`, `password`).
  - Employee reference dataset now includes `image` for end-to-end visual support.
- Validation rules with test evidence:
  - `Employee.image` must be a valid `http/https` URL.
  - `Employee.salary` must be numeric and `>= 0`.
  - `Employee.role` must be non-empty.
  - `Employee.refStore` must contain a valid Store URN.

## 18. Implementation alignment progress (Issue #6)

### ES
- Estado: Alineacion implementada y cerrada para consumo UI de ubicacion e imagenes.
- Alineacion de modelo aplicada:
  - `Store.location` (GeoJSON Point) se consume en detalle de tienda para renderizar mapa Leaflet con marcador.
  - Se mantiene el contrato NGSIv2 original de `location`; la transformacion a lat/lng se realiza en capa de presentacion.
  - Atributos `image` de Store/Product/Employee conservan contrato `Text` y fallback visual uniforme en templates.
- Reglas/validaciones con evidencia de test:
  - Integridad de navegacion principal validada por smoke tests (4 secciones operativas).
  - Render de contenedor de mapa en detalle de Store validado por smoke tests.

### EN
- Status: Alignment implemented and closed for UI consumption of location and image attributes.
- Applied model alignment:
  - `Store.location` (GeoJSON Point) is consumed in Store detail to render a Leaflet map marker.
  - Original NGSIv2 contract for `location` remains unchanged; lat/lng adaptation is handled in the presentation layer.
  - Store/Product/Employee `image` attributes keep the `Text` contract with unified visual fallback behavior in templates.
- Validation rules with test evidence:
  - Main navigation integrity validated by smoke tests (4 operational sections).
  - Store detail map-container rendering validated by smoke tests.

## 19. Implementation alignment progress (Store detail normalization)

### ES
- Estado: Alineacion aplicada en capa de vista sin cambios de esquema NGSIv2.
- Alineacion de modelo aplicada:
  - El atributo `Store.id` conserva formato URN en persistencia/API; la UI muestra solo el sufijo operativo (`S001`).
  - El atributo `Store.countryCode` conserva ISO alpha-2 en datos; la UI lo transforma a nombre completo de pais para lectura humana.
  - El atributo `Store.address` (PostalAddress) se expone completo en detalle con `streetAddress`, `addressLocality`, `addressRegion`.
  - El atributo `Store.type` permanece en contrato NGSIv2 pero deja de mostrarse en la ficha de detalle por redundancia.
- Evidencia de validacion:
  - Smoke test de detalle de tienda verifica ID simplificado, pais expandido, direccion visible y ausencia de campo `Type`.

### EN
- Status: Alignment applied at view layer with no NGSIv2 schema changes.
- Applied model alignment:
  - `Store.id` remains URN-formatted in persistence/API; UI renders only the operational suffix (`S001`).
  - `Store.countryCode` remains ISO alpha-2 in data; UI transforms it into full country name for human readability.
  - `Store.address` (PostalAddress) is fully exposed in detail view with `streetAddress`, `addressLocality`, `addressRegion`.
  - `Store.type` remains part of NGSIv2 contract but is no longer displayed in detail UI due to redundancy.
- Validation evidence:
  - Store-detail smoke test validates simplified ID, expanded country name, visible full address, and `Type` field removal.

## 20. Implementation alignment progress (Global entity-format normalization)

### ES
- Estado: Alineacion aplicada en capa de vista sin cambios de esquema NGSIv2.
- Alineacion de modelo aplicada:
  - `Store.id`, `Product.id` y `Employee.id` conservan URN en persistencia/API; UI muestra solo sufijo operativo.
  - `Employee.refStore` conserva URN en datos y se renderiza simplificado en vistas de listado/detalle.
  - `Store.countryCode` y `Product.originCountry` mantienen ISO alpha-2 y se renderizan como nombre completo (`ES`, `DE`, `FR`, `EC`) segun idioma activo.
  - `type` permanece en contrato NGSIv2 para las entidades, pero deja de mostrarse en las vistas detalle de Store/Product/Employee.
- Evidencia de validacion:
  - Smoke test transversal valida formato simplificado de IDs y referencias, expansion de paises y eliminacion de `Type` en detalles.

### EN
- Status: Alignment applied at view layer with no NGSIv2 schema changes.
- Applied model alignment:
  - `Store.id`, `Product.id`, and `Employee.id` remain URN-formatted in persistence/API; UI renders only operational suffixes.
  - `Employee.refStore` remains URN-formatted in data and is rendered simplified in list/detail views.
  - `Store.countryCode` and `Product.originCountry` remain ISO alpha-2 values and are rendered as full names (`ES`, `DE`, `FR`, `EC`) based on active language.
  - `type` remains part of NGSIv2 entity contracts but is no longer shown in Store/Product/Employee detail views.
- Validation evidence:
  - Cross-view smoke test validates simplified ID/reference formatting, country-name expansion, and `Type` removal in detail pages.

## 21. Implementation alignment progress (Issue #7 CRUD in detail views)

### ES
- Estado: Alineacion implementada para operaciones CRUD de `Shelf` e `InventoryItem` desde vistas de detalle.
- Alineacion de modelo aplicada:
  - `Shelf` incorporado en normalizacion/validacion NGSIv2 con campos:
    - `name` (Text)
    - `location` (geo:json)
    - `maxCapacity` (Integer)
    - `refStore` (Relationship)
  - `InventoryItem` reforzado en normalizacion/validacion NGSIv2 con campos:
    - `refStore`, `refShelf`, `refProduct` (Relationship)
    - `stockCount`, `shelfCount` (Integer)
  - Reglas de integridad aplicadas en operaciones:
    - `refShelf` debe pertenecer a `refStore`.
    - no duplicar tripleta (`refStore`, `refShelf`, `refProduct`).
    - `shelfCount <= stockCount`.
    - suma de `shelfCount` por shelf no supera `maxCapacity`.
    - borrado de shelf bloqueado con `409` si existen InventoryItems dependientes.
- Evidencia de validacion:
  - Pruebas de integracion y smoke amplian cobertura para CRUD anidado en Store/Product detail.

### EN
- Status: Alignment implemented for `Shelf` and `InventoryItem` CRUD operations from detail views.
- Applied model alignment:
  - `Shelf` added to NGSIv2 normalization/validation with fields:
    - `name` (Text)
    - `location` (geo:json)
    - `maxCapacity` (Integer)
    - `refStore` (Relationship)
  - `InventoryItem` validation reinforced in NGSIv2 normalization with fields:
    - `refStore`, `refShelf`, `refProduct` (Relationship)
    - `stockCount`, `shelfCount` (Integer)
  - Integrity rules enforced in operations:
    - `refShelf` must belong to `refStore`.
    - duplicate (`refStore`, `refShelf`, `refProduct`) tuples are rejected.
    - `shelfCount <= stockCount`.
    - per-shelf `shelfCount` sum cannot exceed `maxCapacity`.
    - shelf deletion is blocked with `409` when dependent InventoryItems exist.
- Validation evidence:
  - Integration and smoke tests extend coverage for nested CRUD in Store/Product detail contexts.

## 22. Closure status (Issue #7)

### ES
- Estado de alineacion:
  - La alineacion de `Shelf` e `InventoryItem` para CRUD contextual queda consolidada en `main`.
  - Reglas IR aplicadas en runtime para consistencia relacional y capacidad.
- Estado de sincronizacion:
  - Sin diferencias entre rama de trabajo de Issue #7 y `main` tras merge/sync.
- Estado de ticket:
  - El recurso `issues/7` no esta disponible por API publica en el momento de cierre tecnico.

### EN
- Alignment status:
  - `Shelf` and `InventoryItem` alignment for context-scoped CRUD is consolidated on `main`.
  - IR rules are enforced at runtime for relationship and capacity consistency.
- Synchronization status:
  - No diffs remain between Issue #7 branch and `main` after merge/sync.
- Ticket status:
  - `issues/7` resource is not available via public API at technical closure time.
