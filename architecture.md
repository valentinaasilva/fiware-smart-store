# Architecture - fiware-smart-store

## 1. Document control

### ES
- Version: 1.0
- Fecha: 2026-03-28
- Estado: Baseline tecnico
- Alcance: Arquitectura objetivo para implementacion Flask + FIWARE

### EN
- Version: 1.0
- Date: 2026-03-28
- Status: Technical baseline
- Scope: Target architecture for Flask + FIWARE implementation

## 1.1 Change log

### ES
- 2026-03-29: Actualizada arquitectura de presentacion con shell de dos niveles (sidebar + cabecera superior) y dashboard enriquecido con mapa agregado de tiendas y KPI de bajo stock.
- 2026-03-29: Se incorporan busqueda de productos por query, selector de tema dark/light/system y formularios CRUD en listados para Store/Product/Employee.

### EN
- 2026-03-29: Presentation architecture updated with a two-level shell (sidebar + top header) and an enriched dashboard with aggregated stores map and low-stock KPI.
- 2026-03-29: Added query-based product search, dark/light/system theme selector, and list-view CRUD forms for Store/Product/Employee.

## 2. Architectural goals

### ES
1. Separar claramente capas de presentacion, aplicacion e integracion.
2. Minimizar acoplamiento entre UI y backend mediante API estable.
3. Priorizar Orion NGSIv2 como verdad principal de negocio.
4. Garantizar continuidad operativa con fallback SQLite.
5. Propagar eventos de negocio en tiempo real usando SocketIO.

### EN
1. Clearly separate presentation, application, and integration layers.
2. Minimize coupling between UI and backend through a stable API.
3. Prioritize Orion NGSIv2 as business source of truth.
4. Ensure operational continuity with SQLite fallback.
5. Propagate business events in real time through SocketIO.

## 3. System context

### ES
El sistema opera como una app Flask conectada a Orion Context Broker y MongoDB en Docker. Tambien consume providers externos del contenedor tutorial para enriquecer Stores con temperature, relativeHumidity y tweets.

Actores externos:
- Navegador web del operador/supervisor.
- Orion Context Broker (API NGSIv2).
- MongoDB (persistencia de Orion).
- Tutorial Context Provider.

### EN
The system runs as a Flask app connected to Orion Context Broker and MongoDB in Docker. It also consumes external providers from the tutorial container to enrich Stores with temperature, relativeHumidity, and tweets.

External actors:
- Operator/supervisor web browser.
- Orion Context Broker (NGSIv2 API).
- MongoDB (Orion persistence).
- Tutorial Context Provider.

## 4. Logical architecture

### ES
Capas y componentes:
1. Presentation layer
- Plantillas Jinja2 para vistas y formularios.
- Assets estaticos CSS/JS.
- Socket.IO client para actualizaciones real-time.
- Librerias visuales Leaflet, Three.js, Mermaid y Font Awesome.
- Shell UI desacoplado en `templates/base.html` con sidebar fijo, support strip y top header de controles.
- Header con formulario de busqueda global (`GET /products?q=...`) y selector de tema de tres modos.

2. Application layer
- app.py como punto de entrada Flask y configuracion SocketIO.
- Blueprints por dominio:
  - routes/stores.py
  - routes/products.py
  - routes/employees.py
  - routes/inventory.py
  - routes/notifications.py
- Servicio de i18n para ES/EN.
- Servicio de tema para dark/light mode.

3. Data access layer
- Adapter OrionClient (NGSIv2 CRUD y subscriptions).
- Adapter SQLiteRepository (fallback local).
- DataSourceSelector (estrategia Orion first + fallback).

4. Integration layer
- Client HTTP hacia Orion /v2/entities, /v2/subscriptions, /v2/registrations.
- Endpoint webhook para notificaciones Orion -> Flask.
- Emision de eventos SocketIO hacia clientes conectados.

### EN
Layers and components:
1. Presentation layer
- Jinja2 templates for views and forms.
- Static CSS/JS assets.
- Socket.IO client for real-time updates.
- Visual libraries Leaflet, Three.js, Mermaid, and Font Awesome.
- Decoupled UI shell in `templates/base.html` with fixed sidebar, support strip, and control-oriented top header.
- Header with global search form (`GET /products?q=...`) and three-mode theme selector.

2. Application layer
- app.py as Flask entrypoint and SocketIO bootstrap.
- Domain blueprints:
  - routes/stores.py
  - routes/products.py
  - routes/employees.py
  - routes/inventory.py
  - routes/notifications.py
- i18n service for ES/EN.
- Theme service for dark/light mode.

3. Data access layer
- OrionClient adapter (NGSIv2 CRUD and subscriptions).
- SQLiteRepository adapter (local fallback).
- DataSourceSelector (Orion-first + fallback strategy).

