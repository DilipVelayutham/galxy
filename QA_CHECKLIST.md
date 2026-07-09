# QA Checklist — GALXY Module 6 (Cart) Backend

This checklist summarizes the test verification scenarios and QA checkpoints for Module 6 (Cart).

## 1. Authentication & Security
- [x] Verify `@require_auth` decorator is applied to all cart routes.
- [x] Test requesting `/api/cart` (GET), `/api/cart/items` (POST, PUT, DELETE), and `/api/cart/clear` (DELETE) without any user credentials (must return HTTP `401 Unauthorized`).
- [x] Test requests with an invalid user ID format (must return HTTP `401 Unauthorized`).

## 2. API Routes & Status Codes
- [x] **GET `/api/cart`**:
  - [x] Returns status `200 OK` on success.
  - [x] Automatically creates an empty cart if one does not exist for the user (never returns `404`).
  - [x] Returns the correct root-level properties: `items`, `item_count`, and `subtotal_estimate`.
- [x] **POST `/api/cart/items`**:
  - [x] Returns status `201 Created` on successful add.
  - [x] Returns status `400 Bad Request` if selected attributes are invalid.
  - [x] Returns status `404 Not Found` if the product does not exist or is inactive.
- [x] **PUT `/api/cart/items/:item_id`**:
  - [x] Returns status `200 OK` on successful update.
  - [x] Returns status `400 Bad Request` if attributes selection or updated quantity is invalid.
  - [x] Returns status `404 Not Found` if the item is not in the user's cart.
- [x] **DELETE `/api/cart/items/:item_id`**:
  - [x] Returns status `200 OK` on successful removal.
  - [x] Returns status `404 Not Found` if the item is not found in the cart.
- [x] **DELETE `/api/cart/clear`**:
  - [x] Returns status `200 OK` on success and resets items to an empty array.

## 3. Core Cart Business Logic
- [x] **Product Snapshotting (`cart_snapshot_helper.py`)**:
  - [x] Snapshots the correct fields: `product_title`, `category_name`, and `thumbnail` at the exact time of adding to the cart.
  - [x] Ensure that snapshot fields are frozen on the cart document, avoiding live joins on cart retrieval.
- [x] **Pricing & Validation Delegation**:
  - [x] Delegates price calculations directly to Module 4's `calculate_price()`. Never trusts client-side prices.
  - [x] Delegates attribute validations to Module 4's `validate_attributes()`.
- [x] **Duplicate Item Merging**:
  - [x] On **POST** (Add Item): Merges duplicate items (same product ID, attributes, and custom text) by incrementing quantity.
  - [x] On **PUT** (Update Item): If updating an item makes it identical to another item, merges them together.
- [x] **Quantity Constraints**:
  - [x] Ensures quantity must be a positive integer (rejects `0`, negative values, or floats).

## 4. Stale-Item Graceful Degradation
- [x] **Inactive/Deleted Products**:
  - [x] Dynamically flags products as `"is_available": false` if they are soft-deleted or deactivated.
  - [x] Excludes unavailable items from the cart's `subtotal_estimate`.
- [x] **Modified Category Attribute Schemas**:
  - [x] Dynamically flags items as `"needs_attention": true` on GET if they fail silent validation against the current category schema.
  - [x] Returns specific validation error messages in the response payload.
  - [x] Ensures stale/invalid items are *never* auto-deleted or modified from the database, allowing users to resolve issues themselves.
- [x] Ensure stale flags are computed fresh at read-time (GET) and never persisted to the DB.

## 5. Integration Contracts
- [x] **Checkout Handoff**:
  - [x] Exposes `cart_service.get_or_create_cart(user_id)` as an importable method for Module 8 (Orders) to read the cart at checkout time.
  - [x] Exposes `cart_service.clear(user_id)` to empty the cart immediately after order creation.
