import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CartItemRow from './CartItemRow';
import CartPage from './CartPage';
import { CartProvider } from '../context/CartContext';
import { mockCartApi } from '../api/mockCartApi';

// Mock localStorage
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

describe('Cart Components Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    mockCartApi.resetCart();
    mockCartApi.setLatency(0); // Eliminate latency for fast and robust component tests
  });

  it('CartItemRow renders item details and triggers interaction handlers', () => {
    const mockItem = {
      _id: 'item_123',
      product_id: 'prod_supernova',
      product_title: 'Supernova Pendant Light',
      category_name: 'Pendant Lights',
      thumbnail: 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15',
      selected_attributes: [{ name: 'Finish', value: 'Brushed Brass', price_modifier: 30 }],
      custom_text: 'Special text request',
      quantity: 2,
      unit_price_estimate: 480,
      line_total_estimate: 960,
      is_available: true,
      needs_attention: false
    };

    const updateQtySpy = vi.fn();
    const removeSpy = vi.fn();
    const fixSpy = vi.fn();

    render(
      <CartItemRow
        item={mockItem}
        isMutating={false}
        onUpdateQty={updateQtySpy}
        onRemove={removeSpy}
        onFixSelection={fixSpy}
      />
    );

    expect(screen.getByText('Supernova Pendant Light')).toBeDefined();
    expect(screen.getByText('$480')).toBeDefined();
    expect(screen.getByText('$960')).toBeDefined();
    expect(screen.getByText(/"Special text request"/)).toBeDefined();

    // Trigger increment
    const incButton = screen.getByLabelText('Increase quantity');
    fireEvent.click(incButton);
    expect(updateQtySpy).toHaveBeenCalledWith('item_123', 3);

    // Trigger remove
    const removeButton = screen.getByTitle('Remove item');
    fireEvent.click(removeButton);
    expect(removeSpy).toHaveBeenCalledWith('item_123');
  });

  it('CartPage displays Fix Selection modal with proper accessibility tags and handles option correction', async () => {
    // Seed stale state so that CartPage renders the 'Fix' button
    mockCartApi.setStaleState('cart_item_01', {
      is_available: true,
      needs_attention: true,
      error_message: 'Brushed Brass finish is currently unavailable.'
    });

    render(
      <CartProvider>
        <CartPage onBackToShop={vi.fn()} />
      </CartProvider>
    );

    // Wait for the cart items to load
    const fixButton = await screen.findByRole('button', { name: /Fix/i });
    expect(fixButton).toBeDefined();

    // Click 'Fix' to open the modal
    fireEvent.click(fixButton);

    // Check accessibility tags on the modal content
    const modal = await screen.findByRole('dialog');
    expect(modal).toBeDefined();
    expect(modal.getAttribute('aria-modal')).toBe('true');
    expect(modal.getAttribute('aria-labelledby')).toBe('fix-modal-title');
    expect(modal.getAttribute('aria-describedby')).toBe('fix-modal-desc');

    // Check that we can select another option (Matte Black is available)
    const matteBlackBtn = screen.getByRole('button', { name: /Matte Black/i });
    expect(matteBlackBtn).toBeDefined();
    fireEvent.click(matteBlackBtn);

    // Click Apply Correction
    const applyBtn = screen.getByRole('button', { name: /Apply Correction/i });
    fireEvent.click(applyBtn);

    // Modal should close after correction is applied
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).toBeNull();
    });
  });

  it('CartPage Fix Selection modal can be closed via the Escape key', async () => {
    mockCartApi.setStaleState('cart_item_01', {
      is_available: true,
      needs_attention: true,
      error_message: 'Brushed Brass finish is currently unavailable.'
    });

    render(
      <CartProvider>
        <CartPage onBackToShop={vi.fn()} />
      </CartProvider>
    );

    const fixButton = await screen.findByRole('button', { name: /Fix/i });
    fireEvent.click(fixButton);

    const modal = await screen.findByRole('dialog');
    expect(modal).toBeDefined();

    // Press Escape key
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });

    // Modal should close
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).toBeNull();
    });
  });
});