4. Integration layer
- HTTP client to Orion /v2/entities, /v2/subscriptions, /v2/registrations.
- Webhook endpoint for Orion -> Flask notifications.
- SocketIO event emission to connected clients.

## 5. Deployment architecture

### ES
Topologia de desarrollo local:
- Contenedor Orion CB (puerto 1026).
- Contenedor MongoDB (puerto 27017 interno).
- Contenedor tutorial/provider (segun compose).
- Servicio Flask ejecutado en host o contenedor app.

Regla de conectividad clave:
- Las subscriptions de Orion deben usar callback hacia host.docker.internal, no localhost.

### EN
Local development topology:
- Orion CB container (port 1026).
- MongoDB container (internal port 27017).
- Tutorial/provider container (as defined in compose).
- Flask service running on host or app container.

Critical connectivity rule:
- Orion subscriptions must use callback URL with host.docker.internal, not localhost.

## 6. Startup sequence

### ES
1. Cargar configuracion (.env) y levantar Flask + SocketIO.
2. Ejecutar health-check Orion.
3. Seleccionar fuente activa:
- Orion disponible -> modo ORION
- Orion no disponible -> modo SQLITE
4. Si modo ORION:
- Registrar context providers externos (temperature, relativeHumidity, tweets).
- Crear/validar subscriptions:
  - Price change on Product
  - Low stock on InventoryItem por Store
5. Inicializar cache ligera para catalogos (stores, products, shelves) si aplica.
6. Exponer endpoints web y API interna para formularios dinamicos.

### EN
1. Load configuration (.env) and start Flask + SocketIO.
2. Execute Orion health-check.
3. Select active source:
- Orion reachable -> ORION mode
- Orion unreachable -> SQLITE mode
4. If ORION mode:
- Register external context providers (temperature, relativeHumidity, tweets).
- Create/validate subscriptions:
  - Price change on Product
  - Low stock on InventoryItem per Store
5. Initialize lightweight cache for catalogs (stores, products, shelves) if applicable.
6. Expose web endpoints and internal API for dynamic forms.

## 7. Runtime data flows

### ES

#### 7.1 CRUD flow (normal)
1. Usuario interactua con formulario en UI.
2. Blueprint valida payload y aplica reglas de dominio.
3. DataSourceSelector enruta a OrionClient o SQLiteRepository.
4. Persistencia en origen activo.
5. Respuesta a UI y refresco de atributos visibles.

#### 7.4 Dashboard map flow
1. `app.py` agrega datos de ubicacion validos de Store en `stores_map` para el dashboard.
2. `templates/dashboard.html` serializa los marcadores en atributo de datos del contenedor Leaflet.
3. `static/js/app.js` inicializa mapa agregado y ajusta bounds para mostrar todas las tiendas.

#### 7.2 Price-change event flow
1. Cambio de price en Product ocurre via CRUD.
2. Orion detecta condicion de subscription y emite notificacion HTTP.
3. routes/notifications.py recibe evento y lo normaliza.
4. SocketIO emite evento product_price_changed.
5. JS cliente actualiza atributo de precio en vistas activas (sin regenerar HTML).

#### 7.3 Low-stock event flow
1. stockCount/shelfCount desciende por debajo de umbral definido.
2. Orion emite notificacion low_stock.
3. Backend registra evento y lo publica por SocketIO.
4. UI Store detail actualiza panel de alertas en tiempo real.

### EN

#### 7.1 CRUD flow (normal)
1. User interacts with UI form.
2. Blueprint validates payload and applies domain rules.
3. DataSourceSelector routes to OrionClient or SQLiteRepository.
4. Persistence in active source.
5. Response to UI and refresh of visible attributes.

#### 7.4 Dashboard map flow
1. `app.py` aggregates valid Store coordinates into `stores_map` for dashboard rendering.
2. `templates/dashboard.html` serializes markers into a Leaflet container data attribute.
3. `static/js/app.js` initializes the aggregate map and fits bounds to show all stores.

#### 7.2 Price-change event flow
1. Product price change occurs through CRUD.
2. Orion matches subscription condition and sends HTTP notification.
3. routes/notifications.py receives and normalizes the event.
4. SocketIO emits product_price_changed event.
5. Client JS updates price attribute in active views (no HTML regeneration).

#### 7.3 Low-stock event flow
1. stockCount/shelfCount drops below configured threshold.
2. Orion emits low_stock notification.
3. Backend stores event and publishes via SocketIO.
4. Store detail UI updates alerts panel in real time.

## 8. Module decomposition

### ES
- app.py
  - Inicializa Flask, SocketIO, registro de blueprints y startup hooks.

