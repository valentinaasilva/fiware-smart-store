# Issue #12: Implementar suscripciones de Orion (NGSIv2) y notificaciones en tiempo real con SocketIO

## 🎯 Descripción

Implementar un **sistema completo de notificaciones en tiempo real** que conecte suscripciones de Orion Context Broker (NGSIv2) con actualizaciones dinámicas en el frontend mediante Flask-SocketIO.

**Contexto técnico:**
- Orion está en Docker, por lo que las callbacks deben usar `host.docker.internal`
- Backend Flask con SocketIO ya está inicializado
- Estructura de webhooks ya existe en `/notifications`
- Frontend necesita cliente SocketIO para escuchar eventos

**Objetivo:** Cuando cambia el precio de un Producto o el stock de un InventoryItem en Orion, el servidor notifica en tiempo real al cliente, que actualiza la UI sin reload.

---

## ✅ Criterios de aceptación

### 🔔 Backend Webhooks
- [ ] Endpoint `POST /notifications/price-change` procesa payload NGSIv2 de cambios de precio
  - Extrae: `id` (product_id), `price` (nuevo valor), `name`
  - Normaliza estructura compleja de Orion a formato simple
  - Emite evento SocketIO `"price_changed"` con payload normalizado
  - Retorna `200 OK {status: "ok"}`

- [ ] Endpoint `POST /notifications/low-stock` procesa payload NGSIv2 de bajo stock
  - Extrae: `id` (inventory_id), `refStore`, `refProduct`, `stockCount`
  - Normaliza y emite evento SocketIO `"low_stock"`
  - Retorna `200 OK`

- [ ] Suscripciones registradas en bootstrap Orion:
  - Suscripción 1: cambios de atributo `price` en entidades `Product`
    - Callback: `http://host.docker.internal:5000/notifications/price-change`
    - Condición monitorea: `attrs: ["price"]`
  - Suscripción 2: cambios de atributos `stockCount`, `shelfCount` en entidades `InventoryItem`
    - Callback: `http://host.docker.internal:5000/notifications/low-stock`
    - Condición monitorea: `attrs: ["stockCount", "shelfCount"]`

- [ ] Validar que `CALLBACK_BASE_URL` env var es `http://host.docker.internal:5000` en `docker-compose.yml` o `.env`

### 🌐 Frontend SocketIO
- [ ] Crear módulo JavaScript `static/js/socketio-client.js` que:
  - Inicializa conexión: `const socket = io();`
  - Escucha evento `"connect"` y loguea "Cliente conectado al servidor SocketIO"
  - Escucha evento `"disconnect"` y loguea "Cliente desconectado"
  - Define handlers para `"price_changed"` y `"low_stock"`

- [ ] Cargar scripts en `templates/base.html`:
  - `<script src="/static/socket.io/socket.io.js"></script>`
  - `<script src="/static/js/socketio-client.js"></script>`

- [ ] Integrar lógica de actualización dinámica:
  - Cuando llega `"price_changed"` con `{product_id, new_price}`:
    - Buscar elemento DOM con `data-product-id="{product_id}"`
    - Actualizar `.product-price` con nuevo precio
    - Aplicar clase `.highlight-flash` por 2 segundos (fade-in/out)
  - Cuando llega `"low_stock"` con `{inventory_id, stock_count, store_id}`:
    - Buscar elemento con `data-inventory-id="{inventory_id}"`
    - Actualizar `.stock-count` con nuevo valor
    - Si `stock_count < threshold` (ej: 5), aplicar clase `.alert-low-stock`

### 📱 Templates con data attributes
- [ ] `templates/products/list.html`:
  - Agregar `data-product-id="{product.id}"` a fila de tabla
  - Celda de precio con clase `.product-price`

- [ ] `templates/stores/detail.html` (si muestra inventario):
  - Agregar `data-inventory-id="{item.id}"` a elemento inventario
  - Agregar `data-stock-count="{item.stockCount}"` inicialmente
  - Celda de stock con clase `.stock-count`

### 🎨 Estilos
- [ ] Crear clase CSS `.highlight-flash` en `static/css/main.css`:
  ```css
  .highlight-flash {
    animation: flash-highlight 2s ease-in-out;
  }
  @keyframes flash-highlight {
    0%, 100% { background-color: transparent; }
    50% { background-color: rgba(255, 193, 7, 0.5); }
  }
  ```

