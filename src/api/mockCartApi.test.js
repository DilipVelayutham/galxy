import { describe, it, expect, beforeEach } from 'vitest';
import { mockCartApi } from './mockCartApi';

// Replicate localStorage in Node runtime environment
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = String(value); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

// eslint-disable-next-line no-undef
global.localStorage = localStorageMock;

describe('mockCartApi Unit Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    mockCartApi.resetCart();
  });

  it('GET /api/cart - retrieves cart with correct envelope and totals', async () => {
    const res = await mockCartApi.getCart();
    expect(res.success).toBe(true);
    expect(res.message).toBe("Cart retrieved successfully");
    expect(res.data.items).toHaveLength(3);
    expect(res.data.item_count).toBe(4);
    expect(res.data.subtotal_estimate).toBe(1415); // Supernova ($540*2) + Nebula ($210*1) + Comet ($125*1) = $1415
  });

  it('PUT /api/cart/items/:id - updates quantities and line price estimates', async () => {
    // Increase quantity from 2 to 3 for Supernova (unit price $540)
    const res = await mockCartApi.updateItemQuantity('cart_item_01', 3);
    expect(res.success).toBe(true);
    
    const item = res.data.items.find(i => i._id === 'cart_item_01');
    expect(item.quantity).toBe(3);
    expect(item.line_total_estimate).toBe(1620); // $540 * 3
    expect(res.data.item_count).toBe(5); // 3 + 1 + 1
    expect(res.data.subtotal_estimate).toBe(1955); // 1620 + 210 + 125 = 1955
  });

  it('DELETE /api/cart/items/:id - removes targeted item', async () => {
    const res = await mockCartApi.removeItem('cart_item_01');
    expect(res.success).toBe(true);
    expect(res.data.items.find(i => i._id === 'cart_item_01')).toBeUndefined();
    expect(res.data.item_count).toBe(2); // Nebula (1) + Comet (1)
  });

  it('DELETE /api/cart/clear - clears items array', async () => {
    const res = await mockCartApi.clearCart();
    expect(res.success).toBe(true);
    expect(res.data.items).toHaveLength(0);
    expect(res.data.item_count).toBe(0);
    expect(res.data.subtotal_estimate).toBe(0);
  });

  it('Stale States - excludes unavailable items from subtotal estimate and item count', async () => {
    // Mark Supernova (cart_item_01) as sold out
    mockCartApi.setStaleState('cart_item_01', { 
      is_available: false, 
      needs_attention: false, 
      error_message: '' 
    });

    const res = await mockCartApi.getCart();
    const item = res.data.items.find(i => i._id === 'cart_item_01');
    expect(item.is_available).toBe(false);
    
    // Subtotal should exclude Supernova ($1080)
    // Subtotal = Nebula ($210) + Comet ($125) = $335
    expect(res.data.subtotal_estimate).toBe(335);
    // Item count should also exclude unavailable items (4 - 2 = 2)
    expect(res.data.item_count).toBe(2);
  });

  it('Stale States - handles needs_attention warnings and error messages', async () => {
    const errMsg = "Alternative finish selected.";
    mockCartApi.setStaleState('cart_item_01', { 
      is_available: true, 
      needs_attention: true, 
      error_message: errMsg 
    });

    const res = await mockCartApi.getCart();
    const item = res.data.items.find(i => i._id === 'cart_item_01');
    expect(item.needs_attention).toBe(true);
    expect(item.error_message).toBe(errMsg);
  });

  it('PUT /api/cart/items/:id/configuration - updates configurations and clears stale flags', async () => {
    // 1. Trigger stale state warning first
    mockCartApi.setStaleState('cart_item_01', { 
      is_available: true, 
      needs_attention: true, 
      error_message: 'Brushed Brass finish is currently unavailable.' 
    });

    const updatedAttrs = [
      { name: "Size", value: "Large (24\")", price_modifier: 50 },
      { name: "Finish", value: "Matte Black", price_modifier: 0 },
      { name: "Bulb Type", value: "Edison LED (Warm)", price_modifier: 10 }
    ];
    // Base 450 + modifiers 60 = 510
    const newPrice = 510;

    const res = await mockCartApi.updateItemConfiguration('cart_item_01', updatedAttrs, newPrice);
    expect(res.success).toBe(true);

    const item = res.data.items.find(i => i._id === 'cart_item_01');
    expect(item.selected_attributes.find(a => a.name === 'Finish').value).toBe('Matte Black');
    expect(item.unit_price_estimate).toBe(510);
    expect(item.needs_attention).toBe(false); // warning cleared
  });
});
