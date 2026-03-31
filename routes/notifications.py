import logging
from datetime import datetime
from typing import Any

from flask import Blueprint, current_app, jsonify, request

logger = logging.getLogger(__name__)
notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


def extract_attr_value(attr_value: Any) -> Any:
    """
    Extrae el valor de un atributo NGSIv2.
    
    NGSIv2 retorna atributos con estructura:
    - {"type": "Text", "value": "Yogur"}
    - {"type": "Number", "value": 29.99}
    - {"type": "Relationship", "object": "urn:ngsi-ld:Store:S001"}
    
    Esta función desenvuelve esa estructura.
    
    Args:
        attr_value: Atributo NGSIv2 (dict o valor simple)
    
    Returns:
        Valor extraído
    """
    if isinstance(attr_value, dict):
        # Intenta extraer "value" primero (atributos normales)
        if "value" in attr_value:
            return attr_value.get("value")
        # Para Relationships, usa "object"
        if "object" in attr_value:
            return attr_value.get("object")
    return attr_value


def normalize_ngsiv2_entity(entity: dict) -> dict:
    """
    Normaliza una entidad NGSIv2 a formato simple para el frontend.
    
    Entrada (NGSIv2):
    {
        "id": "urn:ngsi-ld:Product:PROD-001",
        "type": "Product",
        "price": {"type": "Number", "value": 29.99},
        "name": {"type": "Text", "value": "Yogur"}
    }
    
    Salida (normalizada):
    {
        "id": "urn:ngsi-ld:Product:PROD-001",
        "type": "Product",
        "price": 29.99,
        "name": "Yogur"
    }
    
    Args:
        entity: Entidad NGSIv2 del webhook
    
    Returns:
        Entidad normalizada
    """
    normalized = {}
    
    for key, value in entity.items():
        if key in ("id", "type"):
            normalized[key] = value
        else:
            normalized[key] = extract_attr_value(value)
    
    return normalized


def extract_entity_id_short(entity_id: str) -> str:
    """
    Extrae ID corto de un URN NGSIv2.
    
    urn:ngsi-ld:Product:PROD-001 → PROD-001
    urn:ngsi-ld:InventoryItem:INV-S001-SH1-P001 → INV-S001-SH1-P001
    
    Args:
        entity_id: URN completo
    
    Returns:
        ID corto (la última parte después de ':')
    """
    if ":" in entity_id:
        return entity_id.split(":")[-1]
    return entity_id


@notifications_bp.post("/price-change")
def price_change_webhook():
    """
    Webhook de Orion para cambios de precio de producto.
    
    Procesa payload NGSIv2, normaliza y emite evento SocketIO a clientes conectados.
    """
    try:
        payload = request.get_json(silent=True) or {}
        
        # Orion envía: {"subscriptionId": "...", "data": [{...}]}
        data_list = payload.get("data", [])
        if not data_list:
            logger.warning("price_change_webhook: No data in payload")
            return jsonify({"status": "ok"}), 200
        
        # Procesar cada entidad en la notificación
        for entity in data_list:
            entity_normalized = normalize_ngsiv2_entity(entity)
            
            # Extraer información clave
            entity_id = entity_normalized.get("id", "")
            entity_type = entity_normalized.get("type", "")
            product_id = extract_entity_id_short(entity_id)
            new_price = entity_normalized.get("price")
            product_name = entity_normalized.get("name", "Unknown")
            
            logger.info(
                "Price change notification: product=%s (type=%s), new_price=%s",
                product_id, entity_type, new_price
            )
            
            # Construir evento SocketIO
            event_data = {
                "entity_id": entity_id,
                "product_id": product_id,
                "product_name": product_name,
                "new_price": new_price,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Emitir a clientes SocketIO conectados
            socketio = current_app.extensions["socketio"]
            socketio.emit("price_changed", event_data)
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        logger.error("Error in price_change_webhook: %s", e, exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@notifications_bp.post("/low-stock")
def low_stock_webhook():
    """
    Webhook de Orion para notificaciones de bajo stock de inventario.
    
    Procesa payload NGSIv2, normaliza y emite evento SocketIO a clientes conectados.
    """
    try:
        payload = request.get_json(silent=True) or {}
        
        # Orion envía: {"subscriptionId": "...", "data": [{...}]}
        data_list = payload.get("data", [])
        if not data_list:
            logger.warning("low_stock_webhook: No data in payload")
            return jsonify({"status": "ok"}), 200
        
        # Procesar cada entidad en la notificación
        for entity in data_list:
            entity_normalized = normalize_ngsiv2_entity(entity)
            
            # Extraer información clave
            entity_id = entity_normalized.get("id", "")
            entity_type = entity_normalized.get("type", "")
            inventory_id = extract_entity_id_short(entity_id)
            stock_count = entity_normalized.get("stockCount")
            shelf_count = entity_normalized.get("shelfCount")
            ref_store = entity_normalized.get("refStore", "")
            ref_product = entity_normalized.get("refProduct", "")
            ref_shelf = entity_normalized.get("refShelf", "")
            
            # Extraer IDs cortos de referencias
            store_id = extract_entity_id_short(ref_store) if ref_store else ""
            product_id = extract_entity_id_short(ref_product) if ref_product else ""
            shelf_id = extract_entity_id_short(ref_shelf) if ref_shelf else ""
            
            logger.info(
                "Low stock notification: inventory=%s (store=%s, product=%s), stock=%s",
                inventory_id, store_id, product_id, stock_count
            )
            
            # Construir evento SocketIO
            event_data = {
                "entity_id": entity_id,
                "inventory_id": inventory_id,
                "store_id": store_id,
                "product_id": product_id,
                "shelf_id": shelf_id,
                "stock_count": stock_count,
                "shelf_count": shelf_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Emitir a clientes SocketIO conectados
            socketio = current_app.extensions["socketio"]
            socketio.emit("low_stock", event_data)
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        logger.error("Error in low_stock_webhook: %s", e, exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
