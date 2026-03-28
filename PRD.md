# PRD - fiware-smart-store

## 1. Document control

### ES
- Version: 1.0
- Fecha: 2026-03-28
- Estado: Baseline para implementacion
- Producto: fiware-smart-store
- Tipo de documento: Product Requirements Document

### EN
- Version: 1.0
- Date: 2026-03-28
- Status: Baseline for implementation
- Product: fiware-smart-store
- Document type: Product Requirements Document

## 2. Product vision and goals

### ES
fiware-smart-store es una aplicacion web Flask para gestionar una cadena de supermercados con FIWARE Orion Context Broker como fuente principal de datos (NGSIv2), con fallback a SQLite cuando Orion no esta disponible.

Objetivos de producto:
1. Permitir CRUD completo de tiendas, productos, empleados, estanterias e items de inventario.
2. Exponer cambios de contexto en tiempo real mediante subscriptions NGSIv2 y Flask-SocketIO.
3. Mostrar datos externos de contexto (temperature, relativeHumidity, tweets) asociados a cada tienda.
4. Ofrecer una UI moderna, compacta, bilingue (ES/EN) y con modo dark/light.
5. Mantener trazabilidad entre requisitos funcionales y modelo de datos NGSIv2.

### EN
fiware-smart-store is a Flask web application to manage a supermarket chain with FIWARE Orion Context Broker as the primary data source (NGSIv2), with SQLite fallback when Orion is unavailable.

Product goals:
1. Provide full CRUD for stores, products, employees, shelves, and inventory items.
2. Surface real-time context changes through NGSIv2 subscriptions and Flask-SocketIO.
3. Display external context data (temperature, relativeHumidity, tweets) for each store.
4. Deliver a modern, compact UI, bilingual (ES/EN), with dark/light mode.
5. Keep traceability between functional requirements and the NGSIv2 data model.

## 3. Scope

### ES
Incluido en esta fase:
- Backend Flask con modulos de rutas por dominio.
- Integracion Orion NGSIv2 para operaciones CRUD y subscripciones.
- Fallback SQLite para continuidad operativa local.
- Dashboard, vistas de listado y detalle por entidad, stores map.
- Notificaciones servidor-cliente en tiempo real.
- Soporte idioma ES/EN y tema dark/light.
- Docker compose para entorno local de desarrollo.

Fuera de alcance:
- Hardening de seguridad productiva (WAF, IDS, SIEM).
- Escalado horizontal multi-region.
- Integracion ERP/BI corporativa.
- Aplicacion movil nativa.

### EN
Included in this phase:
- Flask backend with domain-based routing modules.
- Orion NGSIv2 integration for CRUD operations and subscriptions.
- SQLite fallback for local operational continuity.
- Dashboard, list and detail views per entity, stores map.
- Real-time server-to-client notifications.
- ES/EN language support and dark/light theme.
- Docker compose for local development environment.

Out of scope:
- Production security hardening (WAF, IDS, SIEM).
- Multi-region horizontal scaling.
- Corporate ERP/BI integration.
- Native mobile app.

## 4. Stakeholders and users

### ES
- Product Owner academico: valida alcance de practica y criterios de evaluacion.
- Equipo de desarrollo: implementa backend, frontend e integraciones.
- Usuario operador de cadena: gestiona tiendas, stock y personal.
- Usuario supervisor: consulta metricas y alertas de bajo stock.

### EN
- Academic Product Owner: validates assignment scope and grading criteria.
- Development team: implements backend, frontend, and integrations.
- Chain operator user: manages stores, stock, and staff.
- Supervisor user: reviews metrics and low-stock alerts.

## 5. User journeys

### ES
1. Como operador quiero crear una tienda con geolocalizacion para poder asignar estanterias e inventario.
2. Como operador quiero ver y editar productos para mantener precio, talla y color actualizados.
3. Como operador quiero asociar inventario por tienda y estanteria para controlar stock real.
4. Como supervisor quiero recibir alertas de bajo stock sin recargar la pagina.
5. Como supervisor quiero detectar cambios de precio de producto en tiempo real.
6. Como usuario quiero cambiar idioma y tema visual para adaptar la interfaz.

