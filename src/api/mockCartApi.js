// Mock API client for GALXY Module 6: Cart
// Replicates GET /api/cart, PUT /api/cart/items/:item_id, DELETE /api/cart/items/:item_id, and DELETE /api/cart/clear

// Standard product definitions and attributes for reference/visuals
const INITIAL_CART_ITEMS = [
  {
    _id: "cart_item_01",
    product_id: "prod_supernova",
    product_title: "Supernova Pendant Light",
    category_name: "Pendant Lights",
    thumbnail: "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=150&auto=format&fit=crop&q=80",
    selected_attributes: [
      { name: "Size", value: "Large (24\")", price_modifier: 50 },
      { name: "Finish", value: "Brushed Brass", price_modifier: 30 },
      { name: "Bulb Type", value: "Edison LED (Warm)", price_modifier: 10 }
    ],
    custom_text: "Hang exactly 7ft above the dining table surface.",
    base_price: 450,
    unit_price_estimate: 540,
    line_total_estimate: 1080,
    quantity: 2,
    is_available: true,
    needs_attention: false,
    error_message: ""
  },
  {
    _id: "cart_item_02",
    product_id: "prod_nebula",
    product_title: "Nebula Desk Lamp",
    category_name: "Table Lamps",
    thumbnail: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=150&auto=format&fit=crop&q=80",
    selected_attributes: [
      { name: "Size", value: "Standard", price_modifier: 0 },
      { name: "Shade", value: "Smoked Glass", price_modifier: 25 },
      { name: "Cord", value: "Black Fabric Braided", price_modifier: 5 }
    ],
    custom_text: null,
    base_price: 180,
    unit_price_estimate: 210,
    line_total_estimate: 210,
    quantity: 1,
    is_available: true,
    needs_attention: false,
    error_message: ""
  },
  {
    _id: "cart_item_03",
    product_id: "prod_comet",
    product_title: "Comet Sconce",
    category_name: "Wall Lights",
    thumbnail: "https://images.unsplash.com/photo-1517999144091-3d9dca6d1e43?w=150&auto=format&fit=crop&q=80",
    selected_attributes: [
      { name: "Finish", value: "Matte Black", price_modifier: 0 },
      { name: "Temperature", value: "Warm White (3000K)", price_modifier: 0 }
    ],
    custom_text: "For master bedroom accent wall.",
    base_price: 125,
    unit_price_estimate: 125,
    line_total_estimate: 125,
    quantity: 1,
    is_available: true,
    needs_attention: false,
    error_message: ""
  }
];

// Helper to load or initialize database in localStorage
function getDB() {
  const data = localStorage.getItem("galxy_cart_db");
  if (!data) {
    const db = {
      items: JSON.parse(JSON.stringify(INITIAL_CART_ITEMS)),
      latency: 400, // ms
      staleStates: {
        // Maps cart_item_id to stale options
      }
    };
    saveDB(db);
    return db;
  }
  return JSON.parse(data);
}

function saveDB(db) {
  localStorage.setItem("galxy_cart_db", JSON.stringify(db));
}

// Calculate totals using DB rules exactly
function calculateCartTotals(db) {
  let itemCount = 0;
  let subtotalEstimate = 0;

  db.items.forEach(item => {
    // Look up dynamic stale configurations
    const staleConfig = db.staleStates[item._id] || {};
    item.is_available = staleConfig.is_available !== undefined ? staleConfig.is_available : true;
    item.needs_attention = staleConfig.needs_attention !== undefined ? staleConfig.needs_attention : false;
    item.error_message = staleConfig.error_message || "";

    // Calculate line total if available
    item.line_total_estimate = item.unit_price_estimate * item.quantity;
    
    if (item.is_available) {
      itemCount += item.quantity;
      subtotalEstimate += item.line_total_estimate;
    }
  });

  return {
    items: db.items,
    item_count: itemCount,
    subtotal_estimate: subtotalEstimate
  };
}

