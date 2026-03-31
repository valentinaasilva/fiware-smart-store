# 📖 Instrucciones para crear Issue #12 en GitHub

El issue #12 propone: **Implementar suscripciones de Orion (NGSIv2) y notificaciones en tiempo real con SocketIO**.

El contenido completo está en [ISSUE_12.md](ISSUE_12.md).

---

## Opción 1: Crear manualmente en GitHub (Recomendado - 3 minutos)

1. **Abre tu repositorio GitHub:**
   - URL: `https://github.com/tu-usuario/fiware-smart-store`
   - Pestaña: **Issues**

2. **Crea un nuevo issue:**
   - Click en **New issue**
   - Pon el **Título:**
     ```
     Issue #12: Implementar suscripciones de Orion (NGSIv2) y notificaciones en tiempo real con SocketIO
     ```

3. **Copia el contenido de la descripción:**
   - Abre [ISSUE_12.md](ISSUE_12.md) en tu editor
   - Selecciona TODO desde `## 🎯 Descripción` hasta el final
   - Pégalo en el campo **Description** del issue en GitHub

4. **Agrega etiquetas (opcional pero recomendado):**
   - `feature`
   - `realtime`
   - `orion`
   - `socketio`

5. **Opcionales:**
   - Asigna a responsable (si trabajas en equipo)
   - Asigna al milestone correspondiente (ej: "Phase 2")
   - Agrega a un project board si existe

6. **Click "Submit new issue"**

---

## Opción 2: Usar GitHub CLI (si lo tienes instalado)

```bash
# Instalar GitHub CLI (si no lo tienes)
# macOS:
brew install gh

# Debian/Ubuntu:
sudo apt install gh

# Fedora:
sudo dnf install gh

# Autenticarte
gh auth login

# Crear el issue desde línea de comandos
gh issue create \
  --title "Issue #12: Implementar suscripciones de Orion (NGSIv2) y notificaciones en tiempo real con SocketIO" \
  --body "$(cat ISSUE_12.md | tail -n +3)" \
  --label "feature,realtime,orion,socketio"
```

---

## Opción 3: Desde VS Code con extensión

Si tienes instalada la extensión **GitHub Issues**:

1. Abre la Command Palette (`Ctrl+Shift+P`)
2. Escribe: "GitHub Issues: Create New Issue"
3. Rellena: título y descripción (copia de ISSUE_12.md)
4. Presiona Enter

---

## ✅ Verificación

Después de crear el issue:

1. **Verifica que el issue está en GitHub:**
   - URL: `https://github.com/tu-usuario/fiware-smart-store/issues/12`
   - Debe mostrar título y descripción completa

2. **Opcional: Vincula a ramas futuras**
   - Cuando hagas commit, incluye: `Closes #12` en el mensaje para auto-linkar

3. **Opcional: Agrega checklist en comentario**
   - El issue ya tiene un checklist integrado (tasks con `[ ]`)
   - Puedes ir marcando con `[x]` conforme avances

---

## 📝 Próximos pasos

Una vez creado el issue:

1. **En GitHub:** Asigna el issue a ti mismo
2. **Localmente:** Crea rama: `git checkout -b feature/issue-12-realtime-notifications`
3. **En el README o IMPLEMENTATION_SUMMARY.md:** Documenta el inicio de este issue
4. **Comienza la implementación:** Ver tasks en ISSUE_12.md

---

## 🔗 Referencias

- **Documento del issue:** [ISSUE_12.md](ISSUE_12.md)
- **Plan de implementación:** `/memories/session/plan.md`
- **Documentación GitHub:** https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues

---

¿Necesitas ayuda con algo específico de la creación del issue?

Si tienes acceso a GitHub y no quieres que te ayude manualmente, ejecuta esta opción rápida:

```bash
# Desde la carpeta del proyecto
cat ISSUE_12.md | head -n 150 | wc -l  # Ver número de líneas
# Luego copia manualmente a GitHub o usa gh CLI
```