### EN
1. As an operator, I want to create a store with geolocation so I can assign shelves and inventory.
2. As an operator, I want to view and edit products to keep price, size, and color updated.
3. As an operator, I want to map inventory by store and shelf to control real stock.
4. As a supervisor, I want low-stock alerts without page refresh.
5. As a supervisor, I want to detect product price changes in real time.
6. As a user, I want language and visual theme toggles to adapt the UI.

## 6. Functional requirements

### ES

#### 6.1 Core platform
- FR-001: El sistema debe arrancar comprobando conectividad con Orion.
- FR-002: Si Orion responde, el sistema usa Orion como fuente principal.
- FR-003: Si Orion no responde, el sistema usa SQLite fallback sin interrumpir UI.
- FR-004: El sistema debe registrar providers externos de temperature, relativeHumidity y tweets al arrancar.
- FR-005: El sistema debe registrar subscriptions NGSIv2 para cambio de precio y bajo stock.

#### 6.2 Stores
- FR-010: Listado de stores con imagen, nombre, countryCode, temperature y relativeHumidity.
- FR-011: CRUD completo de stores con validacion HTML5 y JS.
- FR-012: Vista detalle store con mapa Leaflet y ubicacion geojson.
- FR-013: Vista detalle store con area 3D Three.js del recorrido de estanterias.
- FR-014: Vista detalle store con tabla InventoryItems agrupada por shelf.
- FR-015: Vista detalle store con barra de progreso de llenado por shelf.
- FR-016: Vista detalle store con panel de notificaciones en tiempo real.
- FR-017: CRUD de shelves desde detalle store.
- FR-018: CRUD de inventory items desde detalle store.

#### 6.3 Products
- FR-020: Listado de productos con imagen, nombre, color, size y acciones editar/borrar.
- FR-021: CRUD completo de products con validacion HTML5 y JS.
- FR-022: Vista detalle product con InventoryItems agrupados por store y shelf.
- FR-023: CRUD de inventory items desde detalle product.
- FR-024: Select dinamico de shelves segun store seleccionada.

#### 6.4 Employees
- FR-030: Listado empleados con imagen, nombre, category, skills e iconos asociados.
- FR-031: CRUD completo de employees con validacion HTML5 y JS.
- FR-032: Imagen de empleado con efecto zoom en hover (CSS).

#### 6.5 Dashboard and map
- FR-040: Home dashboard con metricas de stores, products, employees e inventory items.
- FR-041: Render de diagrama UML con Mermaid en dashboard.
- FR-042: Stores map con Leaflet y marcadores de todas las tiendas.
- FR-043: Hover en marcador muestra tarjeta flotante con datos principales.
- FR-044: Click en marcador navega a detalle de store.

#### 6.6 UX and visual standards
- FR-050: Soporte bilingue ES/EN en toda la app.
- FR-051: Toggle dark/light funcional y persistente por sesion.
- FR-052: Navbar fija en scroll con seccion activa resaltada.
- FR-053: Efectos visuales priorizan CSS sobre JS.
- FR-054: JS cliente no crea HTML nuevo; solo actualiza atributos en nodos existentes.

#### 6.7 Real-time notifications
- FR-060: Notificacion de cambio de precio debe actualizar vistas de producto activas sin reload.
- FR-061: Notificacion de bajo stock debe aparecer en panel de detalle store.
- FR-062: Integracion Socket.IO cliente-servidor debe mantener conexion estable y reconexion.

### EN

#### 6.1 Core platform
- FR-001: The system must check Orion connectivity on startup.
- FR-002: If Orion is reachable, Orion is the primary data source.
- FR-003: If Orion is unreachable, SQLite fallback is used without UI interruption.
- FR-004: The system must register external providers for temperature, relativeHumidity, and tweets at startup.
- FR-005: The system must register NGSIv2 subscriptions for price change and low stock.