// Wait helper
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const mockCartApi = {
  // GET /api/cart
  async getCart() {
    const db = getDB();
    await delay(db.latency);
    return {
      success: true,
      message: "Cart retrieved successfully",
      data: calculateCartTotals(db)
    };
  },

  // PUT /api/cart/items/:item_id
  async updateItemQuantity(itemId, quantity) {
    const db = getDB();
    await delay(db.latency);
    
    const item = db.items.find(i => i._id === itemId);
    if (!item) {
      throw new Error(`Item ${itemId} not found in cart`);
    }

    if (quantity <= 0) {
      db.items = db.items.filter(i => i._id !== itemId);
    } else {
      item.quantity = quantity;
    }

    saveDB(db);
    return {
      success: true,
      message: "Item quantity updated successfully",
      data: calculateCartTotals(db)
    };
  },

  // DELETE /api/cart/items/:item_id
  async removeItem(itemId) {
    const db = getDB();
    await delay(db.latency);

    db.items = db.items.filter(i => i._id !== itemId);
    saveDB(db);
    
    return {
      success: true,
      message: "Item removed from cart successfully",
      data: calculateCartTotals(db)
    };
  },

  // DELETE /api/cart/clear
  async clearCart() {
    const db = getDB();
    await delay(db.latency);

    db.items = [];
    saveDB(db);

    return {
      success: true,
      message: "Cart cleared successfully",
      data: calculateCartTotals(db)
    };
  },

  // PUT /api/cart/items/:item_id/configuration (simulated endpoint)
  async updateItemConfiguration(itemId, selectedAttributes, unitPrice) {
    const db = getDB();
    await delay(db.latency);
    
    const item = db.items.find(i => i._id === itemId);
    if (item) {
      item.selected_attributes = selectedAttributes;
      item.unit_price_estimate = unitPrice;
      
      // Clear warnings
      if (db.staleStates[itemId]) {
        db.staleStates[itemId].needs_attention = false;
        db.staleStates[itemId].error_message = '';
      }
    }
    
    saveDB(db);
    return {
      success: true,
      message: "Item configuration updated successfully",
      data: calculateCartTotals(db)
    };
  },

  // Developer control options
  setLatency(ms) {
    const db = getDB();
    db.latency = ms;
    saveDB(db);
    return ms;
  },

  getLatency() {
    return getDB().latency;
  },

  setStaleState(itemId, { is_available, needs_attention, error_message }) {
    const db = getDB();
    db.staleStates[itemId] = {
      is_available,
      needs_attention,
      error_message
    };
    saveDB(db);
    return {
      success: true,
      message: "Stale state configured successfully",
      data: calculateCartTotals(db)
    };
  },

  getStaleStates() {
    return getDB().staleStates;
  },

  resetCart() {
    const db = getDB();
    db.items = JSON.parse(JSON.stringify(INITIAL_CART_ITEMS));
    db.staleStates = {};
    saveDB(db);
    return {
      success: true,
      message: "Cart reset successfully",
      data: calculateCartTotals(db)
    };
  },

  // Add dummy item for demo purposes
  async addDemoItem(product) {
    const db = getDB();
    await delay(db.latency);

    // Check if item with same configuration already exists
    const match = db.items.find(i => 
      i.product_id === product.product_id && 
      JSON.stringify(i.selected_attributes) === JSON.stringify(product.selected_attributes) &&
      i.custom_text === product.custom_text
    );

    if (match) {
      match.quantity += 1;
    } else {
      const uniqueSuffix = Math.random().toString(36).substring(2, 11);
      const newId = `cart_item_${Date.now()}_${uniqueSuffix}`;
      db.items.push({
        _id: newId,
        ...product,
        base_price: product.base_price || 450,
        unit_price_estimate: product.unit_price_estimate,
        line_total_estimate: product.unit_price_estimate,
        quantity: 1,
        is_available: true,
        needs_attention: false,
        error_message: ""
      });
    }

    saveDB(db);
    return {
      success: true,
      message: "Product added to cart successfully",
      data: calculateCartTotals(db)
    };
  }
};
