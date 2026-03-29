# Issue #9: Ampliación del Modelo de Datos & UML con Mermaid

## Objetivo
Ampliar el modelo de datos de `Employee`, `Store` y `Product` con atributos faltantes, representar el modelo completo con un diagrama UML usando Mermaid en el dashboard Home, y crear un script de carga inicial determinista con divisiones mínimas exigidas. Se mantiene compatibilidad con la estrategia Orion-first + fallback SQLite sin sincronización Orion⟷SQLite.

## Aceptance Criteria

### Atributos Ampliados
- ✅ **Employee:**
  - `email`: Formato RFC5322 válido, único
  - `dateOfContract`: ISO-8601 DateTime, obligatorio
  - `skills`: Array con enum {MachineryDriving, WritingReports, CustomerRelationships}, obligatorio, no vacío
  - `username`: Text 4-32 caracteres, único, obligatorio
  - `password`: Text, obligatorio (en demo sin hash, deuda documentada)
  - `refStore`: Relationship a una única Store (cardinalidad 1)

- ✅ **Store:**
  - `url`: URL válida (http/https), opcional
  - `telephone`: Patrón internacional válido, opcional
  - `capacity`: Número > 0, obligatorio
  - `description`: Text máx 2000 caracteres, opcional
  - `temperature`: Float -30.0 a 60.0 °C, opcional, externo
  - `relativeHumidity`: Float 0.0 a 100.0 %, opcional, externo

