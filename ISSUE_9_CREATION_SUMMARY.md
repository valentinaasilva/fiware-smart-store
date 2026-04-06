# Issue #9 - Creación en GitHub: LISTO PARA EJECUTAR

**Fecha:** 2026-03-29  
**Estado:** Archivos generados y listos  
**Acción pendiente:** Proporcionar GitHub token o crear manualmente

---

## 📋 Resumen de lo Généralo

Se han creado los archivos necesarios para crear el **Issue #9 en GitHub** con el plan completo de implementación de la ampliación del modelo de datos. Los archivos están ubicados en la raíz del proyecto:

```
/home/valen/XDEI/fiware-smart-store/
├── ISSUE_9_CONTENT.md          (6.9 KB) — Contenido completo del issue
├── ISSUE_9_INSTRUCTIONS.md     (3.9 KB) — Instrucciones paso a paso
├── create_issue_9.py           (4.1 KB) — Script automático (ejecutable)
└── ISSUE_9_CREATION_SUMMARY.md (este archivo)
```

## 🎯 Contenido del Issue #9

**Título:** Issue #9: Ampliación del Modelo de Datos & UML con Mermaid

**Objetivo:** Ampliar el modelo de datos de Employee/Store/Product con atributos faltantes, representar el modelo con diagrama UML Mermaid en dashboard Home y crear script de carga inicial determinista.

**Componentes:**
- ✅ 20+ validaciones nuevas para Employee y Store
- ✅ Diagrama ER (Entity Relationship) con Mermaid
- ✅ Dataset deterministico: 4 emp, 4 stores, 16 shelves, 10 prod, 64+ items
- ✅ 8 fases de implementación con dependencias documentadas
- ✅ 38+ aceptance criteria checkables

**Tamaño:** ~2,500 caracteres (~0.5 páginas en PDF)

---

## 🚀 Cómo Crear el Issue

### Opción A: Manualmente (Recomendado - 2 minutos)
1. Abre https://github.com/valentinaasilva/fiware-smart-store/issues/new
2. Copia el contenido de `ISSUE_9_CONTENT.md`
3. Pégalo en el formulario de GitHub
4. Añade etiquetas: `feature`, `data-model`, `nice-to-have`
5. Click en "Submit new issue"

### Opción B: Script Automatizado (Requiere token - 30 segundos)
```bash
cd /home/valen/XDEI/fiware-smart-store
python3 create_issue_9.py --token <tu_github_token>
```

O con variable de entorno:
```bash
export GITHUB_TOKEN=<tu_github_token>
python3 create_issue_9.py
```

---

## 📝 Especificación del Issue

El issue contiene:

### 1. Objetivo & Scope
- Ampliación de atributos Employee/Store/Product
- Integración de Mermaid UML en dashboard
- Script de carga inicial determinista

### 2. Aceptance Criteria (38 checks)
- Atributos ampliados: Employee (6 nuevos), Store (6 nuevos), Product (1, color)
- Dataset: 4/4/16/10/64+
- UML: renderizado responsivo en Home
- Validaciones: centralizadas en routes/utils.py
- Tests: 108/108 pasando
- Docs: PRD/architecture/data_model sincronizadas

### 3. Plan 8 Fases
1. Alineación funcional & criterios
2. Auditoría del modelo & gap analysis
3. Diseño cambios NGSIv2
4. Representación UML Mermaid
5. Cambios capa aplicación & validaciones
6. Script de carga inicial
7. Pruebas & verificacion
8. Cierre documental & trazabilidad

### 4. Archivos a Modificar (10 total, ~430 líneas)
| Archivo | Cambios | Líneas |
|---------|---------|--------|
| routes/utils.py | Validaciones | +98 |
| templates/dashboard.html | Mermaid UML | +68 |
| templates/base.html | Script CDN | +1 |
| templates/stores/form.html | Nuevos campos | +20 |
| static/css/main.css | Estilos | +19 |
| static/js/app.js | Inicializacion | +8 |
| scripts/load_test_data.py | Dataset config | +14 |
| PRD.md | Reqtos + closure | +86 |
| architecture.md | Decisiones + closure | +82 |
| data_model.md | NGSIv2 + closure | +120 |

### 5. Decisiones de Alcance
**Incluido:**
- Ampliación atributos Employee/Store/Product
- Diagrama UML Mermaid en dashboard
- Script carga inicial determinista
- Validaciones centralizadas

**Excluido:**
- Sync Orion⟷SQLite
- Rediseno visual global
- Seguridad avanzada credenciales (se documenta deuda)

---

## 🔐 Seguridad

Para usar el script automático (Opción B), necesitas:
1. GitHub Personal Access Token (clásico, scope "repo")
   - Genera en: https://github.com/settings/tokens
   - Solo visible una vez
   - NO compartir en chat/commits/público

---

## 📊 Trazabilidad

El issue está completamente documentado con referencia a:
- **Plan:** /memories/session/plan.md (120 líneas, 8 fases)
- **Exploración:** /memories/session/issue_9_exploration.md (350+ líneas)
- **Auditoría Phase 2:** /memories/session/issue_9_phase_2_audit.md (100+ líneas)

Cada fase implementada debe actualizar estos 3 documentos:
- `PRD.md` — Requisitos funcionales
- `architecture.md` — Decisiones técnicas
- `data_model.md` — Modelo de datos NGSIv2

---

## ✅ Checklist de Creación

Antes de proceder con la creación, verifica:

- [ ] Tienes acceso al repositorio valentinaasilva/fiware-smart-store
- [ ] Has generado un GitHub Personal Access Token (si usas script)
- [ ] El token tiene scope `repo`
- [ ] `ISSUE_9_CONTENT.md` existe en /home/valen/XDEI/fiware-smart-store/
- [ ] `create_issue_9.py` es ejecutable (✓ confirmado)
- [ ] `requests` library está instalada (✓ confirmado: 2.32.3)

---

## 📞 Próximos Pasos

### Inmediatamente después de crear el issue:
1. Verificar que el issue aparece en GitHub con número #9
2. Verificar etiquetas: feature, data-model, nice-to-have
3. Copiar el link y compartirlo si es necesario

### Para iniciar la implementación:
1. Crear rama: `git checkout -b feature/issue-9-model-expansion`
2. Ejecutar Fase 1: Alineación funcional (3-4 horas)
3. Ejecutar Fase 2: Auditoría del modelo (2-3 horas)
4. Continuar con las 6 fases restantes (20-30 horas totales)

### Al completar:
1. Commit final con: `git commit -m "feat: Issue #9 data model expansion — Closes #9"`
2. Push: `git push origin feature/issue-9-model-expansion`
3. GitHub cerrará automáticamente el issue al hacer merge a main

---

## 🎯 Objetivos Finales

Cuando se complete Issue #9:

✅ Issue #9 creado en GitHub con especificación completa  
✅ Todas las 8 fases de implementación completadas  
✅ 20+ validaciones nuevas funcionando  
✅ Diagrama UML Mermaid renderizado en dashboard  
✅ Dataset determinístico: 4 emp, 4 stores, 16 shelves, 10 prod, 64+ items  
✅ 108/108 tests pasando sin regresiones  
✅ PRD/architecture/data_model sincronizados  
✅ Trazabilidad completa Issue → Implementación → Documentación  

---

## 📚 Referencias

- GitHub API: https://docs.github.com/rest/issues
- GitHub Tokens: https://github.com/settings/tokens
- FIWARE Smart Store: https://github.com/valentinaasilva/fiware-smart-store
- Issue #9 Plan: /memories/session/plan.md