- routes/stores.py
  - Listado, detalle, alta, edicion y borrado de Store.
  - Formularios de alta/edicion/borrado desde vista de listado (`/stores/new`, `/stores/edit/<id>`, `/stores/delete/<id>`).
  - CRUD de Shelf e InventoryItem asociados.

- routes/products.py
  - CRUD Product.
  - Filtro de busqueda por query en listado (`q` por id/nombre/categoria/origen).
  - Formularios de alta/edicion/borrado desde vista de listado (`/products/new`, `/products/edit/<id>`, `/products/delete/<id>`).
  - Vista detalle product con agregacion de inventario por tienda/estanteria.

- routes/employees.py
  - CRUD Employee con validaciones de email, salary, contract date.
  - Formularios de alta/edicion/borrado desde vista de listado (`/employees/new`, `/employees/edit/<id>`, `/employees/delete/<id>`).

- routes/inventory.py
  - Operaciones transversales de InventoryItem.
  - Endpoint para carga dinamica de shelves por store.

- routes/notifications.py
  - Webhook de Orion subscriptions.
  - Historial en memoria o persistencia ligera de eventos para Store detail.

- models/database.py
  - Modelos SQLAlchemy para fallback SQLite.

- models/orion_client.py
  - Cliente NGSIv2 (entities, subscriptions, registrations).
  - Normalizacion payload NGSIv2 <-> DTO internos.

### EN
- app.py
  - Initializes Flask, SocketIO, blueprint registration, startup hooks.

- routes/stores.py
  - Store list/detail/create/update/delete.
  - List-page create/edit/delete form endpoints (`/stores/new`, `/stores/edit/<id>`, `/stores/delete/<id>`).
  - CRUD for related Shelf and InventoryItem.

- routes/products.py
  - Product CRUD.
  - Query-based search filtering on list endpoint (`q` by id/name/category/origin).
  - List-page create/edit/delete form endpoints (`/products/new`, `/products/edit/<id>`, `/products/delete/<id>`).
  - Product detail with inventory aggregation by store/shelf.

- routes/employees.py
  - Employee CRUD with validation for email, salary, contract date.
  - List-page create/edit/delete form endpoints (`/employees/new`, `/employees/edit/<id>`, `/employees/delete/<id>`).

- routes/inventory.py
  - Cross-entity InventoryItem operations.
  - Endpoint for dynamic shelf loading by store.

- routes/notifications.py
  - Orion subscription webhook.
  - In-memory or lightweight event persistence for Store detail.

- models/database.py
  - SQLAlchemy models for SQLite fallback.

- models/orion_client.py
  - NGSIv2 client (entities, subscriptions, registrations).
  - NGSIv2 payload normalization <-> internal DTOs.

## 9. API design principles

### ES
- API interna REST orientada a recursos por entidad.
- DTO de entrada y salida con convencion estable y validacion server-side.
- Manejo de errores explicito con codigos HTTP coherentes:
  - 200/201 operaciones exitosas
  - 400 validacion
  - 404 recurso no encontrado
  - 409 conflicto de integridad
  - 502 errores de Orion no recuperables en modo ORION
- Tiempos de timeout y retry para llamadas a Orion configurables por entorno.

### EN
- Internal REST API resource-oriented by entity.
- Stable input/output DTOs with server-side validation.
- Explicit error handling with coherent HTTP codes:
  - 200/201 success
  - 400 validation
  - 404 not found
  - 409 integrity conflict
  - 502 non-recoverable Orion errors in ORION mode
- Configurable timeout and retry for Orion calls per environment.

## 10. Security and compliance baseline

### ES
- Password en Employee debe almacenarse como hash fuerte (ejemplo: bcrypt).
- Validacion de entrada para prevenir inyeccion y payloads inconsistentes.
- Escapado de salida en plantillas para prevenir XSS reflejado.
- Secretos en variables de entorno, no hardcode.
- Limitar CORS a origenes esperados en desarrollo.

### EN
- Employee password must be stored as strong hash (example: bcrypt).
- Input validation to prevent injection and inconsistent payloads.
- Output escaping in templates to prevent reflected XSS.
- Secrets in environment variables, no hardcoding.
- Restrict CORS to expected origins in development.

## 11. Observability and operations

### ES
- Logging estructurado por modulo (app, routes, orion, socketio).
- Correlation id por request para trazabilidad.
- Eventos criticos a log:
  - cambio de fuente ORION/SQLITE
  - alta/baja de subscriptions
  - error de callback realtime
- Comandos operativos:
  - start.sh para reiniciar entorno y app
  - stop.sh para apagar contenedores

### EN
- Structured logging by module (app, routes, orion, socketio).
- Correlation id per request for traceability.
- Critical events to log:
  - ORION/SQLITE source switch
  - subscription registration/removal
  - realtime callback errors
