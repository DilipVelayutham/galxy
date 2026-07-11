import { NextResponse } from 'next/server';
import { getCart } from './store';

export async function GET() {
  const cart = getCart();
  return NextResponse.json(cart);
}
