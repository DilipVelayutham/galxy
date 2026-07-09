import { NextRequest, NextResponse } from 'next/server';
import { updateItem, removeItem } from '../../store';

export async function PUT(
  req: NextRequest,
  { params }: { params: Promise<{ item_id: string }> }
) {
  try {
    const { item_id } = await params;
    const body = await req.json();
    const { quantity, selected_attributes, custom_text } = body;

    // Reject 0 or negative quantities
    if (quantity !== undefined && quantity <= 0) {
      return NextResponse.json(
        { success: false, message: 'Quantity must be a positive integer.' },
        { status: 400 }
      );
    }

    const updatedCart = updateItem(item_id, { quantity, selected_attributes, custom_text });

    if (!updatedCart) {
      return NextResponse.json(
        { success: false, message: 'Item not found in this cart.' },
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true, data: updatedCart.data });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Server error';
    return NextResponse.json(
      { success: false, message },
      { status: 500 }
    );
  }
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ item_id: string }> }
) {
  try {
    const { item_id } = await params;
    const updatedCart = removeItem(item_id);

    if (!updatedCart) {
      return NextResponse.json(
        { success: false, message: 'Item not found in this cart.' },
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true, message: 'Item removed', data: updatedCart.data });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Server error';
    return NextResponse.json(
      { success: false, message },
      { status: 500 }
    );
  }
}
