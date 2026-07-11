

export interface CartItem {
  _id: string;
  product_id: string;
  category_id: string;
  product_title: string;
  category_name: string;
  thumbnail: string;
  selected_attributes: Record<string, string | number | boolean>;
  quantity: number;
  unit_price_estimate: number;
  line_total_estimate: number;
  price_breakdown: Array<{ label: string; delta: number }>;
  ai_preview_image: string | null;
  custom_text: string | null;
  added_at: string;
  updated_at: string;
  // Stale state indicators computed at read time
  is_available: boolean;
  needs_attention: boolean;
  stale_reason?: string;
}

declare global {
  var mockCartStore: {
    items: CartItem[];
  };
}

if (!global.mockCartStore) {
  global.mockCartStore = {
    items: [
      {
        _id: "item_neon_1",
        product_id: "prod_neon_123",
        category_id: "cat_neon",
        product_title: "Custom Cursive Neon Sign",
        category_name: "Neon Boards",
        thumbnail: "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=200",
        selected_attributes: {
          font: "cursive",
          color: "Electric Pink",
          backing: "cut_to_shape",
          size: "medium"
        },
        quantity: 1,
        unit_price_estimate: 1799,
        line_total_estimate: 1799,
        price_breakdown: [
          { label: "Base Price", delta: 1200 },
          { label: "Cursive Font Option", delta: 150 },
          { label: "Medium Size Delta", delta: 449 }
        ],
        ai_preview_image: "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=600",
        custom_text: "Galxy Studio",
        added_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
        updated_at: new Date(Date.now() - 86400000).toISOString(),
        is_available: true,
        needs_attention: false
      },
      {
        _id: "item_moonlight_stale",
        product_id: "prod_moonlight_456",
        category_id: "cat_moonlight",
        product_title: "Acrylic Moonlight Lamp",
        category_name: "Moonlight Lamps",
        thumbnail: "https://images.unsplash.com/photo-1507508064433-641572e9c133?auto=format&fit=crop&q=80&w=200",
        selected_attributes: {
          size: "large",
          base: "wooden_lighted",
          engraving: "Moonlight Glow"
        },
        quantity: 1,
        unit_price_estimate: 2499,
        line_total_estimate: 2499,
        price_breakdown: [
          { label: "Base Price", delta: 1800 },
          { label: "Large Size Delta", delta: 699 }
        ],
        ai_preview_image: null,
        custom_text: "Happy Birthday",
        added_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
        updated_at: new Date(Date.now() - 172800000).toISOString(),
        // Simulating needs attention (e.g. base type is deprecated in newer schema)
        is_available: true,
        needs_attention: true,
        stale_reason: "Attribute selection 'wooden_lighted' for option 'base' is no longer supported in the current category schema. Please re-configure."
      },
      {
        _id: "item_magnet_deleted",
        product_id: "prod_magnet_789",
        category_id: "cat_magnets",
        product_title: "Vintage Acrylic Fridge Magnet",
        category_name: "Fridge Magnets",
        thumbnail: "https://images.unsplash.com/photo-1590076247563-7ee4f2150821?auto=format&fit=crop&q=80&w=200",
        selected_attributes: {
          shape: "square",
          finish: "glossy"
        },
        quantity: 2,
        unit_price_estimate: 350,
        line_total_estimate: 700,
        price_breakdown: [
          { label: "Base Price", delta: 350 }
        ],
        ai_preview_image: null,
        custom_text: "Family Photo",
        added_at: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
        updated_at: new Date(Date.now() - 259200000).toISOString(),
        // Simulating product no longer available (inactive / deleted)
        is_available: false,
        needs_attention: false,
        stale_reason: "This product is no longer available in our store catalog. Please remove it from your cart."
      }
    ]
  };
}

export const getCart = () => {
  const items = global.mockCartStore.items;
  const subtotal_estimate = items.reduce((acc, item) => acc + item.line_total_estimate, 0);
  const item_count = items.reduce((acc, item) => acc + item.quantity, 0);
  
  return {
    success: true,
    data: {
      items,
      item_count,
      subtotal_estimate
    }
  };
};