#### 6.2 Stores
- FR-010: Store list with image, name, countryCode, temperature, and relativeHumidity.
- FR-011: Full store CRUD with HTML5 and JS validation.
- FR-012: Store detail page with Leaflet map and geojson location.
- FR-013: Store detail page with Three.js shelf walkthrough area.
- FR-014: Store detail page with InventoryItems table grouped by shelf.
- FR-015: Store detail page with fill progress bar by shelf.
- FR-016: Store detail page with real-time notifications panel.
- FR-017: Shelf CRUD from store detail.
- FR-018: Inventory item CRUD from store detail.

#### 6.3 Products
- FR-020: Product list with image, name, color swatch, size, edit/delete actions.
- FR-021: Full product CRUD with HTML5 and JS validation.
- FR-022: Product detail with InventoryItems grouped by store and shelf.
- FR-023: Inventory item CRUD from product detail.
- FR-024: Dynamic shelf select filtered by selected store.

#### 6.4 Employees
- FR-030: Employee list with image, name, category, skills, mapped icons.
- FR-031: Full employee CRUD with HTML5 and JS validation.
- FR-032: Employee image hover zoom effect (CSS).

#### 6.5 Dashboard and map
- FR-040: Home dashboard with metrics for stores, products, employees, inventory items.
- FR-041: UML diagram rendered with Mermaid on dashboard.
- FR-042: Stores map using Leaflet with markers for all stores.
- FR-043: Marker hover displays floating card with main store data.
- FR-044: Marker click navigates to store detail.

#### 6.6 UX and visual standards
- FR-050: Full ES/EN bilingual support.
- FR-051: Functional dark/light toggle persisted per session.
- FR-052: Sticky navbar with active section highlight.
- FR-053: Visual effects should prioritize CSS over JS.
- FR-054: Client JS must not generate new HTML; only update existing node attributes.

#### 6.7 Real-time notifications
- FR-060: Price change notification must update active product views without reload.
- FR-061: Low-stock notification must appear on store detail notification panel.
- FR-062: Socket.IO client-server integration must keep stable connection and reconnect.

## 7. Non-functional requirements

### ES
- NFR-001 Disponibilidad local de desarrollo >= 95% durante ejecucion de practicas.
- NFR-002 Tiempo de respuesta p95 en CRUD < 500 ms con dataset de prueba inicial.
- NFR-003 UI responsive usable en 360px a 1920px.
- NFR-004 Compatibilidad navegadores modernos (Chrome, Edge, Firefox ultimas 2 versiones).
- NFR-005 Seguridad minima: hash de password, validacion de input y escape de salida.
- NFR-006 Observabilidad basica: logs de errores de integracion Orion y SocketIO.
- NFR-007 Mantenibilidad: separacion por blueprints y modulos de dominio.
- NFR-008 Testabilidad: cobertura de tests unitarios e integracion CRUD por entidad.

### EN
- NFR-001 Local development availability >= 95% during practice sessions.
- NFR-002 p95 response time for CRUD < 500 ms with initial sample dataset.
- NFR-003 Responsive UI usable from 360px to 1920px.
- NFR-004 Modern browser compatibility (Chrome, Edge, Firefox latest 2 versions).
- NFR-005 Minimum security: password hashing, input validation, output escaping.
- NFR-006 Basic observability: integration error logs for Orion and SocketIO.
- NFR-007 Maintainability: separation by blueprints and domain modules.
- NFR-008 Testability: unit and integration test coverage for entity CRUD.

## 8. Acceptance criteria

### ES
- AC-001: Al arrancar, la app detecta Orion y cambia automaticamente entre Orion y SQLite.
- AC-002: CRUD de las 5 entidades funciona desde UI y persiste en fuente activa.
- AC-003: Suscripcion de cambio de precio propaga evento y actualiza UI en menos de 2 segundos.
- AC-004: Suscripcion de bajo stock genera alerta visible en detalle de tienda en menos de 2 segundos.
- AC-005: Providers externos aportan temperature, relativeHumidity y tweets visibles en detalle store.
- AC-006: Toggle ES/EN cambia textos de navegacion, botones, labels y validaciones de formularios.
- AC-007: Toggle dark/light cambia tema completo y se mantiene durante la sesion.
- AC-008: Dashboard muestra conteos correctos para stores/products/employees/inventory items.
- AC-009: Stores map permite hover informativo y click navegable a detalle store.

