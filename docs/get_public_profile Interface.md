# Public Profile Exposure Interface (`get_public_profile`)

This document describes the design, security properties, and usage of the public-facing user profile exposure function (`get_public_profile`). This function is a frozen contract intended for consumption by external modules (such as Orders, Reviews, and Wishlists) that need to look up customer display information.

---

## Technical Details

* **Function Location**: `backend/app/services/user_service.py`
* **Signature**: `get_public_profile(user_id)`
* **Parameters**:
  * `user_id` (string or BSON `ObjectId`): The identifier of the user to look up.
* **Return Value**:
  * A dictionary containing safe, public profile information, or `None` if the user is not found.

---

## Security Guidelines (Sensitive Data Sanitization)

This function guarantees that **no sensitive credentials or internal flags are ever returned**. The underlying implementation sanitizes fields before returning them:
* `password_hash` is explicitly popped/removed.
* Admin privileges, tokens, and internal state trackers are excluded.

---

## Data Structure

The returned dictionary follows this exact shape:

```json
{
  "_id": "6a479e45c779c8aa0c395f46",
  "name": "Test User",
  "email": "test@galxy.com",
  "phone": "9876543210",
  "addresses": [
    {
      "_id": "7b589e45c779c8aa0c395f99",
      "label": "Home",
      "line1": "123 Main St",
      "line2": "Apartment 4B",
      "city": "Chennai",
      "state": "Tamil Nadu",
      "pincode": "600001",
      "is_default": true
    }
  ],
  "auth_provider": "email",
  "is_verified": false,
  "is_active": true,
  "created_at": "2026-07-03T11:32:55.334000",
  "updated_at": "2026-07-03T11:32:55.334000"
}
```

---

## Consumer Usage Examples

Dependent modules (such as **Module 8: Orders** for building order customer snapshots, and **Module 9: Reviews**) should import and call this service directly instead of querying the users collection themselves.

### Python Service Layer Integration (Module 8 / Module 9)

```python
from backend.app.services.user_service import get_public_profile

def create_order_snapshot(user_id):
    # Fetch sanitized customer profile
    customer = get_public_profile(user_id)
    if not customer:
        raise ValueError("Customer not found.")

    # Find customer's default address for shipping snapshot
    default_address = None
    for addr in customer.get('addresses', []):
        if addr.get('is_default'):
            default_address = addr
            break

    # Build customer snapshot for the order
    customer_snapshot = {
        "name": customer['name'],
        "email": customer['email'],
        "phone": customer['phone'],
        "address": default_address
    }
    return customer_snapshot
```