export const addItem = (newItem: Omit<CartItem, '_id' | 'added_at' | 'updated_at' | 'is_available' | 'needs_attention' | 'line_total_estimate' | 'price_breakdown' | 'unit_price_estimate' | 'product_title' | 'category_name' | 'thumbnail'>) => {
  // Check duplicates rule: same product_id AND same selected_attributes AND same custom_text
  const isDuplicate = (item: CartItem) => {
    if (item.product_id !== newItem.product_id) return false;
    if (item.custom_text !== newItem.custom_text) return false;
    
    // Compare selected attributes
    const keys1 = Object.keys(item.selected_attributes);
    const keys2 = Object.keys(newItem.selected_attributes);
    if (keys1.length !== keys2.length) return false;
    for (const key of keys1) {
      if (item.selected_attributes[key] !== newItem.selected_attributes[key]) return false;
    }
    return true;
  };

  const existingItemIndex = global.mockCartStore.items.findIndex(isDuplicate);

  if (existingItemIndex > -1) {
    // Increment quantity
    global.mockCartStore.items[existingItemIndex].quantity += newItem.quantity;
    global.mockCartStore.items[existingItemIndex].line_total_estimate = 
      global.mockCartStore.items[existingItemIndex].unit_price_estimate * global.mockCartStore.items[existingItemIndex].quantity;
    global.mockCartStore.items[existingItemIndex].updated_at = new Date().toISOString();
  } else {
    // Generate snapshot variables based on product_id
    let product_title = "Custom Quilling Frame";
    let category_name = "Quilling Art";
    let thumbnail = "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&q=80&w=200";
    let base_price = 1500;
    
    if (newItem.product_id === 'prod_neon_123') {
      product_title = "Custom Cursive Neon Sign";
      category_name = "Neon Boards";
      thumbnail = "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=200";
      base_price = 1200;
    } else if (newItem.product_id === 'prod_moonlight_456') {
      product_title = "Acrylic Moonlight Lamp";
      category_name = "Moonlight Lamps";
      thumbnail = "https://images.unsplash.com/photo-1507508064433-641572e9c133?auto=format&fit=crop&q=80&w=200";
      base_price = 1800;
    }

    // Compute price deltas based on selected_attributes
    const price_breakdown = [{ label: "Base Price", delta: base_price }];
    let attribute_delta_sum = 0;

    Object.entries(newItem.selected_attributes).forEach(([key, val]) => {
      // Simulate some price deltas for selected options
      if (val === 'cursive' || val === 'gold' || val === 'large' || val === 'wooden_lighted') {
        const delta = val === 'large' ? 699 : val === 'wooden_lighted' ? 299 : 150;
        price_breakdown.push({ label: `Option ${String(key)}: ${String(val)}`, delta });
        attribute_delta_sum += delta;
      }
    });

    const unit_price_estimate = base_price + attribute_delta_sum;
    const line_total_estimate = unit_price_estimate * newItem.quantity;

    const createdItem: CartItem = {
      _id: 'item_' + Math.random().toString(36).substr(2, 9),
      product_id: newItem.product_id,
      category_id: newItem.category_id || 'cat_custom',
      product_title,
      category_name,
      thumbnail,
      selected_attributes: newItem.selected_attributes,
      quantity: newItem.quantity,
      unit_price_estimate,
      line_total_estimate,
      price_breakdown,
      ai_preview_image: newItem.ai_preview_image || null,
      custom_text: newItem.custom_text || null,
      added_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_available: true,
      needs_attention: false
    };

    global.mockCartStore.items.push(createdItem);
  }

  return getCart();
};

export const updateItem = (itemId: string, updates: { quantity?: number; selected_attributes?: Record<string, string | number | boolean>; custom_text?: string | null }) => {
  const itemIndex = global.mockCartStore.items.findIndex(item => item._id === itemId);
  if (itemIndex === -1) return null;

  const item = global.mockCartStore.items[itemIndex];

  if (updates.quantity !== undefined) {
    if (updates.quantity <= 0) return null; // must use delete
    item.quantity = updates.quantity;
  }

  if (updates.selected_attributes !== undefined) {
    item.selected_attributes = updates.selected_attributes;
    // Re-validate / re-price in mock
    const base_price = item.product_title.includes("Neon") ? 1200 : 1500;
    const price_breakdown = [{ label: "Base Price", delta: base_price }];
    let attribute_delta_sum = 0;

    Object.entries(item.selected_attributes).forEach(([key, val]) => {
      if (val === 'cursive' || val === 'gold' || val === 'large' || val === 'wooden_lighted') {
        const delta = val === 'large' ? 699 : val === 'wooden_lighted' ? 299 : 150;
        price_breakdown.push({ label: `Option ${String(key)}: ${String(val)}`, delta });
        attribute_delta_sum += delta;
      }
    });

    item.unit_price_estimate = base_price + attribute_delta_sum;
    item.price_breakdown = price_breakdown;
    // Resolve needs_attention if they edited it
    item.needs_attention = false;
    item.stale_reason = undefined;
  }

  if (updates.custom_text !== undefined) {
    item.custom_text = updates.custom_text;
  }

  item.line_total_estimate = item.unit_price_estimate * item.quantity;
  item.updated_at = new Date().toISOString();

  return getCart();
};

export const removeItem = (itemId: string) => {
  const initialLen = global.mockCartStore.items.length;
  global.mockCartStore.items = global.mockCartStore.items.filter(item => item._id !== itemId);
  return global.mockCartStore.items.length !== initialLen ? getCart() : null;
};

export const clearCart = () => {
  global.mockCartStore.items = [];
  return getCart();
};