### EN
- AC-001: On startup, the app detects Orion and automatically switches between Orion and SQLite.
- AC-002: CRUD for all 5 entities works from UI and persists in active data source.
- AC-003: Price-change subscription propagates event and updates UI in under 2 seconds.
- AC-004: Low-stock subscription raises visible alert on store detail in under 2 seconds.
- AC-005: External providers supply temperature, relativeHumidity, and tweets visible on store detail.
- AC-006: ES/EN toggle changes navigation text, buttons, labels, and form validation text.
- AC-007: Dark/light toggle updates full theme and remains during session.
- AC-008: Dashboard shows correct counts for stores/products/employees/inventory items.
- AC-009: Stores map supports informative hover and clickable navigation to store detail.

## 9. Dependencies and assumptions

### ES
Dependencias:
- Orion Context Broker (NGSIv2) y MongoDB en Docker.
- Contenedor tutorial FIWARE para context providers y datos externos.
- Flask, Flask-SocketIO, Socket.IO client, Leaflet, Three.js, Mermaid, Font Awesome.

Supuestos:
- La red Docker permite resolver host.docker.internal para callbacks de subscriptions.
- El dataset inicial contiene al menos 4 stores, 10 products, 4 employees y stock representativo.
- El usuario operador tiene permisos de CRUD en todas las vistas.

### EN
Dependencies:
- Orion Context Broker (NGSIv2) and MongoDB in Docker.
- FIWARE tutorial container for context providers and external data.
- Flask, Flask-SocketIO, Socket.IO client, Leaflet, Three.js, Mermaid, Font Awesome.

Assumptions:
- Docker networking resolves host.docker.internal for subscription callbacks.
- Initial dataset includes at least 4 stores, 10 products, 4 employees, and representative stock.
- Operator user has CRUD permissions in all views.

## 10. Risks and mitigations

### ES
- Riesgo R1: Fallos de conectividad Orion. Mitigacion: fallback SQLite y health-check inicial.
- Riesgo R2: Notificaciones no recibidas por URL de callback incorrecta. Mitigacion: usar host.docker.internal y pruebas de humo.
- Riesgo R3: Inconsistencia entre UI y fuente de datos activa. Mitigacion: capa adaptadora unica para acceso datos.
- Riesgo R4: Complejidad de vista 3D impacta performance. Mitigacion: degradacion progresiva y carga diferida.

### EN
- Risk R1: Orion connectivity failures. Mitigation: SQLite fallback and startup health check.
- Risk R2: Notifications not received due to wrong callback URL. Mitigation: use host.docker.internal and smoke tests.
- Risk R3: Inconsistency between UI and active data source. Mitigation: single adapter layer for data access.
- Risk R4: 3D view complexity impacts performance. Mitigation: progressive degradation and lazy loading.

## 11. Requirement traceability matrix

### ES
| Requirement ID | Modulo principal | Entidades | Criterio de aceptacion |
|---|---|---|---|
| FR-001..FR-005 | Plataforma core | Store, Product, InventoryItem | AC-001, AC-003, AC-004, AC-005 |
| FR-010..FR-018 | Stores | Store, Shelf, InventoryItem | AC-002, AC-004, AC-005 |
| FR-020..FR-024 | Products | Product, InventoryItem, Shelf | AC-002, AC-003 |
| FR-030..FR-032 | Employees | Employee | AC-002 |
| FR-040..FR-044 | Dashboard y Map | Store, Product, Employee, InventoryItem | AC-008, AC-009 |
| FR-050..FR-054 | UX transversal | Todas | AC-006, AC-007 |
| FR-060..FR-062 | Notificaciones realtime | Product, InventoryItem, Store | AC-003, AC-004 |