- [ ] Crear clase CSS `.alert-low-stock`:
  ```css
  .alert-low-stock {
    background-color: rgba(244, 67, 54, 0.1);
    border-left: 3px solid #f44336;
    color: #f44336;
    font-weight: bold;
  }
  ```

### 🧪 Pruebas
- [ ] Test/validación manual end-to-end:
  1. Iniciar stack: `docker-compose up -d`
  2. Iniciar app: `source venv/bin/activate && python app.py`
  3. Abrir navegador: `http://localhost:5000`
  4. Abrir Developer Console (F12) → Console tab
  5. Verificar: "Cliente conectado al servidor SocketIO"
  6. Actualizar producto en Orion: `curl -X PATCH http://localhost:1026/v2/entities/urn:ngsi-ld:Product:PROD-001/attrs/price -H "Content-Type: application/json" -d '{"value": 25.99}'`
  7. Verificar: evento `"price_changed"` llega a consola del navegador
  8. Verificar: tabla de productos se actualiza sin reload

- [ ] Verificar suscripciones activas en Orion:
  ```bash
  curl http://localhost:1026/v2/subscriptions | jq '.[] | {id, description, status}'
  ```

- [ ] Test con múltiples clientes conectados:
  - Abrir 2 pestañas del navegador
  - Ambas deben recibir eventos simultáneamente

---

## 📋 Tasks

### Fase 1: Verificar y asegurar suscripciones en Orion
1. [ ] Revisar `models/data_source.py::_register_external_integrations()` línea ~70-115
   - Confirmar que dos suscripciones están definidas (price-change, low-stock)
   - Validar URLs de callback usan `host.docker.internal:5000`
   - Agregar logs para confirmar registro en bootstrap

2. [ ] Verificar `docker-compose.yml` y `.env`:
   - Confirmar `CALLBACK_BASE_URL=http://host.docker.internal:5000`
   - Confirmar puerto Flask es 5000

3. [ ] Crear script simple `scripts/check_subscriptions.py`:
   ```bash
   #!/usr/bin/env python3
   # Lista todas las suscripciones activas en Orion
   # Uso: python scripts/check_subscriptions.py
   ```

### Fase 2: Mejorar webhooks del backend
4. [ ] Refactorizar `routes/notifications.py`:
   - Para `/price-change`:
     - Procesar payload NGSIv2 (estructura con `data[]`)
     - Extraer `id`, `price.value`, `name.value`
     - Normalizar: `{product_id, new_price, name, timestamp}`
     - Emitir a SocketIO con payload normalizado
   
   - Para `/low-stock`:
     - Procesar payload similiar
     - Extraer `id`, `refStore`, `refProduct`, `stockCount.value`
     - Normalizar: `{inventory_id, store_id, product_id, stock_count, timestamp}`
     - Emitir a SocketIO

5. [ ] Agregar logging en webhooks para debugging

### Fase 3: Implementar cliente SocketIO en frontend
6. [ ] Crear `static/js/socketio-client.js` con:
   - Inicialización SocketIO
   - Listeners: connect, disconnect, price_changed, low_stock
   - Lógica de actualización DOM

7. [ ] Actualizar `templates/base.html`:
   - Cargar scripts SocketIO

8. [ ] Actualizar `static/css/main.css`:
   - Styles para `.highlight-flash` y `.alert-low-stock`

### Fase 4: Agregar atributos a templates
9. [ ] Actualizar `templates/products/list.html`:
   - Agregar data attributes a tabla

10. [ ] Actualizar `templates/stores/detail.html` (si aplica)

### Fase 5: Pruebas y documentación
11. [ ] Ejecutar test end-to-end manual
12. [ ] Validar suscripciones en Orion
13. [ ] Documento de actualización en PRD.md/architecture.md/data_model.md

---

## 📚 Archivos relevantes