- Operational commands:
  - start.sh to restart environment and app
  - stop.sh to stop containers

## 12. Testing architecture

### ES
Niveles de test:
1. Unit tests
- Validaciones de modelos y mapeos NGSIv2.
- Reglas de dominio (stock, capacity, formatos).

2. Integration tests
- CRUD por entidad en endpoints Flask.
- Flujos de fallback Orion->SQLite.
- Recepcion de webhooks Orion y emision SocketIO.

3. UI smoke tests
- Navegacion basica por secciones.
- Toggle idioma y tema.
- Render de mapa y dashboard.

### EN
Test levels:
1. Unit tests
- Model validations and NGSIv2 mappings.
- Domain rules (stock, capacity, formats).

2. Integration tests
- CRUD per entity on Flask endpoints.
- Orion->SQLite fallback flows.
- Orion webhook intake and SocketIO emission.

3. UI smoke tests
- Basic section navigation.
- Language and theme toggle.
- Map and dashboard rendering.

## 13. Architecture decision records (summary)

### ES
- ADR-001: Orion-first con SQLite fallback para resiliencia en entorno academico.
- ADR-002: Blueprints por dominio para escalabilidad de mantenimiento.
- ADR-003: CSS-first y restriccion de no generar HTML desde JS.
- ADR-004: Real-time con SocketIO para minimizar refresh manual.
- ADR-005: host.docker.internal obligatorio en callbacks de subscriptions Orion.

### EN
- ADR-001: Orion-first with SQLite fallback for resilience in academic environment.
- ADR-002: Domain-based blueprints for maintainability scaling.
- ADR-003: CSS-first and no-HTML-generation rule from JS.
- ADR-004: Real-time via SocketIO to minimize manual refresh.
- ADR-005: host.docker.internal mandatory for Orion subscription callbacks.

## 14. Open questions

### ES
1. Se requiere cache distribuida o basta cache local en memoria?
2. Los eventos de notificacion deben persistirse mas alla de una sesion de servidor?
3. El modo SQLite debe soportar todas las consultas agregadas del dashboard o solo subset?

### EN
1. Is distributed caching needed, or is local in-memory cache enough?
2. Should notification events persist beyond one server session?
3. Must SQLite mode support full dashboard aggregations or only a subset?

## 15. Implementation progress (Issue #1)

### ES
- Implementado en iteracion 1:
  - `app.py` con app factory, inicializacion SocketIO y registro de blueprints.
  - `models/data_source.py` con DataSourceSelector y bootstrap Orion/SQLite.
  - `models/orion_client.py` con operaciones NGSIv2 base y registro de providers/subscriptions.
  - `models/database.py` con repositorio SQLite generico para entidades JSON.
  - Blueprints CRUD iniciales en `routes/` y webhook realtime en `routes/notifications.py`.
  - Plantillas server-rendered base y estilos iniciales.
- Implementado especificamente para cierre de Issue #1:
  - Script de carga de datos `scripts/load_test_data.py` integrado al flujo de desarrollo local.
  - Inicializacion de dataset funcional para cadena de supermercados (4 stores, 10 products, 8 employees, 12 shelves, 55+ inventory items).
  - IDs de empleados en semilla reindexados de forma correlativa (`E001..E008`) para consistencia operativa y pruebas.
  - Suites de pruebas para validacion estructural de entidades y reglas de integridad.
  - Correccion posterior: el script ahora permite target `sqlite` por defecto para carga local efectiva del dashboard.
  - Correccion de navegacion: barra superior usa rutas estables y blueprints de listado aceptan URL con y sin slash final.
- Desviaciones temporales respecto a arquitectura objetivo:
  - Persistencia fallback implementada con `sqlite3` generico en vez de SQLAlchemy tipado.
  - Validacion de dominio en capa inicial minima; se ampliara por entidad.
- Estado de la arquitectura para este issue:
  - Completado y estable para alcance base de plataforma y carga de datos de prueba.
- Decision vigente:
  - Mantener interfaz comun de repositorio para poder migrar la implementacion SQLite sin romper rutas.

### EN
- Implemented in iteration 1:
  - `app.py` with app factory, SocketIO initialization, and blueprint registration.
  - `models/data_source.py` with DataSourceSelector and Orion/SQLite bootstrap.
  - `models/orion_client.py` with baseline NGSIv2 operations and provider/subscription registration.
  - `models/database.py` with generic SQLite JSON-entity repository.
  - Initial CRUD blueprints in `routes/` and realtime webhook in `routes/notifications.py`.
  - Base server-rendered templates and initial styling.
