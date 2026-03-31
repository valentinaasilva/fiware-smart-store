#!/usr/bin/env python3
"""
Script para verificar suscripciones activas en Orion Context Broker.

Uso:
    python scripts/check_subscriptions.py
    python scripts/check_subscriptions.py http://localhost:1026  # Custom Orion URL
"""

import os
import sys
import json
import requests
from typing import Optional

def check_subscriptions(orion_url: str = "http://localhost:1026") -> None:
    """
    Lista todas las suscripciones registradas en Orion.
    
    Args:
        orion_url: URL base del Orion Context Broker
    """
    endpoint = f"{orion_url}/v2/subscriptions"
    
    try:
        print(f"\n📡 Verificando suscripciones en: {endpoint}")
        print("=" * 80)
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        subscriptions = response.json()
        
        if not subscriptions:
            print("⚠️  No hay suscripciones registradas en Orion.")
            return
        
        print(f"\n✅ Total de suscripciones: {len(subscriptions)}\n")
        
        for i, sub in enumerate(subscriptions, 1):
            print(f"📌 Suscripción #{i}")
            print(f"   ID: {sub.get('id')}")
            print(f"   Descripción: {sub.get('description', 'N/A')}")
            print(f"   Estado: {sub.get('status', 'unknown')}")
            
            # Información del subject (qué monitorea)
            subject = sub.get("subject", {})
            entities = subject.get("entities", [])
            if entities:
                for entity in entities:
                    print(f"   Monitoreando entidades tipo: {entity.get('type')} (patrón: {entity.get('idPattern', 'N/A')})")
            
            condition = subject.get("condition", {})
            attrs = condition.get("attrs", [])
            if attrs:
                print(f"   Atributos monitoreados: {', '.join(attrs)}")
            
            # Información de notificación (dónde enviar)
            notification = sub.get("notification", {})
            http_config = notification.get("http", {})
            callback_url = http_config.get("url")
            if callback_url:
                print(f"   URL de callback: {callback_url}")
            
            attrs_notif = notification.get("attrs", [])
            if attrs_notif:
                print(f"   Atributos a enviar: {', '.join(attrs_notif)}")
            
            print()
        
        print("=" * 80)
        print("\n✨ Verificación completada.\n")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: No se puede conectar a Orion en {orion_url}")
        print("   ¿Está Orion corriendo? Prueba: docker-compose ps")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        sys.exit(1)
    except requests.exceptions.JSONDecodeError:
        print("❌ Error: Respuesta de Orion no es JSON válido")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


def test_webhook_availability(callback_url: str) -> Optional[dict]:
    """
    Prueba si la URL de callback del webhook es accesible.
    
    Args:
        callback_url: URL del webhook (ej: http://host.docker.internal:5000/notifications/price-change)
    
    Returns:
        Resultado del test o None si hay error
    """
    try:
        # Para test, intentamos una petición POST sin body (los webhooks típicamente
        # aceptan POST con cuerpo, pero queremos verificar accesibilidad básica)
        print(f"\n🔗 Probando accesibilidad del webhook: {callback_url}")
        
        # En lugar de POST, hacemos OPTIONS para no afectar el sistema
        response = requests.options(callback_url, timeout=3)
        if response.status_code in (200, 404, 405):  # 405 es OK (método no permitido)
            print(f"   ✅ Webhook accesible (status {response.status_code})")
            return True
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ No se puede conectar a {callback_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout conectando a {callback_url}")
        return False
    except Exception as e:
        print(f"   ⚠️  Error verificando webhook: {e}")
        return None


if __name__ == "__main__":
    # Obtener URL de Orion de argumentos o variable de entorno
    orion_url = os.getenv("ORION_URL", "http://localhost:1026")
    if len(sys.argv) > 1:
        orion_url = sys.argv[1]
    
    # Listar suscripciones
    check_subscriptions(orion_url)
    
    # Si hay suscripciones, intentar verificar webhooks
    try:
        response = requests.get(f"{orion_url}/v2/subscriptions", timeout=5)
        subscriptions = response.json()
        
        if subscriptions:
            print("\n🧪 Verificando accesibilidad de webhooks:")
            print("=" * 80)
            for sub in subscriptions:
                notification = sub.get("notification", {})
                http_config = notification.get("http", {})
                callback_url = http_config.get("url")
                if callback_url:
                    test_webhook_availability(callback_url)
            print("=" * 80 + "\n")
    except Exception:
        pass  # No interrumpir si fallan las pruebas de webhook