- **Backend:**
  - [app.py](app.py#L178-L253) — SocketIO inicializado ✅
  - [models/data_source.py](models/data_source.py#L70-L115) — Suscripciones (verificar/mejorar)
  - [models/orion_client.py](models/orion_client.py#L93) — `register_subscription()`
  - [routes/notifications.py](routes/notifications.py) — Webhooks Orion (refactor)

- **Frontend:**
  - [templates/base.html](templates/base.html) — Shell UI (agregar scripts)
  - [templates/products/list.html](templates/products/list.html) — Tabla productos (agregar data attrs)
  - [templates/stores/detail.html](templates/stores/detail.html) — Detalle tienda (agregar data attrs si aplica)
  - [static/js/app.js](static/js/app.js) — Lógica existente
  - [static/js/socketio-client.js](static/js/socketio-client.js) — **NUEVO**
  - [static/css/main.css](static/css/main.css) — Estilos (agregar clases)

- **Infraestructura:**
  - [docker-compose.yml](docker-compose.yml) — Validar vars env
  - [.env](.env) o env vars

- **Testing:**
  - [scripts/check_subscriptions.py](scripts/check_subscriptions.py) — **NUEVO**
  - [tests/integration/test_notifications.py](tests/integration/test_notifications.py) — Considera agregar tests

---

## 🔄 Flujo de datos

```
┌─────────────────────────────────────────────────────────────┐
│ NAVEGADOR (Cliente)                                         │
│ • static/js/socketio-client.js escucha eventos            │
│ • Actualiza DOM dinámicamente (sin reload)                │
└────────────────────┬────────────────────────────────────────┘
                     │ WebSocket (SocketIO)
                     │ "price_changed", "low_stock"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND FLASK (5000)                                        │
│ • routes/notifications.py recibe webhooks                  │
│ • Procesa payload NGSIv2 y normaliza                       │
│ • Emite eventos SocketIO a clientes conectados            │
└────────────────────┬────────────────────────────────────────┘
                     │ REST POST
                     │ /notifications/price-change
                     │ /notifications/low-stock
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ORION CONTEXT BROKER (Docker, 1026)                        │
│ • Subscripciones monitoras cambios de precio/stock        │
│ • Envía webhooks cuando hay cambios                        │
│ • Estructura payload: NGSIv2 compleja                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Órdenes de magnitud

- **Tiempo estimado:** 4-6 horas
- **Complejidad:** Media-Alta
  - Entender estructura NGSIv2 de payloads Orion
  - Coordinar backend-frontend vía SocketIO
  - Testing end-to-end Docker + Orion
  
- **Dependencias:**
  - Docker + Orion corriendo
  - Flask-SocketIO ya disponible (requirements.txt)
  - Navegador moderno con WebSocket

- **No requiere:**
  - Cambios en modelo de datos
  - Nuevas dependencias Python/npm
  - Cambios en CRUD existentes

---

## 📖 Notas

1. **Payload NGSIv2 de Orion:** depende de cómo se registre la suscripción. Típicamente:
   ```json
   {
     "subscriptionId": "...",
     "data": [
       {
         "id": "urn:ngsi-ld:Product:PROD-001",
         "type": "Product",
         "price": {"type": "Number", "value": 29.99},
         "name": {"type": "Text", "value": "Yogur"}
       }
     ]
   }
   ```

2. **SocketIO Broadcast vs Rooms:** Por simplicidad, usar broadcast global. Todos los clientes conectados reciben todos los eventos. Para escala productiva, considerar namespaces por tienda.

3. **Sincronización de datos:** Si cliente se conecta y ve datos stale, ¿hacer refresh? Recomendación: agregar en el servidor un evento de "sync" cuando cliente se conecta, que envía datos actuales principales.

4. **Debugging Orion:** `docker-compose logs -f orion-v2 | grep -i "POST\|callback"`

5. **CORS:** SocketIO CORS ya configurado en `app.py` con `cors_allowed_origins="*"`

---

## 🔗 Issue relacionados

- **Anterior:** Issue #11 (Providers externos de Store)
- **Siguiente:** Issue #13 (Audit log de cambios, persistencia de eventos)

---

## ✨ Verificación Final

Cuando este issue esté completo:
- [ ] PRD.md actualizado con explicación de feature Real-time
- [ ] architecture.md actualizado con diagrama actualizado de flujo SocketIO → Orion
- [ ] data_model.md sin cambios (modelos no se alteran)
- [ ] Código pusheado a rama `feature/issue-12-realtime-notifications`
- [ ] Suscripciones activas en Orion verificadas
- [ ] Test end-to-end pasado