- Implemented specifically to close Issue #1:
  - Test data loading script `scripts/load_test_data.py` integrated into local development workflow.
  - Functional supermarket bootstrap dataset (4 stores, 10 products, 8 employees, 12 shelves, 55+ inventory items).
  - Seed employee IDs were reindexed to a contiguous range (`E001..E008`) for operational and test consistency.
  - Test suites for entity-structure validation and integrity rule checks.
  - Post-fix: the script now supports `sqlite` as default target to ensure effective local dashboard seeding.
  - Navigation fix: topbar uses stable route links and list blueprints accept URLs both with and without trailing slash.
- Temporary deviations from target architecture:
  - Fallback persistence currently implemented with generic `sqlite3` instead of typed SQLAlchemy models.
  - Domain validation currently minimal and to be expanded per entity.
- Stability fix applied:
  - Default SQLite location switched to `instance/fiware.db` and repository path normalization added to avoid collisions with existing file paths such as `services`.
- Architecture status for this issue:
  - Completed and stable for baseline platform scope and test-data provisioning.
- Current decision:
  - Keep a common repository interface to allow SQLite implementation migration without route changes.

## 16. Implementation progress (Issue #2)

### ES
- Implementado en iteracion inicial de i18n:
  - Modulo de traducciones lightweight en `models/i18n.py`.
  - Seleccion de locale en `before_request` y persistencia en `session`.
  - Context processor para inyeccion de helper `_()` y `current_lang` en plantillas.
  - Endpoint `/language/<lang>` para cambiar idioma y redirigir a la ruta actual.
  - Toggle ES/EN en navbar y traduccion de vistas principales.
- Impacto arquitectonico:
  - No se altera la capa de datos ni contratos NGSIv2.
  - i18n se mantiene en capa de presentacion y contexto de peticion.

### EN
- Implemented in initial i18n iteration:
  - Lightweight translation module in `models/i18n.py`.
  - Locale selection in `before_request` with session persistence.
  - Context processor injecting `_()` helper and `current_lang` in templates.
  - `/language/<lang>` endpoint to switch language and redirect to current route.
  - ES/EN toggle in navbar and translation of main views.
- Architectural impact:
  - No changes to data layer or NGSIv2 contracts.
  - i18n remains in presentation layer and request context.

## 17. Implementation progress (Issue #3)

### ES
- Estado: Bateria de pruebas ampliada y estable para la arquitectura actual.
- Cambios aplicados:
  - Estructura de tests separada por capas (`tests/unit`, `tests/integration`) para mantener coherencia con la arquitectura logica.
  - Cobertura unitaria dedicada para `OrionClient` (health-check, CRUD y registro de integrations NGSIv2).
  - Fixtures compartidas en `tests/conftest.py` para aislar SQLite temporal y forzar escenarios Orion no disponible.
  - Pruebas de integracion para blueprints CRUD y webhooks de notificaciones.
  - Pruebas `tests/e2e` para flujo operativo completo y resiliencia ante caida de Orion con fallback a SQLite.
  - Correccion de compatibilidad en rutas de inventario para aceptar URL con y sin slash final, evitando redirecciones 308 en clientes API.
- Verificacion:
  - Ejecucion de suite completa con 87 tests en verde.

### EN
- Status: Expanded test battery is stable for the current architecture.
- Applied changes:
  - Layered test structure (`tests/unit`, `tests/integration`) aligned with logical architecture boundaries.
  - Dedicated unit coverage for `OrionClient` (health-check, CRUD, and NGSIv2 integration registration).
  - Shared fixtures in `tests/conftest.py` to isolate temporary SQLite and force Orion-unavailable scenarios.
  - Integration tests for CRUD blueprints and notification webhooks.
  - `tests/e2e` coverage for full operational flow and resilience when Orion fails and SQLite fallback takes over.
  - Inventory route compatibility fix to accept both trailing-slash and non-trailing-slash URLs, preventing 308 redirects for API clients.
- Verification:
  - Full suite execution with 87 passing tests.

## 18. Implementation progress (Issue #4)

### ES
- Estado: Iteracion de refuerzo de contrato NGSIv2 completada y cerrada en Store/Product.
- Cambios aplicados:
  - `routes/utils.py` centraliza normalizacion NGSIv2, denormalizacion para vistas HTML y validaciones de dominio para Store/Product.
  - `routes/stores.py` y `routes/products.py` aplican normalizacion/validacion en create/update y mantienen respuestas JSON para consumidores API.
  - Vistas de `stores` y `products` muestran `image`; vistas de productos muestran adicionalmente `originCountry`.
  - Navegacion principal en `templates/base.html` queda enfocada en dashboard, stores y products.
  - Etiqueta de entrada principal ajustada a `Dashboard` (EN) y `Panel` (ES) para consistencia de UX.
  - `static/css/main.css` se rediseña como sistema visual de panel administrativo (tokens, jerarquia tipografica, tablas/cards, responsive).
  - Datos semilla de imagenes en `scripts/load_test_data.py` migran a URLs fijas curadas para coherencia por entidad, incluyendo mapeo final de Stores a URLs especificas con nomenclatura Xantadis (Norte/Sur/Este/Oeste) y ajuste explicito de productos clave (manzana roja, leche).
  - Fixtures y pruebas de integracion/unit se actualizan para cubrir el nuevo contrato.
