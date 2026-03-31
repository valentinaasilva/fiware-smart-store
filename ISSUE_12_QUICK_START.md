# 🚀 QUICK START: Crear Issue #12 en GitHub

## 📋 TL;DR

Tu issue #12 está listo para crear en GitHub. Aquí hay dos formas rápidas:

---

## ✅ Opción A: Copia y pega (2 minutos)

**Paso 1:** Abre [ISSUE_12.md](ISSUE_12.md) en tu editor  
**Paso 2:** Selecciona TODO el contenido desde `## 🎯 Descripción` hasta el final  
**Paso 3:** Ve a https://github.com/tu-usuario/fiware-smart-store/issues/new  
**Paso 4:** Pega el contenido en el campo Description  
**Paso 5:** Título: `Issue #12: Implementar suscripciones de Orion (NGSIv2) y notificaciones en tiempo real con SocketIO`  
**Paso 6:** Click Create issue ✅

---

## ✅ Opción B: GitHub CLI (1 minuto)

Si tienes `gh` CLI instalado:

```bash
cd /home/soraya/xdei/P2/fiware-smart-store
gh issue create \
  --title "Issue #12: Implementar suscripciones de Orion (NGSIv2) y notificaciones en tiempo real con SocketIO" \
  --body "$(tail -n +3 ISSUE_12.md)" \
  --label "feature,realtime,orion,socketio"
```

---

## 📝 Contenido del Issue

**Líneas de acción:**
1. ✅ Backend: Procesar payloads NGSIv2 de Orion
2. ✅ Backend: Emitir eventos SocketIO (price_changed, low_stock)
3. ✅ Frontend: Cliente SocketIO en JavaScript
4. ✅ Frontend: Actualizar DOM dinámicamente (sin reload)
5. ✅ Templates: Agregar data attributes
6. ✅ Estilos: Animaciones de resaltado

**Estimación:** 4-6 horas  
**Complejidad:** Media-Alta  
**Dependencias:** Orion + Flask + SocketIO (todos ya presentes ✅)

---

## 🎯 Próximos pasos después de crear

1. Abre GitHub, encuentra tu issue #12
2. Crea rama local:
   ```bash
   git checkout -b feature/issue-12-realtime-notifications
   ```
3. Comienza con **Fase 1** del plan (verificar suscripciones Orion)

---

## 📚 Documentos de referencia

- **Plan detallado:** `/memories/session/plan.md`
- **Issue full:** [ISSUE_12.md](ISSUE_12.md)
- **Instrucciones:** [CREATE_ISSUE_12.md](CREATE_ISSUE_12.md)

---

**¿Listo? Ve a [CREATE_ISSUE_12.md](CREATE_ISSUE_12.md) para las instrucciones completas.**
