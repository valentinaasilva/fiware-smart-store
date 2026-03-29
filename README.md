# FIWARE Smart Store

Aplicacion Flask para gestion de cadena de supermercados con integracion Orion Context Broker (NGSIv2) y fallback a SQLite.

## Requisitos

- Python 3.12+
- Entorno virtual en `.venv`
- Docker + Docker Compose (para stack Orion/Mongo/tutorial)

## URL del repositorio

- https://github.com/valentinaasilva/fiware-smart-store

## Ejecucion rapida

1. Activar entorno virtual:

```bash
source .venv/bin/activate
```

2. Arrancar stack + aplicacion con script operativo:

```bash
./start.sh
```

3. Abrir la aplicacion en:

- http://localhost:5000

4. Detener aplicacion y contenedores:

```bash
./stop.sh
```

## Alternativa manual

1. Levantar contenedores Orion/Mongo/tutorial:

```bash
docker compose up -d
```

2. Arrancar Flask:

```bash
python app.py
```

3. (Opcional) Cargar datos de prueba en SQLite:

```bash
python scripts/load_test_data.py --target sqlite --sqlite-path instance/fiware.db --clean --verbose
```

## Notas

- Seleccion de fuente de datos al arranque:
  - Orion disponible -> modo ORION
  - Orion no disponible -> fallback SQLITE
- No hay sincronizacion de datos entre Orion y SQLite.
