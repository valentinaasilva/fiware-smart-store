# Instrucciones para Crear Issue #9 en GitHub

## Opción 1: Crear Manualmente (Recomendado para menor riesgo)

### Paso 1: Ir a GitHub
1. Abre https://github.com/valentinaasilva/fiware-smart-store
2. Haz clic en la pestaña **"Issues"**
3. Haz clic en botón verde **"New issue"**

### Paso 2: Copiar Contenido
1. Abre el archivo `ISSUE_9_CONTENT.md` en el workspace
2. Copia TODO el contenido del archivo

### Paso 3: Crear Issue
1. En GitHub, pega el contenido en el cuerpo del issue
2. El título se extraerá automáticamente de la primera línea
3. Añade las etiquetas: `feature`, `data-model`, `nice-to-have`
4. Haz clic en **"Submit new issue"**

---

## Opción 2: Automatizado con Script

### Pre-requisitos
1. Generar GitHub Personal Access Token:
   - GitHub → Settings → Developer Settings → Personal Access Tokens → Classic tokens
   - Crear nuevo token con scope `repo` (acceso completo a repositorios)
   - Copiar el token (solo se ve una vez)

2. Asegurar que `requests` está disponible (✓ verificado)

### Paso 1: Ejecutar Script
```bash
cd /home/valen/XDEI/fiware-smart-store
python3 create_issue_9.py --token <tu_github_token>
```

O usar variable de entorno:
```bash
export GITHUB_TOKEN=<tu_github_token>
python3 create_issue_9.py
```

### Resultado Esperado
```
Creating issue in valentinaasilva/fiware-smart-store...
Title: Issue #9: Ampliación del Modelo de Datos & UML con Mermaid

✅ Issue created successfully!
   Issue #: 9
   URL: https://github.com/valentinaasilva/fiware-smart-store/issues/9
```

---

## Contenido del Issue

El archivo `ISSUE_9_CONTENT.md` contiene:
- **Objetivo:** Ampliación modelo datos + UML Mermaid
- **Aceptance Criteria:** 38 checks específicos
- **Plan de Implementación:** 8 fases detalladas
- **Archivos a Modificar:** 10 archivos con líneas estimadas
- **Decisiones de Alcance:** Componentes incluidos/excluidos
- **Trazabilidad:** Sincronización PRD/architecture/data_model

Tamaño total: ~2,500 caracteres

---

## Verificación Post-Creación

Una vez creado el issue #9, verifica estos puntos:

✅ Issue aparece en https://github.com/valentinaasilva/fiware-smart-store/issues/9
✅ Titulo: "Issue #9: Ampliación del Modelo de Datos & UML con Mermaid"
✅ Etiquetas: feature, data-model, nice-to-have
✅ 8 fases de implementación listadas
✅ Aceptance criteria con 38+ checkboxes
✅ Trazabilidad a PRD/architecture/data_model documentada

---

## Archivos Generados

Para facilitar el proceso automático, se han creado:

1. **ISSUE_9_CONTENT.md** (2,5 KB)
   - Contenido completo del issue en markdown
   - Listo para copiar-pegar

2. **create_issue_9.py** (3,5 KB)
   - Script Python que usa GitHub REST API v3
   - Autentica con Personal Access Token
   - Crear el issue automáticamente
   - Requiere token del usuario

---

## Seguridad

⚠️ **Importante:**
- NO compartir el GitHub token en chat, commits, o archivos públicos
- El token tiene acceso completo al repositorio
- Los tokens se pueden revocar en GitHub Settings → Personal Access Tokens

---

## Problemas Comunes

| Problema | Solución |
|----------|----------|
| Error 401 (Unauthorized) | Verifica que el token sea válido y tenga scope `repo` |
| Error 404 (Not Found) | Verifica owner/repo: valentinaasilva/fiware-smart-store |
| Error 422 (Validation) | El titulo o body pueden tener caracteres inválidos |
| Token expirado | Genera uno nuevo en GitHub Settings |

---

## Próximos Pasos Después del Issue

Una vez creado el issue #9:

1. Ejecutar las 8 fases de implementación
2. Cada fase debe actualizar el estado del issue
3. Al completar, tagging el commit con `Closes #9`
4. El issue se cerrará automáticamente al hacer merge a main

---

## Referencias

- GitHub Issues API: https://docs.github.com/en/rest/issues
- Personal Access Tokens: https://github.com/settings/tokens
- Issue #9 Plan (detallado): /memories/session/plan.md
