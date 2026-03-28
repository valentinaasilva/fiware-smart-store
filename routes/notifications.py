from flask import Blueprint, current_app, jsonify, request

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.post("/price-change")
def price_change_webhook():
    payload = request.get_json(silent=True) or {}
    socketio = current_app.extensions["socketio"]
    socketio.emit("product_price_changed", payload)
    return jsonify({"status": "ok"})


@notifications_bp.post("/low-stock")
def low_stock_webhook():
    payload = request.get_json(silent=True) or {}
    socketio = current_app.extensions["socketio"]
    socketio.emit("inventory_low_stock", payload)
    return jsonify({"status": "ok"})
