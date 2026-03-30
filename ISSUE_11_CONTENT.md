# Issue #11: Proveedores de contexto externo NGSIv2 para Store

## Objetivo
Implementar el registro automatico de proveedores de contexto externo en Orion NGSIv2 para entidades de tipo `Store`, separando los atributos externos en dos registros independientes:

1. `temperature` y `relativeHumidity`
2. `tweets`

El registro debe ejecutarse automaticamente al arrancar la aplicacion.

## Requisitos
- Usar Orion API de registros NGSIv2: `POST /v2/registrations`.
- Crear dos registros separados:
  - Registro A: `temperature` + `relativeHumidity`
  - Registro B: `tweets`
- Ambos aplican a entidades tipo `Store`.
- Registro automatico durante startup de la app.

## Acceptance Criteria
- [ ] Al iniciar la app con Orion disponible, se ejecutan dos `POST /v2/registrations`.
- [ ] Existe un registro activo para `attrs: ["temperature", "relativeHumidity"]` y `type: "Store"`.
- [ ] Existe un registro activo para `attrs: ["tweets"]` y `type: "Store"`.
- [ ] Ambos registros usan `idPattern: "urn:ngsi-ld:Store:.*"` para aplicar a todas las Store.
- [ ] El proceso es idempotente en reinicios (acepta `201` y `409` como exito).
- [ ] No hay regresion en fallback SQLite cuando Orion no esta disponible.
- [ ] Documentacion actualizada en `PRD.md`, `architecture.md` y `data_model.md`.

## Plan de Implementacion

### Fase 1: Integracion en startup
- Reutilizar el flujo actual de `DataSourceSelector.bootstrap()`.
- Mantener el registro dentro de `_register_external_integrations()` para que se ejecute solo si Orion esta saludable.

### Fase 2: Separar registrations
- Reemplazar el provider unico actual por dos payloads NGSIv2:
  - Payload A: weather (`temperature`, `relativeHumidity`)
  - Payload B: tweets (`tweets`)
- Ambos con:
  - `entities: [{"idPattern": "urn:ngsi-ld:Store:.*", "type": "Store"}]`
  - `status: "active"`

### Fase 3: Configuracion por entorno
- Introducir variables de entorno especificas con defaults:
  - `WEATHER_PROVIDER_URL` = `http://tutorial:3000/proxy/v1/random/weatherConditions`
  - `TWEETS_PROVIDER_URL` = `http://tutorial:3000/proxy/v1/catfacts/tweets`
- Mantener compatibilidad con configuracion actual del proyecto.

### Fase 4: Ejecucion y robustez
- Iterar los dos payloads y llamar `register_provider()` para cada uno.
- Preservar semantica idempotente del cliente Orion (`201` o `409` = exito).

### Fase 5: Pruebas
- Actualizar tests unitarios en `tests/unit/test_data_source.py` para validar 2 registros en bootstrap ORION.
- Validar contrato `register_provider()` en `tests/unit/test_orion_client.py`.
- Ejecutar suite objetivo:
  - `pytest tests/unit/test_data_source.py -q`
  - `pytest tests/unit/test_orion_client.py -q`

### Fase 6: Documentacion y trazabilidad
- Actualizar documentacion operativa en `README.md` (nuevas env vars y comportamiento en startup).
- Actualizar obligatoriamente:
  - `PRD.md`
  - `architecture.md`
  - `data_model.md`
- Mantener trazabilidad entre requisito funcional, decision de arquitectura y modelo NGSIv2.

## Archivos Impactados
- `models/data_source.py`
- `models/orion_client.py` (sin cambios de contrato esperados)
- `tests/unit/test_data_source.py`
- `tests/unit/test_orion_client.py`
- `README.md`
- `PRD.md`
- `architecture.md`
- `data_model.md`

## Verificacion Funcional
1. Arrancar aplicacion con `ORION_URL` valido.
2. Consultar Orion: `GET /v2/registrations`.
3. Confirmar presencia de dos registros para `Store`:
   - attrs weather: `temperature`, `relativeHumidity`
   - attrs social: `tweets`
4. Reiniciar aplicacion y validar que no falla por duplicados (`409` permitido).
5. Probar fallback cuando Orion no responde y confirmar operacion con SQLite.

## Fuera de alcance
- Cambios de UI/UX.
- Cambios de modelo de entidades no relacionados con providers externos.
- Sincronizacion Orion <-> SQLite.

## Definicion de completado
- [ ] Dos registrations NGSIv2 separadas, activas y funcionales para `Store`.
- [ ] Auto-registro en startup implementado.
- [ ] Tests relevantes pasando.
- [ ] `PRD.md`, `architecture.md`, `data_model.md` actualizados y consistentes.