### EN
| Requirement ID | Main module | Entities | Acceptance criteria |
|---|---|---|---|
| FR-001..FR-005 | Core platform | Store, Product, InventoryItem | AC-001, AC-003, AC-004, AC-005 |
| FR-010..FR-018 | Stores | Store, Shelf, InventoryItem | AC-002, AC-004, AC-005 |
| FR-020..FR-024 | Products | Product, InventoryItem, Shelf | AC-002, AC-003 |
| FR-030..FR-032 | Employees | Employee | AC-002 |
| FR-040..FR-044 | Dashboard and Map | Store, Product, Employee, InventoryItem | AC-008, AC-009 |
| FR-050..FR-054 | Cross-cutting UX | All | AC-006, AC-007 |
| FR-060..FR-062 | Real-time notifications | Product, InventoryItem, Store | AC-003, AC-004 |

## 12. Open questions

### ES
1. El mecanismo de autenticacion sera solo demo o habra roles persistentes por usuario?
2. Se requiere versionado de cambios para auditoria de inventario y precios?
3. El recorrido 3D debe reflejar ubicacion real de shelves o solo una representacion simbolica?

### EN
1. Will authentication stay demo-only, or require persisted role-based users?
2. Is change versioning required for inventory and price auditing?
3. Should the 3D walkthrough reflect actual shelf geometry or a symbolic representation?

## 13. Implementation progress (Issue #1)

### ES
- Estado: Completado para Issue #1.
- Alcance implementado y validado:
	- Estructura base Flask y app factory operativa.
	- Blueprints CRUD para Stores, Products, Employees, Inventory y Notifications.
	- Capa de seleccion de fuente de datos Orion-first con fallback SQLite.
	- Script de carga de datos de prueba `scripts/load_test_data.py` con opciones `--clean`, `--dry-run` y `--verbose`.
	- Carga objetivo cumplida: 4 stores, 10 products, 10 employees, 12 shelves y 55+ inventory items.
	- Suites de tests agregadas para stores, products, employees, inventory y data loading.
- Cobertura de requisitos lograda en Issue #1:
	- FR-001, FR-002, FR-003: implementados y operativos.
	- FR-005, FR-060, FR-061: baseline de webhooks y emision realtime implementado.
	- FR-010, FR-020, FR-030, FR-040: version funcional inicial completada.
	- AC de datos base cumplidos: cadena de supermercados inicial cargable y verificable.
- Ajustes tecnicos aplicados:
	- Ruta SQLite por defecto movida a `instance/fiware.db` para evitar conflicto con la entrada `services`.
	- Normalizacion defensiva de rutas SQLite en el repositorio local.
	- Script de carga actualizado para soportar destino `sqlite` (por defecto), permitiendo inicializacion local sin dependencia de Orion.
	- Enlaces de navegacion principales ajustados a rutas directas (`/stores`, `/products`, `/employees`) y rutas Flask tolerantes con/sin slash final.
	- Carga inicial alineada al enunciado minimo: 4 stores, 10 products y al menos 5 productos por tienda.
- Pendiente para siguientes iteraciones:
	- UI avanzada (Leaflet, Three.js, Mermaid y mejoras de experiencia visual).
	- i18n ES/EN completo y toggle dark/light persistente.
	- Endurecimiento de validaciones avanzadas y pruebas E2E.

### EN
- Status: Completed for Issue #1.
- Implemented and validated scope:
	- Operational Flask base structure and app factory.
	- CRUD blueprints for Stores, Products, Employees, Inventory, and Notifications.
	- Orion-first data source selector with SQLite fallback.
	- Test data loader script `scripts/load_test_data.py` with `--clean`, `--dry-run`, and `--verbose`.
	- Target dataset delivered: 4 stores, 10 products, 10 employees, 12 shelves, and 55+ inventory items.
	- Test suites added for stores, products, employees, inventory, and data loading.
- Requirement coverage achieved in Issue #1:
	- FR-001, FR-002, FR-003: implemented and working.
	- FR-005, FR-060, FR-061: webhook and realtime emission baseline implemented.
	- FR-010, FR-020, FR-030, FR-040: initial functional version completed.
	- Base-data acceptance for supermarket chain startup is satisfied.