- ✅ **Product:**
  - `color`: Hex RGB (#RRGGBB), obligatorio
  - (Sin cambios adicionales; ya implementado)

### Dataset Determinista
- ✅ 4 Employees (E001–E004)
- ✅ 4 Stores (S001–S004)
- ✅ 4 Shelves por Store = 16 Shelves totales
- ✅ 10 Products
- ✅ 64+ InventoryItems con distribución mínima 4 productos por estantería

### Diagrama UML Mermaid
- ✅ Representación ER en Home (dashboard.html)
- ✅ Entidades: Store, Employee, Shelf, Product, InventoryItem
- ✅ Relaciones: Store 1..N Employee, Store 1..N Shelf, Shelf 1..N InventoryItem, Product 1..N InventoryItem
- ✅ Renderizado responsivo sin romper layout

### Validaciones & Integridad
- ✅ Todas las nuevas validaciones en `routes/utils.py` vía `normalize_ngsi_payload()`
- ✅ Tests unitarios para validación de atributos
- ✅ Tests de integración CRUD con nuevos campos
- ✅ Tests e2e con fallback SQLite
- ✅ 108/108 tests pasando sin regresiones

### Documentación Sincronizada
- ✅ `PRD.md`: Requisitos funcionales FR-051..FR-055 + cierre Issue #9
- ✅ `architecture.md`: Decisiones técnicas + integraciones Mermaid
- ✅ `data_model.md`: Especificación completa NGSIv2 + validaciones + closure

## Plan de Implementación (8 Fases)

### Fase 1: Alineación Funcional & Criterios de Aceptación
- Consolidar criterios en PRD/architecture/data_model
- Definir características del dataset inicial (4 emp, 4 stores, 16 shelves, 10 prod, 64+ items)
- **Entrada para:** Fases 2-8

### Fase 2: Auditoría del Modelo & Gap Analysis
- Revisar atributos actuales en `routes/utils.py`
- Identificar 20+ gaps de validación
- Documentar reglas de negocio por entidad
- **Entrada para:** Phase 3 & changes en normalizacion

### Fase 3: Diseño de Cambios NGSIv2
- Especificar contratos NGSIv2 (Text/Number/DateTime/Array/Relationship)
- Definir enums y rangos de validación
- Documentar política de seguridad (password en texto para demo)
- **Entrada para:** formularios y validaciones

### Fase 4: Representación UML con Mermaid
- Definir diagrama ER (5 entidades, 5 relaciones)
- Integración en dashboard.html
- Script CDN en base.html
- Inicialización en app.js
- **Depende de:** dashboard template

### Fase 5: Cambios en Capa de Aplicación & Validaciones
- Extender `routes/utils.py` con 98 líneas de validación
- Actualizar formularios HTML (templates/stores/form.html)
- Ajustar vistas list/detail para nuevos atributos
- **Bloquea:** Tests de CRUD

### Fase 6: Script de Carga Inicial
- Modificar `scripts/load_test_data.py`
- SHELVES_PER_STORE: 3 → 4
- EMPLOYEES_DATA: 8 → 4
- Distribucion mínima garantizada
- **Usa:** Reglas de Fase 3

### Fase 7: Pruebas & Verificación
- Unit: validaciones nuevas
- Integration: CRUD con nuevos campos
- E2E: con/sin Orion
- Smoke: Dashboard + Mermaid
- **Bloquea:** Cierre Issue

### Fase 8: Cierre Documental
- Actualizar PRD.md + architecture.md + data_model.md
- Registrar evidencias de tests
- Commit con "Closes #9"
- **Obligatorio** antes de merge

## Archivos a Modificar

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `routes/utils.py` | Validaciones Employee/Store | +98 |
| `templates/dashboard.html` | Sección Mermaid ERD | +68 |
| `templates/base.html` | Script CDN Mermaid | +1 |
| `templates/stores/form.html` | Nuevos campos Store | +20 |
| `static/css/main.css` | Estilos Mermaid container | +19 |
| `static/js/app.js` | Inicializacion Mermaid | +8 |
| `scripts/load_test_data.py` | Reconfiguracion dataset | +14 |
| `PRD.md` | Requisitos + closure | +86 |
| `architecture.md` | Decisiones técnicas + closure | +82 |
| `data_model.md` | Especificacion NGSIv2 + closure | +120 |

## Decisiones de Alcance

### Incluido
- ✅ Ampliación de atributos Employee/Store/Product
- ✅ Diagrama UML Mermaid en dashboard Home
- ✅ Script de carga inicial con cardinalidades mínimas
- ✅ Validaciones completas NGSIv2 en capa central

### Excluido
- ❌ Sincronizacion Orion⟷SQLite (se mantiene Orion-first + fallback)
- ❌ Rediseno visual global fuera del UML
- ❌ Implementacion de seguridad avanzada de credenciales (se documenta deuda)

## Notas Técnicas

1. **Validaciones centralizadas:** Todas en `normalize_ngsi_payload()` de routes/utils.py
2. **Estrategia de datos:** Orion primario, SQLite fallback, sin sync automático
3. **Password en demo:** Almacenado en texto claro, se documenta como deuda técnica en data_model.md
4. **Mermaid rendering:** CDN (jsdelivr.net), inicialización en app.js.DOMContentLoaded
5. **Tests:** Suite completa debe pasar sin regresiones (actual: 108/108)

## Definiciones & Referencias

- **NGSI:** FIWARE Next Generation Service Interface v2
- **Orion:** FIWARE Context Broker (motor principal)
- **SQLite:** Base de datos fallback cuando Orion no disponible
- **Mermaid:** Librería de diagramas (ERD, flowchart, secuencia, etc.)
- **ER Diagram:** Entity Relationship, visualiza entidades y relaciones

## Trazabilidad

| Documento | Sección | Estado |
|-----------|---------|--------|
| PRD.md | FR-051..FR-055, Issue #9 closure | Pending implementation |
| architecture.md | Data model extension, Mermaid integration | Pending implementation |
| data_model.md | Employee/Store/Product specs, validations | Pending implementation |

## Cierre

Este issue se considerará completado cuando:

1. ✅ Todas las 8 fases implementadas y verificadas
2. ✅ 108/108 tests pasando
3. ✅ PRD/architecture/data_model actualizado y sincronizado
4. ✅ Commit pushado a origin/main con referencia "Closes #9"
5. ✅ Diagrama UML renderizable en Home bajo cualquier condición de datos

---

**Etiquetas propuestas:** `feature`, `data-model`, `nice-to-have`
**Prioridad:** Media (requisito para release v0.3)
**Sprint:** Actual
