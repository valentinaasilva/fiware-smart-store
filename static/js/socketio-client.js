/**
 * Cliente SocketIO para notificaciones en tiempo real
 * 
 * Conecta al servidor Flask-SocketIO y escucha eventos:
 * - "price_changed": Cambio de precio de producto
 * - "low_stock": Bajo stock de inventario
 * 
 * Actualiza dinámicamente el DOM sin necesidad de reload.
 */

// Inicializar conexión SocketIO (detecta servidor automáticamente)
const socket = io();

// ============================================================================
// Event Listeners: Conexión/Desconexión
// ============================================================================

socket.on("connect", () => {
  console.log("✅ Cliente conectado al servidor SocketIO");
  console.log("Socket ID:", socket.id);
});

socket.on("disconnect", () => {
  console.log("❌ Cliente desconectado del servidor SocketIO");
});

socket.on("connect_error", (error) => {
  console.error("❌ Error de conexión SocketIO:", error);
});

// ============================================================================
// Event Listeners: Cambio de Precio (Product)
// ============================================================================

socket.on("price_changed", (eventData) => {
  console.log("📊 Evento: Cambio de precio", eventData);
  
  const { product_id, product_name, new_price, timestamp } = eventData;
  
  if (!product_id || new_price === undefined) {
    console.warn("⚠️ Datos incompletos en evento price_changed:", eventData);
    return;
  }
  
  // Buscar elemento en la tabla que corresponde a este producto
  const productRows = document.querySelectorAll(`[data-product-id="${product_id}"]`);
  
  if (productRows.length === 0) {
    console.warn(`⚠️ No se encontró elemento con data-product-id="${product_id}"`);
    return;
  }
  
  productRows.forEach((row) => {
    // Buscar la celda de precio dentro de esta fila
    const priceCell = row.querySelector(".product-price");
    
    if (priceCell) {
      const oldPrice = priceCell.textContent;
      
      // Actualizar precio
      priceCell.textContent = new_price.toFixed(2);
      
      // Aplicar animación de resaltado
      applyHighlightFlash(priceCell);
      
      console.log(`💰 Producto: ${product_name} (${product_id})`);
      console.log(`   Precio anterior: ${oldPrice}`);
      console.log(`   Precio nuevo: ${new_price.toFixed(2)}`);
      console.log(`   Cambio registrado a las: ${new Date(timestamp).toLocaleTimeString()}`);
    }
  });
});

// ============================================================================
// Event Listeners: Bajo Stock (InventoryItem)
// ============================================================================

socket.on("low_stock", (eventData) => {
  console.log("📦 Evento: Bajo stock", eventData);
  
  const { inventory_id, store_id, product_id, stock_count, timestamp } = eventData;
  
  if (!inventory_id || stock_count === undefined) {
    console.warn("⚠️ Datos incompletos en evento low_stock:", eventData);
    return;
  }
  
  // Buscar elemento en la tabla que corresponde a este inventario
  const inventoryRows = document.querySelectorAll(`[data-inventory-id="${inventory_id}"]`);
  
  if (inventoryRows.length === 0) {
    console.warn(`⚠️ No se encontró elemento con data-inventory-id="${inventory_id}"`);
    return;
  }
  
  const stockThreshold = 5; // Umbral de bajo stock
  
  inventoryRows.forEach((row) => {
    // Buscar la celda de stock dentro de esta fila
    const stockCell = row.querySelector(".stock-count");
    
    if (stockCell) {
      const oldStock = stockCell.textContent;
      
      // Actualizar stock
      stockCell.textContent = stock_count;
      
      // Aplicar animación de resaltado
      applyHighlightFlash(stockCell);
      
      // Si el stock está bajo, agregar clase de alerta
      if (stock_count < stockThreshold) {
        row.classList.add("alert-low-stock");
        console.warn(`⚠️ ¡BAJO STOCK! Producto: ${product_id} (Tienda: ${store_id})`);
      } else {
        // Si está bien, remover la clase de alerta
        row.classList.remove("alert-low-stock");
      }
      
      console.log(`📊 Inventario: ${inventory_id}`);
      console.log(`   Tienda: ${store_id}`);
      console.log(`   Producto: ${product_id}`);
      console.log(`   Stock anterior: ${oldStock}`);
      console.log(`   Stock nuevo: ${stock_count}`);
      console.log(`   Cambio registrado a las: ${new Date(timestamp).toLocaleTimeString()}`);
    }
  });
});

// ============================================================================
// Funciones Auxiliares
// ============================================================================

/**
 * Aplica animación de resaltado ("flash") a un elemento
 * 
 * @param {HTMLElement} element - Elemento a resaltar
 * @param {string} className - Clase CSS a aplicar (default: 'highlight-flash')
 * @param {number} durationMs - Duración de la animación en ms (default: 2000)
 */
function applyHighlightFlash(element, className = "highlight-flash") {
  if (!element) return;
  
  // Agregar clase
  element.classList.add(className);
  
  // Remover clase después de que termine la animación
  element.addEventListener('animationend', function removeHighlight() {
    element.classList.remove(className);
  }, { once: true });
}

// ============================================================================
// Debugging: Información del cliente
// ============================================================================

// Información disponible en consola para debugging
window.SocketIODebug = {
  socket: socket,
  getConnectionStatus: () => ({
    connected: socket.connected,
    id: socket.id,
    url: socket.io.uri,
  }),
  
  listenerCount: () => ({
    "price_changed": socket.listeners("price_changed").length,
    "low_stock": socket.listeners("low_stock").length,
  }),
  
  // Simular evento de prueba (solo para desarrollo)
  simulatePrice: (productId = "PROD-001", newPrice = 29.99) => {
    console.log("🧪 Simulando evento price_changed...");
    socket.emit("price_changed", {
      product_id: productId,
      product_name: "Producto Test",
      new_price: newPrice,
      timestamp: new Date().toISOString(),
    });
  },
  
  simulateLowStock: (inventoryId = "INV-001", stockCount = 2) => {
    console.log("🧪 Simulando evento low_stock...");
    socket.emit("low_stock", {
      inventory_id: inventoryId,
      store_id: "STORE-001",
      product_id: "PROD-001",
      stock_count: stockCount,
      timestamp: new Date().toISOString(),
    });
  },
};

console.log("🔧 SocketIO Debug tools disponibles en: window.SocketIODebug");
console.log("   - getConnectionStatus()");
console.log("   - listenerCount()");
console.log("   - simulatePrice(productId, newPrice)");
console.log("   - simulateLowStock(inventoryId, stockCount)");