- Technical adjustments applied:
	- Default SQLite path moved to `instance/fiware.db` to avoid collisions with existing `services` entry.
	- Defensive SQLite path normalization added to local repository.
	- Loader script updated to support `sqlite` target (default), enabling local bootstrap without Orion dependency.
	- Main navigation links adjusted to direct routes (`/stores`, `/products`, `/employees`) and Flask routes now accept with/without trailing slash.
	- Initial load aligned with minimum statement scope: 4 stores, 10 products, and at least 5 products per store.
- Pending for next iterations:
	- Advanced UI (Leaflet, Three.js, Mermaid, and richer visual behavior).
	- Persistent dark/light toggle.
	- Advanced validation hardening and end-to-end testing.

## 14. Implementation progress (Issue #2)

### ES
- Estado: Implementado (iteracion inicial de i18n UI).
- Alcance implementado:
	- Soporte multi-idioma ES/EN con seleccion en interfaz (navbar).
	- Persistencia de idioma por sesion de usuario.
	- Traduccion de textos principales en dashboard, barra de navegacion y vistas stores/products/employees.
	- Endpoint de cambio de idioma con redireccion segura a la pagina actual.
- Cobertura de requisitos:
	- FR-050: soporte bilingue ES/EN implementado en vistas principales.
	- Flujo de navegacion validado tras cambio de idioma.

### EN
- Status: Implemented (initial UI i18n iteration).
- Implemented scope:
	- ES/EN multi-language support with UI selector in navbar.
	- Session-based language persistence.
	- Main text translation in dashboard, navbar, and stores/products/employees views.
	- Language-switch endpoint with safe redirect back to current page.
- Requirement coverage:
	- FR-050: ES/EN bilingual support implemented in core views.
	- Navigation flow validated after language switch.

## 15. Implementation progress (Issue #3)

### ES
- Estado: Implementacion de bateria de pruebas completada para la iteracion actual.
- Resultado de validacion:
	- Suite ejecutada con exito: 87 passed.
- Cobertura agregada en esta iteracion:
	- Tests unitarios para utilidades, `OrionClient` y capa de datos (selector/fallback SQLite).
	- Tests de integracion para CRUD de stores, products, employees e inventory.
	- Tests e2e de flujo completo (store -> product -> inventory) y fallback Orion -> SQLite.
	- Tests de endpoint de notificaciones (price change y low stock).
	- Correcciones en tests legacy del cargador de datos para reflejar el comportamiento real del modo Orion.
- Trazabilidad de requisitos:
	- FR-001, FR-002, FR-003: verificados por pruebas de seleccion de fuente y fallback.
	- FR-010, FR-020, FR-030 y FR-040: cubiertos por pruebas de rutas y respuestas JSON.
	- FR-060 y FR-061: cubiertos por pruebas de webhooks de notificaciones.
	- NFR-008: reforzado con nueva bateria de pruebas unitarias e integracion.

### EN
- Status: Test battery implementation completed for the current iteration.
- Validation result:
	- Test suite executed successfully: 87 passed.
- Coverage added in this iteration:
	- Unit tests for utilities, `OrionClient`, and data layer (selector/SQLite fallback).
	- Integration tests for CRUD across stores, products, employees, and inventory.
	- End-to-end tests for full flow (store -> product -> inventory) and Orion -> SQLite fallback.
	- Notification endpoint tests (price change and low stock).
	- Legacy loader test fixes to reflect actual Orion-mode behavior.
- Requirement traceability:
	- FR-001, FR-002, FR-003 verified through source-selection and fallback tests.
	- FR-010, FR-020, FR-030, and FR-040 covered through route and JSON response tests.
	- FR-060 and FR-061 covered through notification webhook tests.
	- NFR-008 strengthened with the new unit and integration test battery.

## 16. Implementation progress (Issue #4)

### ES
- Estado: Implementacion completada y cerrada para la alineacion NGSIv2 en Store/Product y vistas core.
- Resultado de validacion:
	- Suite ejecutada con exito: 95 passed.
