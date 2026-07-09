import { NextResponse } from 'next/server';
import { clearCart } from '../store';

export async function DELETE() {
  const updatedCart = clearCart();
  return NextResponse.json({ success: true, message: 'Cart cleared', data: updatedCart.data });
}
