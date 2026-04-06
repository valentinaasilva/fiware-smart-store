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

El script `start.sh` ejecuta siempre en este orden:
1. Levanta stack Docker (Orion/Mongo/tutorial)
2. Carga dataset en Orion (`scripts/load_test_data.py --target orion --clean`)
3. Arranca Flask app

Para desactivar el seed automatico de forma puntual:

```bash
SEED_ON_START=0 ./start.sh
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
- Registro automatico NGSIv2 al arranque en modo ORION:
  - 2 providers externos para `Store` via `POST /v2/registrations`.
  - Provider A: atributos `temperature` y `relativeHumidity`.
  - Provider B: atributo `tweets`.
  - Se usan endpoints explicitos de provider por atributo; no se usa URL generica del tutorial.

## Variables de entorno

- `ORION_URL`: URL del Orion Context Broker. Default: `http://localhost:1026`.
- `CALLBACK_BASE_URL`: base de callbacks para subscriptions. Default: `http://host.docker.internal:5000`.
- `PROVIDER_BASE_URL`: base del provider externo (NGSI). Default: `http://host.docker.internal:5000`.
- `WEATHER_PROVIDER_URL`: endpoint NGSI para weather provider de `Store`. Default: `${PROVIDER_BASE_URL}/providers/weather`.
- `TWEETS_PROVIDER_URL`: endpoint NGSI para tweets provider de `Store`. Default: `${PROVIDER_BASE_URL}/providers/tweets`.

## Troubleshooting Linux

- Si en modo ORION no aparecen `temperature`, `relativeHumidity`, `tweets` o notificaciones realtime, normalmente Orion no puede alcanzar los endpoints de Flask.
- Este repositorio ya define `extra_hosts: host.docker.internal:host-gateway` en `orion-v2` para resolver ese host en Linux.
- Tras cambios de compose, reinicia Orion para aplicar networking:

```bash
docker compose up -d --force-recreate orion-v2
```

- Si Flask no corre en `:5000`, ajusta `CALLBACK_BASE_URL` y `PROVIDER_BASE_URL` al host/puerto correctos antes de iniciar la app.