- Alcance implementado en esta iteracion:
	- Normalizacion y validacion NGSIv2 para CRUD de Store y Product (create/update).
	- Soporte de atributos `image` en Store y Product y `originCountry` en Product en API, fixtures y vistas.
	- Compatibilidad con payload legacy de Product (`origin` -> `originCountry`).
	- Navegacion principal acotada a dashboard, stores y products.
	- Vistas de detalle de Store/Product actualizadas con nuevos atributos.
	- Rediseño visual integral con layout de panel administrativo, tipografia consistente, tablas/cards mejor maquetadas y responsive.
	- URLs de imagen curadas y fijas en datos semilla para coherencia semantica (tiendas reales y productos reales).
	- Ajuste final de UX en navbar: etiqueta principal visible como Dashboard (EN) y Panel (ES).
	- Ajuste final de imagenes y branding: Stores alineadas a URLs especificas y nomenclatura final Xantadis (Norte/Sur/Este/Oeste), y Product con ejemplos explicitos para manzana roja y leche.
- Trazabilidad de requisitos:
	- FR-010: listado/detalle de tiendas enriquecido con `image`.
	- FR-020: listado/detalle de productos enriquecido con `image` y `originCountry`.
	- FR-040: dashboard se mantiene como vista principal operativa.
	- NFR-008: cobertura ampliada con pruebas de validacion NGSIv2 y contratos de rutas.

### EN
- Status: Implementation completed and closed for NGSIv2 alignment on Store/Product and core views.
- Validation result:
	- Test suite executed successfully: 95 passed.
- Implemented scope in this iteration:
	- NGSIv2 normalization and validation for Store/Product CRUD (create/update).
	- Support for `image` on Store and Product, and `originCountry` on Product across API, fixtures, and views.
	- Backward compatibility for legacy Product payloads (`origin` -> `originCountry`).
	- Main navigation focused on dashboard, stores, and products.
	- Store/Product detail views updated with the new attributes.
	- Full visual redesign with admin-panel layout, consistent typography, improved cards/tables, and responsive behavior.
	- Curated fixed image URLs in seed data to keep entity-semantic coherence (real stores and real products).
	- Final UX refinement in navbar: primary label shown as Dashboard (EN) and Panel (ES).
	- Final image and branding refinement: Stores aligned to specified URLs and final Xantadis naming (North/South/East/West), and Product with explicit examples for red apple and milk.
- Requirement traceability:
	- FR-010: store list/detail enriched with `image`.
	- FR-020: product list/detail enriched with `image` and `originCountry`.
	- FR-040: dashboard remains operational as a main view.
	- FR-050/UX visual: professional and consistent UI style across the three main views.
	- NFR-008: expanded coverage with NGSIv2 validation and route contract tests.

## 17. Implementation progress (Issue #5)

### ES
- Estado: Implementacion completada y cerrada para contrato Employee con atributos obligatorios.
- Resultado de validacion:
	- Suite ejecutada con exito: 101 passed.
- Alcance implementado en esta iteracion:
	- Employee queda alineado con atributos obligatorios `id`, `name`, `image`, `salary`, `role`, `refStore` en create/update.
	- Se mantiene compatibilidad con atributos legacy/extensibles de Employee (`category`, `email`, `skills`, `dateOfContract`, `username`, `password`).
	- Vistas de Employees (listado/detalle) muestran atributos obligatorios y conservan visualizacion de campos opcionales.
	- Datos semilla de Employee incorporan `image` y mantienen `salary`, `role` y `refStore` en formato NGSIv2.
	- Cobertura de pruebas ampliada en unit/integration para validaciones de Employee (URL de image, salario, role, refStore).
- Trazabilidad de requisitos:
	- FR-031: CRUD de employees reforzado con validacion de atributos obligatorios.
	- FR-030: listado/detalle de employees enriquecido con `image`, `role`, `salary` y referencia de tienda.

### EN
- Status: Implementation completed and closed for Employee required-attribute contract.
- Validation result:
	- Test suite executed successfully: 101 passed.
