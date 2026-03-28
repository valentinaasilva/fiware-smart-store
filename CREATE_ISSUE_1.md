# 📖 Instrucciones para crear Issue #1 en GitHub

El repositorio remoto en GitHub aún no existe o no hay acceso a través de credenciales instaladas localmente. Aquí hay varias opciones para crear el Issue #1:

## Opción 1: Crear manualmente en GitHub (Recomendado - 2 minutos)

1. **Crea el repositorio en GitHub:**
   - Ve a https://github.com/new
   - Nombre: `fiware-smart-store`
   - Descripción: "FIWARE-based smart store management system with NGSIv2 integration"
   - Visibilidad: Public
   - Click "Create repository"

2. **Crea el Issue #1:**
   - En tu nuevo repositorio, ve a la pestaña **Issues**
   - Click en **New issue**
   - Copia el contenido de [ISSUE_1.md](ISSUE_1.md)
   - Pega en el título y descripción:
     - **Título:** `Issue #1: Crear aplicación base de gestión de cadena de supermercados con datos de prueba`
     - **Descripción:** (Copia todo el contenido de ISSUE_1.md desde la línea con `## 🎯 Descripción`)
   - Asigna la etiqueta `phase-1` o `implementation`
   - Click **Submit new issue**

3. **Vincula tu repositorio local:**
   ```bash
   cd /home/valen/XDEI/fiware-smart-store
   git remote -v  # Verifica que apunte a tu repo nuevo
   git push -u origin main  # Sube tu código local
   ```

---

## Opción 2: Usar GitHub CLI (si lo instalas)

```bash
# Instalar gh CLI
brew install gh  # macOS
# o en Linux: sudo apt install gh

# Autenticarte
gh auth login

# Crear el issue
gh issue create \
  --title "Issue #1: Crear aplicación base de gestión de cadena de supermercados con datos de prueba" \
  --body "$(cat ISSUE_1.md | tail -n +3)" \
  --label "phase-1,implementation"
```

---

## Opción 3: Usar API REST de GitHub con curl (avanzado)

```bash
# Requiere un token de GitHub personal (ghp_xxx)
export GITHUB_TOKEN="tu_token_aqui"

curl -X POST https://api.github.com/repos/valentinaasilva/fiware-smart-store/issues \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "title": "Issue #1: Crear aplicación base de gestión de cadena de supermercados con datos de prueba",
  "body": "$(cat ISSUE_1.md | tail -n +3)",
  "labels": ["phase-1", "implementation"]
}
EOF
```

---

## Archivo de referencia

- **[ISSUE_1.md](ISSUE_1.md)** - Contenido completo del issue en formato Markdown

Este archivo includes:
- ✅ Especificación de 4 Stores, 10 Products, 10 Employees, 12 Shelves, 50+ InventoryItems
- ✅ Estructura de carpetas y archivos a crear
- ✅ Especificación del script `load_test_data.py`
- ✅ Test suites requeridas
- ✅ 13 Criterios de Aceptación
- ✅ Dependencias y línea de tiempo estimada

---

## Próximos pasos (después de crear el Issue)

1. ✅ Crear el Issue #1 en GitHub
2. ⏭️ Implementar `scripts/load_test_data.py`
3. ⏭️ Crear test suites en `tests/`
4. ⏭️ Ejecutar carga de datos contra Orion local
5. ⏭️ Cerrar Issue #1 con actualización de PRD/architecture/data_model

---

**Recomendación:** Usa la **Opción 1** (manual) - es la más rápida y directa.
