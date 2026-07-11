import { NextRequest, NextResponse } from 'next/server';
import { addItem } from '../store';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { product_id, selected_attributes, quantity, custom_text, ai_preview_image } = body;

    // Validation for testing 404
    if (product_id === 'trigger_404_inactive') {
      return NextResponse.json(
        { success: false, message: 'This product is no longer available or has been deactivated.' },
        { status: 404 }
      );
    }

    // Validation for testing 400
    if (selected_attributes && Object.values(selected_attributes).includes('trigger_invalid_attribute')) {
      return NextResponse.json(
        {
          success: false,
          message: 'Invalid configuration choices.',
          errors: {
            font: 'Selected font is deprecated and cannot be used.',
            color: 'Selected color is out of stock.'
          }
        },
        { status: 400 }
      );
    }

    if (!product_id) {
      return NextResponse.json(
        { success: false, message: 'Missing product_id parameter.' },
        { status: 400 }
      );
    }

    // Reject 0 or negative quantities
    if (quantity !== undefined && quantity <= 0) {
      return NextResponse.json(
        { success: false, message: 'Quantity must be a positive integer.' },
        { status: 400 }
      );
    }

    // Add item to store
    const updatedCart = addItem({
      product_id,
      category_id: body.category_id || 'cat_custom',
      selected_attributes: selected_attributes || {},
      quantity: typeof quantity === 'number' ? quantity : 1,
      custom_text: custom_text || null,
      ai_preview_image: ai_preview_image || null
    });

    return NextResponse.json(
      { success: true, message: 'Added to cart', data: updatedCart.data },
      { status: 201 }
    );
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Server error';
    return NextResponse.json(
      { success: false, message },
      { status: 500 }
    );
  }
}