- Implemented scope in this iteration:
	- Employee is aligned with required attributes `id`, `name`, `image`, `salary`, `role`, `refStore` on create/update.
	- Backward compatibility is preserved for legacy/extensible Employee attributes (`category`, `email`, `skills`, `dateOfContract`, `username`, `password`).
	- Employee views (list/detail) now expose required attributes while keeping optional fields visible.
	- Employee seed data now includes `image` and keeps `salary`, `role`, and `refStore` in NGSIv2 format.
	- Test coverage was expanded in unit/integration for Employee validations (image URL, salary, role, refStore).
- Requirement traceability:
	- FR-031: employee CRUD strengthened with required-attribute validation.
	- FR-030: employee list/detail enriched with `image`, `role`, `salary`, and store reference.

## 18. Implementation progress (Issue #6)

### ES
- Estado: Implementacion completada y cerrada para robustez UI (mapa, imagenes y navegacion).
- Resultado de validacion:
	- Suite ejecutada con exito: 103 passed.
- Alcance implementado en esta iteracion:
	- Integracion de Leaflet JS en detalle de tienda para representar ubicacion real desde `Store.location`.
	- Estandarizacion de visualizacion de imagenes en Stores/Products/Employees con fallback consistente ante carga fallida.
	- Refuerzo de navegacion y enlaces con `url_for` en elementos principales para evitar rutas fragiles.
	- Dashboard actualizado con acceso directo a Employees desde boton de accion.
	- Smoke tests ampliados para verificar enlaces primarios y presencia del contenedor de mapa en detalle de tienda.
- Trazabilidad de requisitos:
	- FR-012: mapa de geolocalizacion integrado en detalle de Store mediante Leaflet.
	- FR-030/FR-031: visualizacion de employees mantenida con rutas funcionales de listado y detalle.
	- FR-042: visualizacion basada en mapa en interfaz operativa de tienda.

### EN
- Status: Implementation completed and closed for UI hardening (map, images, and navigation).
- Validation result:
	- Test suite executed successfully: 103 passed.
- Implemented scope in this iteration:
	- Leaflet JS integrated into Store detail view to render real location from `Store.location`.
	- Image rendering standardized across Stores/Products/Employees with consistent fallback on load failures.
	- Navigation/link reliability improved by replacing fragile hardcoded paths with `url_for` in key UI elements.
	- Dashboard updated with direct Employees access button.
	- Smoke tests expanded to validate primary links and Store detail map container rendering.
- Requirement traceability:
	- FR-012: geolocation map integrated into Store detail via Leaflet.
	- FR-030/FR-031: Employee listing/detail routes remain functional in UI.
	- FR-042: map-driven Store location representation available in operational UI.

## 19. Implementation progress (Store detail normalization)

### ES
- Estado: Implementacion completada para normalizacion de datos visibles en detalle de tienda.
- Alcance implementado:
	- El ID de tienda se muestra simplificado (segmento final del URN, por ejemplo `S001`).
	- El pais se muestra por nombre completo en UI (mapeo de `countryCode` para ES/DE/FR).
	- La direccion completa se muestra en ficha con `streetAddress`, `addressLocality` y `addressRegion`.
	- Se elimina el campo `Tipo` en detalle de tienda por redundancia funcional.
- Trazabilidad de requisitos:
	- FR-010: la presentacion de atributos de Store en detalle mejora legibilidad y semantica.
	- FR-050: el nombre de pais queda integrado en flujo bilingue de etiquetas.

### EN
- Status: Completed implementation for visible-data normalization on Store detail.
- Implemented scope:
	- Store ID is rendered in simplified format (URN trailing segment, e.g. `S001`).
	- Country is rendered as full name in UI (`countryCode` mapping for ES/DE/FR).
	- Full address is shown using `streetAddress`, `addressLocality`, and `addressRegion`.
	- `Type` field was removed from Store detail due to functional redundancy.
- Requirement traceability:
	- FR-010: Store detail attribute rendering is clearer and more semantic.
	- FR-050: country-name rendering is integrated with bilingual label flow.