- Verificacion:
  - Ejecucion de suite completa con 95 tests en verde.

### EN
- Status: NGSIv2 contract-hardening iteration completed and closed for Store/Product.
- Applied changes:
  - `routes/utils.py` now centralizes NGSIv2 normalization, HTML-view denormalization, and Store/Product domain validations.
  - `routes/stores.py` and `routes/products.py` apply normalization/validation on create/update while preserving JSON API responses.
  - `stores` and `products` views now expose `image`; product views additionally expose `originCountry`.
  - Main navigation in `templates/base.html` is focused on dashboard, stores, and products.
  - Primary entry label was refined to `Dashboard` (EN) and `Panel` (ES) for UX consistency.
  - `static/css/main.css` was redesigned as an admin-panel visual system (tokens, typography hierarchy, improved tables/cards, responsive behavior).
  - Seed image data in `scripts/load_test_data.py` now uses curated fixed URLs for entity-level semantic coherence, including final Store URL mapping with Xantadis naming (North/South/East/West) and explicit key-product adjustments (red apple, milk).
  - Fixtures and integration/unit tests were updated to cover the new contract.
- Verification:
  - Full suite execution with 95 passing tests.

## 19. Implementation progress (Issue #5)

### ES
- Estado: Implementacion completada y cerrada para normalizacion/validacion Employee en flujo CRUD.
- Cambios aplicados:
  - `routes/utils.py` incorpora mapeo NGSIv2 de Employee y validacion de atributos obligatorios (`name`, `image`, `salary`, `role`, `refStore`).
  - `routes/employees.py` aplica normalizacion y validacion tambien en `update` (partial=True) para mantener consistencia de contrato.
  - `templates/employees/list.html` y `templates/employees/detail.html` se alinean con atributos obligatorios y mantienen visualizacion de campos opcionales.
  - `scripts/load_test_data.py` incorpora `image` en employees semilla y mantiene salida NGSIv2 tipada para salary/role/refStore.
  - `tests/conftest.py`, `tests/unit/test_utils.py` y `tests/integration/test_routes_crud.py` se actualizan para cubrir reglas de validacion y casos invalidos de Employee.
- Verificacion:
  - Ejecucion de suite completa con 101 tests en verde.

### EN
- Status: Implementation completed and closed for Employee normalization/validation in CRUD flow.
- Applied changes:
  - `routes/utils.py` now includes Employee NGSIv2 mapping and required-attribute validation (`name`, `image`, `salary`, `role`, `refStore`).
  - `routes/employees.py` now applies normalization/validation on `update` as well (`partial=True`) to keep contract consistency.
  - `templates/employees/list.html` and `templates/employees/detail.html` were aligned with required attributes while preserving optional fields.
  - `scripts/load_test_data.py` now includes Employee `image` in seed data and preserves typed NGSIv2 output for salary/role/refStore.
  - `tests/conftest.py`, `tests/unit/test_utils.py`, and `tests/integration/test_routes_crud.py` were updated to cover Employee validation rules and invalid cases.
- Verification:
  - Full suite execution with 101 passing tests.

## 20. Implementation progress (Issue #6)

### ES
- Estado: Implementacion completada y cerrada para mejoras estructurales de UI.
- Cambios aplicados:
  - `templates/base.html` incorpora assets Leaflet y refuerza enlaces de navegacion principal con `url_for`.
  - `templates/stores/detail.html` incorpora bloque de mapa interactivo con coordenadas de `Store.location`.
  - `static/js/app.js` implementa inicializacion condicionada de Leaflet, validacion de coordenadas y marcador con popup.
  - `static/css/main.css` incorpora estilos de mapa y utilidades de fallback visual (`media-frame`, `is-hidden`).
  - Templates de Stores/Products/Employees estandarizan comportamiento de imagen ante error de carga.
  - `tests/test_smoke.py` amplifica cobertura de integridad de enlaces y render del contenedor de mapa.
- Verificacion:
  - Ejecucion de suite completa con 103 tests en verde.

### EN
- Status: Implementation completed and closed for structural UI improvements.
- Applied changes:
  - `templates/base.html` now includes Leaflet assets and strengthens main navigation links with `url_for`.
  - `templates/stores/detail.html` now includes an interactive map block powered by `Store.location` coordinates.
  - `static/js/app.js` now initializes Leaflet conditionally, validates coordinates, and renders a marker popup.
  - `static/css/main.css` now includes map styling and visual fallback utilities (`media-frame`, `is-hidden`).
  - Store/Product/Employee templates now share consistent image error/fallback behavior.
  - `tests/test_smoke.py` now extends link integrity and Store detail map-container checks.
