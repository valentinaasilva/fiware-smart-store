# ISSUE 14: Front-End Best Practices Refinement

**Status:** In Development
**Priority:** High
**Sprint:** P2
**Created:** 2026-03-31

---

## Objetivo

Realizar un audit completo y refinamiento de la capa front-end (HTML, CSS, JavaScript) para garantizar que cumple con los estándares de best practices y requermientos de calidad de código:

1. **Priorizar CSS sobre JavaScript**: CSS para estilos, animaciones, visibilidad
2. **Evitar generar HTML desde JS**: No `innerHTML`, sin creación dinámica de elementos
3. **JS actualiza elementos existentes**: `textContent`, atributos, clases (no direct style manipulation)
4. **Buena estructura**: HTML semántico, CSS organizado, JS modular y claro

---

## Estado Actual (Audit)

### ✅ Cumplimientos

- **HTML**: Semántico, limpio, cero `innerHTML`, sin creación dinámica
- **CSS**: Variables, clases reutilizables, tema oscuro CSS-driven, animaciones en `@keyframes`
- **JS**: Usa `classList`, `textContent`, atributos (sin direct style manipulation)

### ⚠️ Problemas Identificados

| # | Problema | Archivos | Impacto | Severidad |
|---|----------|----------|--------|-----------|
| 1 | Inline `onerror` event handlers | 8 templates (image fallbacks) | Inline handlers, no separation of concerns | 🔴 **ALTA** |
| 2 | Inline `style=` en templates | `products/list.html` L62-65 | CSS scattered, no reusability | 🔴 **ALTA** |
| 3 | Inline `onsubmit` confirmations | 3 list templates | Handlers en HTML | 🟡 **MEDIA** |
| 4 | Inconsistencia sintaxis JS | `app.js` (`var`) vs `socketio-client.js` (`const/let`) | Falta standardización | 🟡 **MEDIA** |
| 5 | Timer-based animations | `socketio-client.js` `applyHighlightFlash()` | Desincronización CSS-JS | 🟡 **MEDIA** |
| 6 | Falta accesibilidad | All templates | `aria-label`, `aria-live`, `role` | 🟡 **MEDIA** |
| 7 | Image fallback pattern | All templates with images | Fragile sibling dependency | 🟡 **MEDIA** |

---

## Solución Propuesta

### Fase 1: Extractar Image Fallback Handlers (PRIORIDAD ALTA)

**Objetivo:** Eliminar `onerror` inline. Crear módulo centralizado reutilizable.

**Cambios:**

1. **Crear:** `static/js/image-fallback.js`
   - Función `initImageFallbacks()` que atiende todos los elementos `[data-fallback-image]`
   - Patrón: imagen carga OK → mostrar; error → esconder imagen + mostrar fallback

2. **Actualizar:** `templates/base.html`
   - Importar nuevo script antes de `</body>`

3. **Actualizar:** 8 templates (partes con imágenes)
   - Reemplazar `onerror` attribute por `data-fallback-image`
   - Mantener fallback span

**Patrón:**
```html
<!-- ANTES -->
<img src="..." onerror="this.classList.add('is-hidden'); this.nextElementSibling.classList.remove('is-hidden');">

<!-- DESPUÉS -->
<img data-fallback-image src="..." alt="...">
<span class="img-fallback is-hidden">No image</span>
```

**Archivos afectados:**
- `static/js/image-fallback.js` (crear)
- `templates/base.html`
- `templates/dashboard.html`
- `templates/products/list.html`
- `templates/products/detail.html`
- `templates/stores/list.html`
- `templates/stores/detail.html`
- `templates/employees/list.html`
- `templates/employees/detail.html`

---

### Fase 2: Mover Inline Styles a Clases CSS (PRIORIDAD ALTA)

**Objetivo:** Eliminar `style=` inline en templates. Usar CSS + variables dinámicas.

**Cambios:**

1. **Actualizar:** `static/css/main.css`
   - Agregar clase `.color-swatch` con estilos base
   - Agregar `.color-swatch-dot` para el círculo de color

2. **Actualizar:** `templates/products/list.html`
   - Reemplazar `<span style="...">` con `<span class="color-swatch" style="--swatch-color: {{ product.color }};">`
   - Agregar `aria-label` para accesibilidad

**Patrón:**
```css
/* CSS */
.color-swatch {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.color-swatch-dot {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background-color: var(--swatch-color);
}
```

```html
<!-- ANTES -->
<span style="display:inline-flex; align-items:center; gap:.4rem;">
  <span style="display:inline-block; width:1rem; height:1rem; border-radius:999px; border:1px solid #d1d5db; background:{{ product.color }};"></span>
  <span class="mono">{{ product.color }}</span>
</span>

<!-- DESPUÉS -->
<span class="color-swatch" style="--swatch-color: {{ product.color }};" aria-label="Color: {{ product.color }}">
  <span class="color-swatch-dot"></span>
  <span class="mono">{{ product.color }}</span>
</span>
```

**Archivos afectados:**
- `static/css/main.css` (+20 líneas)
- `templates/products/list.html` (~5 líneas)

---

### Fase 3: Mejorar Animaciones – Event Listener (PRIORIDAD MEDIA)

**Objetivo:** Cambiar de `setTimeout` a `animationend` event. Sincronizar JS con CSS.

**Cambios:**

1. **Actualizar:** `static/js/socketio-client.js`
   - Función `applyHighlightFlash()`: usar `animationend` event en lugar de `setTimeout`
   - Eliminar dependency en hardcoded `durationMs`

