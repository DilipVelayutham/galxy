import { render, screen, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { CartProvider, useCart } from './CartContext';
import { mockCartApi } from '../api/mockCartApi';

// Mock localStorage for node environment
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

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Consumer component to expose CartContext values for assertions
function TestConsumer() {
  const { cart, updateQuantity, removeItem, loading } = useCart();
  if (loading) {
    return <div data-testid="loading">Loading...</div>;
  }
  return (
    <div>
      <div data-testid="item-count">{cart.item_count}</div>
      <div data-testid="subtotal">{cart.subtotal_estimate}</div>
      {cart.items.map(item => (
        <div key={item._id} data-testid={`item-${item._id}`}>
          <span data-testid={`qty-${item._id}`}>{item.quantity}</span>
          <button data-testid={`btn-inc-${item._id}`} onClick={() => updateQuantity(item._id, item.quantity + 1)}>Inc</button>
          <button data-testid={`btn-rm-${item._id}`} onClick={() => removeItem(item._id)}>Remove</button>
        </div>
      ))}
    </div>
  );
}

describe('CartContext Unit and Integration Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    mockCartApi.resetCart();
    mockCartApi.setLatency(0); // Eliminate latency to avoid async race conditions
    vi.restoreAllMocks();
  });

  it('provides initial cart state after loading', async () => {
    render(
      <CartProvider>
        <TestConsumer />
      </CartProvider>
    );

    // Wait for the cart to load
    const itemCount = await screen.findByTestId('item-count');
    expect(itemCount.textContent).toBe('4');
    expect(screen.getByTestId('subtotal').textContent).toBe('1415');
  });

  it('handles quantity updates with optimistic rendering and 500ms debounce', async () => {
    // Spy on mockCartApi to verify api calls
    const updateSpy = vi.spyOn(mockCartApi, 'updateItemQuantity');

    render(
      <CartProvider>
        <TestConsumer />
      </CartProvider>
    );

    // Wait for initial load
    const qtySpan = await screen.findByTestId('qty-cart_item_01');
    expect(qtySpan.textContent).toBe('2');

    const incButton = screen.getByTestId('btn-inc-cart_item_01');

    // Click increment button (qty changes: 2 -> 3)
    await act(async () => {
      incButton.click();
    });

    // Optimistic update should be immediate in UI before API returns
    expect(qtySpan.textContent).toBe('3');
    // Subtotal should update immediately: Supernova ($540*2 -> $540*3 = +$540)
    // 1415 + 540 = 1955
    expect(screen.getByTestId('subtotal').textContent).toBe('1955');
    expect(updateSpy).not.toHaveBeenCalled();

    // Click increment again immediately (qty changes: 3 -> 4)
    await act(async () => {
      incButton.click();
    });

    expect(qtySpan.textContent).toBe('4');
    expect(screen.getByTestId('subtotal').textContent).toBe('2495'); // 1955 + 540
    expect(updateSpy).not.toHaveBeenCalled();

    // Wait 600ms to trigger the debounced API request
    await act(async () => {
      await sleep(650);
    });

    // API should be called exactly once with the final quantity (4)
    expect(updateSpy).toHaveBeenCalledTimes(1);
    expect(updateSpy).toHaveBeenCalledWith('cart_item_01', 4);
  });

  it('performs automatic state rollback if API update fails', async () => {
    // Force API to reject/fail on next call
    const updateSpy = vi.spyOn(mockCartApi, 'updateItemQuantity').mockRejectedValueOnce(new Error("Network Error"));

    render(
      <CartProvider>
        <TestConsumer />
      </CartProvider>
    );

    // Wait for initial load
    const qtySpan = await screen.findByTestId('qty-cart_item_01');
    expect(qtySpan.textContent).toBe('2');

    const incButton = screen.getByTestId('btn-inc-cart_item_01');

    // Optimistic increment
    await act(async () => {
      incButton.click();
    });
    expect(qtySpan.textContent).toBe('3');

    // Wait for debounce and error rollback
    await act(async () => {
      await sleep(650);
    });

    expect(updateSpy).toHaveBeenCalledTimes(1);
    
    // After API fails, it should rollback quantity to 2
    await waitFor(() => {
      expect(qtySpan.textContent).toBe('2');
      expect(screen.getByTestId('subtotal').textContent).toBe('1415');
    });
  });
});