- Verification:
  - Full suite execution with 103 passing tests.

## 21. Implementation progress (Store detail normalization)

### ES
- Estado: Implementacion completada para ajuste de representacion semantica en capa de presentacion.
- Cambios arquitectonicos aplicados:
  - La simplificacion de identificador (`urn:...` -> segmento final) se resuelve en template Jinja sin modificar contrato de datos.
  - El mapeo de `countryCode` a nombre visible de pais se mantiene en capa de presentacion con soporte i18n.
  - La direccion postal completa se consolida en la ficha de detalle usando atributos existentes del modelo `address`.
  - Se elimina el campo `type` de la vista detalle para reducir ruido de interfaz sin alterar API.
- Trazabilidad tecnica:
  - Capa afectada: Presentation (`templates/stores/detail.html`, `models/i18n.py`).
  - Capas no afectadas: Application, Data access e Integration.

### EN
- Status: Completed implementation for semantic rendering adjustments in the presentation layer.
- Applied architectural changes:
  - Identifier simplification (`urn:...` -> trailing segment) is handled in Jinja template logic without changing data contracts.
  - `countryCode` to country-name mapping remains presentation-layer logic with i18n support.
  - Full postal address is consolidated in Store detail using existing `address` model attributes.
  - `type` field was removed from detail view to reduce UI noise without API changes.
- Technical traceability:
  - Affected layer: Presentation (`templates/stores/detail.html`, `models/i18n.py`).
  - Unaffected layers: Application, Data access, and Integration.

## 22. Implementation progress (Global entity-format normalization)

### ES
- Estado: Implementacion completada para normalizacion transversal de formato en capa de presentacion.
- Cambios arquitectonicos aplicados:
  - Simplificacion de URN (`id`, `refStore`) centralizada en logica de templates para vistas de Stores/Products/Employees.
  - Mapeo de codigos de pais a nombre visible integrado en templates con soporte i18n (`ES`, `DE`, `FR`, `EC`).
  - Eliminacion del campo `type` en vistas detalle para reducir ruido de interfaz sin cambiar contratos de API.
  - Pruebas smoke ampliadas para verificar consistencia de render entre listados y detalles.
- Trazabilidad tecnica:
  - Capa afectada: Presentation (`templates/stores/*`, `templates/products/*`, `templates/employees/*`, `models/i18n.py`, `tests/test_smoke.py`).
  - Capas no afectadas: Application, Data access, Integration.

### EN
- Status: Completed implementation for cross-view formatting normalization in the presentation layer.
- Applied architectural changes:
  - URN simplification (`id`, `refStore`) is handled in template logic across Stores/Products/Employees views.
  - Country-code to full-name mapping is integrated in templates with i18n support (`ES`, `DE`, `FR`, `EC`).
  - `type` field was removed from detail views to reduce UI noise without API contract changes.
  - Smoke tests were extended to verify rendering consistency across list and detail pages.
- Technical traceability:
  - Affected layer: Presentation (`templates/stores/*`, `templates/products/*`, `templates/employees/*`, `models/i18n.py`, `tests/test_smoke.py`).
  - Unaffected layers: Application, Data access, Integration.

## 23. Implementation progress (Issue #7 CRUD in detail views)

### ES
- Estado: Implementacion completada para CRUD contextual en detalles de Store/Product.
- Cambios arquitectonicos aplicados:
  - Se adoptan endpoints anidados por contexto para operaciones en detalle:
    - `stores/<id>/shelves`, `stores/<id>/inventory`
    - `products/<id>/inventory`
  - Se incorporan validaciones de dominio para `Shelf` e `InventoryItem` en capa de rutas/utilidades.
  - Se agrega logica de integridad cruzada:
    - coherencia `refShelf` con `refStore`.
    - no duplicados por tripleta (`refStore`, `refShelf`, `refProduct`).
    - bloqueo de borrado de shelf con dependencias (409).
  - Las vistas server-rendered de detalle incorporan formularios CRUD y tablas operativas.
  - La capa de acceso a datos agrega consulta filtrada por atributo para resolver contextos sin romper fallback Orion/SQLite.
- Trazabilidad tecnica:
  - Capa afectada: Presentation, Application y Data access.
  - Archivos clave: `routes/stores.py`, `routes/products.py`, `routes/inventory.py`, `routes/utils.py`, `models/data_source.py`, `templates/stores/detail.html`, `templates/products/detail.html`.