**Patrón:**
```js
/* ANTES */
function applyHighlightFlash(element, className = "highlight-flash", durationMs = 2000) {
  element.classList.add(className);
  setTimeout(() => {
    element.classList.remove(className);
  }, durationMs);
}

/* DESPUÉS */
function applyHighlightFlash(element, className = "highlight-flash") {
  element.classList.add(className);
  element.addEventListener('animationend', () => {
    element.classList.remove(className);
  }, { once: true });
}
```

**Archivos afectados:**
- `static/js/socketio-client.js` (~10 líneas)

---

### Fase 4: Agregar Atributos de Accesibilidad (PRIORIDAD MEDIA)

**Objetivo:** Mejorar UX para screen readers y asistive technologies.

**Cambios:**

1. **Actualizar:** `templates/products/list.html`
   - `aria-label` en color swatches

2. **Actualizar:** `templates/stores/list.html`, `employees/list.html`
   - `role="alert"` en filas con `.alert-low-stock`
   - `aria-live="polite"` para notificaciones dinámicas

3. **Actualizar:** Todos templates con icons decorativos
   - `aria-hidden="true"` en icons (◫, ◼, ◉, ◍, ⌖, ☎, ✉, ⌕, etc.)

4. **Documentar:** `static/css/main.css`
   - Comentarios sobre patrones de accesibilidad

**Archivos afectados:**
- `templates/products/list.html`
- `templates/stores/list.html`
- `templates/employees/list.html`
- `templates/dashboard.html`
- `templates/base.html`
- `static/css/main.css` (comments)

---

### Fase 5: Modernizar JavaScript – ES6 Syntax (PRIORIDAD BAJA)

**Objetivo:** Normalizar a `const/let` (ES6). Eliminar `var`.

**Cambios:**

1. **Actualizar:** `static/js/app.js`
   - Reemplazar todos `var` por `const`
   - Agregar JSDoc comments

**Archivos afectados:**
- `static/js/app.js` (~10 líneas)

---

## Plan de Implementación

### Ordenamiento de Fases (por dependencias)

```
Fase 1: Image Handlers        ┐
                              ├──→ Verificación
Fase 2: CSS Color Swatches    ┤
                              ├──→ Pruebas
Fase 3: Animations            ┤
                              └──→ Docs Update
Fase 4: Accessibility (parallelizable)
Fase 5: JS Modernization (independent)
```

**Todas las fases pueden ejecutarse en paralelo** (sin conflictos de archivos dependientes).

---

## Archivos a Crear/Modificar

### Crear (2)
- `static/js/image-fallback.js` (~50 líneas)
- (Opcional) `static/js/forms.js` para future confirmations

### Modificar (9)
- `static/css/main.css` (+30 líneas)
- `static/js/app.js` (~15 líneas)
- `static/js/socketio-client.js` (~15 líneas)
- `templates/base.html` (+2 imports)
- `templates/dashboard.html` (attributes)
- `templates/products/list.html` (~30 líneas)
- `templates/products/detail.html` (attributes)
- `templates/stores/list.html` (attributes)
- `templates/stores/detail.html` (attributes)
- `templates/employees/list.html` (attributes)
- `templates/employees/detail.html` (attributes)

**Total de cambios:** ~150-200 líneas

---

## Verificación Post-Implementación

- [ ] ✅ Cero inline `onerror` attributes
- [ ] ✅ Cero inline `onsubmit` attributes  
- [ ] ✅ Cero inline `style=` tags (excepto variables dinámicas)
- [ ] ✅ Cero `innerHTML` o creación dinámica de DOM
- [ ] ✅ Todas las animaciones en `@keyframes`
- [ ] ✅ JS usa `const/let` consistentemente
- [ ] ✅ `aria-label`, `aria-live`, `role` en elementos interactivos
- [ ] ✅ `image-fallback.js` funciona en todas las páginas
- [ ] ✅ Tema oscuro mantiene funcionalidad
- [ ] ✅ SocketIO updates siguen reflejándose correctamente
- [ ] ✅ Tests pasan sin errores
- [ ] ✅ Documentación actualizada (PRD, architecture, data_model)

---

## Criterios de Aceptación

1. **Code Quality**
   - Cero violaciones de best practices detectadas por audit
   - Cero inline event handlers, styles, o HTML generation
   - Separación clara de concerns: HTML, CSS, JS

2. **Funcionalidad**
   - Todas las características existentes funcionan igual
   - Image fallbacks trabajan en todos templates
   - SocketIO updates y notificaciones reflejadas correctamente
   - Tema oscuro/claro funciona
   - Search, forms, deletions, updates funcionan

3. **Accesibilidad**
   - Screen readers pueden interpretar elementos interactivos
   - ARIA attributes presentes donde necesario
   - Icons decorativos marcados como `aria-hidden`

4. **Documentación**
   - PRD.md actualizado con cambios front-end
   - architecture.md documenta nuevos módulos JS
   - Comentarios en código (CSS, JS) explicando patrones

---

## Notas

- Este issue implementa **refinamiento de código, no nuevas features**
- Impacto en usuarios: **CERO** (cambios puramente internos)
- Beneficio: **Mejor mantenibilidad, accesibilidad, y performance**
- Tiempo estimado: **4-6 horas**

---

## Referencias

- [MDN: HTML Attributes](https://developer.mozilla.org/es/docs/Web/HTML/Attributes)
- [MDN: ARIA: alert role](https://developer.mozilla.org/es/docs/Web/Accessibility/ARIA/Roles/alert_role)
- [CSS Tricks: Event Listeners vs Inline Handlers](https://css-tricks.com)
- [JavaScript.info: Events](https://javascript.info/events)

---

**Next Steps:**
1. ✅ Crear issue (este archivo)
2. → Crear rama: `git checkout -b feature/issue-14-front-end-audit`
3. → Implementar todas las fases
4. → Pruebas
5. → Actualizar documentación
6. → PR + merge