### EN
- Status: Implementation completed for context-scoped CRUD in Store/Product detail views.
- Applied architectural changes:
  - Context-nested endpoints were adopted for detail operations:
    - `stores/<id>/shelves`, `stores/<id>/inventory`
    - `products/<id>/inventory`
  - Domain validations for `Shelf` and `InventoryItem` were added in route/utils layer.
  - Cross-entity integrity rules were introduced:
    - `refShelf` and `refStore` consistency.
    - duplicate prevention for (`refStore`, `refShelf`, `refProduct`) tuples.
    - shelf delete blocking when dependencies exist (409).
  - Server-rendered detail views now include operational CRUD forms/tables.
  - Data-access layer now supports attribute-filtered queries to build contextual views while preserving Orion/SQLite fallback behavior.
- Technical traceability:
  - Affected layers: Presentation, Application, and Data access.
  - Key files: `routes/stores.py`, `routes/products.py`, `routes/inventory.py`, `routes/utils.py`, `models/data_source.py`, `templates/stores/detail.html`, `templates/products/detail.html`.

## 24. Closure status (Issue #7)

### ES
- Estado de despliegue en ramas:
  - `main` y `feature/issue-7-crud` convergen en el mismo commit funcional de Issue #7.
  - Sin cambios pendientes tras flujo de merge/sync.
- Estado tecnico:
  - Arquitectura objetivo para CRUD contextual (Store/Product detail) consolidada en `main`.
  - Contratos de errores y reglas de integridad operativos en capas Application/Data access/Presentation.
- Estado de ticket:
  - No se detecta `issues/7` por API publica al momento de cierre tecnico.

### EN
- Branch deployment status:
  - `main` and `feature/issue-7-crud` converge on the same functional Issue #7 commit.
  - No pending changes after merge/sync flow.
- Technical status:
  - Target architecture for context-scoped CRUD (Store/Product detail) is consolidated on `main`.
  - Error contracts and integrity rules are operational across Application/Data access/Presentation layers.
- Ticket status:
  - `issues/7` is not detected via public API at technical closure time.

## 25. Implementation progress (Issue #8 Orion-first operational bootstrap)

### ES
- Estado: Implementacion completada y cerrada para robustecer arquitectura de arranque Orion-first con fallback SQLite sin sincronizacion.
- Cambios arquitectonicos aplicados:
  - `DataSourceSelector.bootstrap()` consolida decision de fuente activa en arranque y registra logs operativos del modo seleccionado.
  - Se mantiene fallback a SQLite ante error de operaciones Orion para continuidad, sin replicacion de datos entre fuentes.
  - `docker-compose.yml` se ajusta al stack del tutorial CRUD Operations con defaults que evitan dependencias de variables no definidas.
  - Scripts de operacion:
    - `start.sh`: detiene stack previo, levanta contenedores, espera salud de Orion y arranca Flask.
    - `stop.sh`: detiene app local y contenedores del stack.
- Trazabilidad tecnica:
  - Capas afectadas: Data access, Integration y operacion local de despliegue.
  - Archivos clave: `models/data_source.py`, `docker-compose.yml`, `start.sh`, `stop.sh`.

### EN
- Status: Implementation completed and closed to harden Orion-first startup architecture with SQLite fallback and no synchronization.
- Applied architectural changes:
  - `DataSourceSelector.bootstrap()` now centralizes startup source decision with explicit operational mode logging.
  - SQLite fallback on Orion operation failures is kept for continuity, without any cross-source data replication.
  - `docker-compose.yml` is aligned to the CRUD Operations tutorial stack with defaults that avoid undefined-variable dependencies.
  - Operational scripts:
    - `start.sh`: stops previous stack, starts containers, waits for Orion health, then starts Flask.
    - `stop.sh`: stops local app process and stack containers.
- Technical traceability:
  - Affected layers: Data access, Integration, and local deployment operations.
  - Key files: `models/data_source.py`, `docker-compose.yml`, `start.sh`, `stop.sh`.

## 26. Closure status (Issue #8)

### ES
- Estado de fusion: cambios de Issue #8 consolidados en `main`.
- Estado de sincronizacion: rama de trabajo y remoto `origin/main` sin diferencias pendientes.
- Estado tecnico: flujo Orion-first en bootstrap, fallback controlado a SQLite y ciclo operativo con scripts start/stop consolidado.
- Estado de ticket: cierre trazado por commit en `main` con referencia de cierre de issue.

### EN
- Merge status: Issue #8 changes consolidated on `main`.
- Sync status: working branch and `origin/main` are aligned with no pending diffs.
- Technical status: Orion-first bootstrap flow, controlled SQLite fallback, and start/stop operational lifecycle consolidated.
- Ticket status: closure traced by a `main` commit with issue-closing reference.
