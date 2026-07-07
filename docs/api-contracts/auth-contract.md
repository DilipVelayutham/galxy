# GALXY - Module 1: Cross-Module API & Authentication Contracts

This document contains the frozen, stable authentication contracts, decorator specifications, and JWT payload designs that all other 11 module teams (Cart, Wishlist, Orders, Reviews, Admin CRUD) must consume and respect. 

---

## 1. Frozen Middleware Decorators

All protected routes across the application must use these centralized decorators rather than performing custom JWT validation.

### 1.1 `@require_auth`
- **Scope**: Customer-facing protected routes.
- **Contract**: Decodes and verifies the customer token. Attaches the MongoDB user document (from the `users` collection) to Flask's request context as `request.user`.
- **Usage**:
  ```python
  from app.utils.auth_middleware import require_auth
  from flask import request, jsonify

  @my_blueprint.route('/my-endpoint', methods=['GET'])
  @require_auth
  def my_endpoint():
      # Access logged-in user id
      customer_id = str(request.user["_id"])
      return jsonify({"success": True, "data": {"user_id": customer_id}})
  ```
- **Error Codes**:
  - `401 Unauthorized`: Token is missing, expired, or invalid.
  - `403 Forbidden`: Authenticated user is not a customer, or account is deactivated.

### 1.2 `@require_admin`
- **Scope**: Admin-only backend actions (CMS, dashboard, products/categories modifications).
- **Contract**: Decodes and verifies the admin token. Attaches the MongoDB administrator document (from the `admin_users` collection) to Flask's request context as `request.admin`.
- **Usage**:
  ```python
  from app.utils.auth_middleware import require_admin
  from flask import request, jsonify

  @admin_blueprint.route('/stats', methods=['GET'])
  @require_admin
  def get_admin_stats():
      # Access logged-in admin details
      admin_name = request.admin["name"]
      return jsonify({"success": True, "data": {"admin_name": admin_name}})
  ```
- **Error Codes**:
  - `401 Unauthorized`: Token is missing, expired, or invalid.
  - `403 Forbidden`: Authenticated user is not an administrator, or account is deactivated.

### 1.3 `@optional_auth`
- **Scope**: Public routes where authenticated info can customize details (e.g. wishlist flags on public products).
- **Contract**: If a valid customer token is present in the Authorization header, attaches it to `request.user`. If no token, or if the token is expired/invalid, sets `request.user = None` and allows the request to proceed.
- **Usage**:
  ```python
  from app.utils.auth_middleware import optional_auth
  from flask import request

  @product_bp.route('/product/<id>', methods=['GET'])
  @optional_auth
  def get_product(id):
      user = request.user
      if user:
          # Customize response with user state
          pass
  ```

---

## 2. JWT Payload Contract

The schema of all JSON Web Tokens is frozen. Do not introduce customized claims in other modules.

```json
{
  "sub": "string (MongoDB ObjectId hex)",
  "role": "customer | super_admin",
  "type": "access | refresh",
  "exp": "integer (Unix Epoch Timestamp)"
}
```

### 2.1 Claims Details
- **`sub`**: Subject. Contains the exact user/admin database ID.
- **`role`**: Security level of the token. A token with `role: "customer"` will be rejected by `@require_admin` and vice versa.
- **`type`**: The token's purpose. `access` tokens are short-lived (15 minutes) and are passed in headers. `refresh` tokens are long-lived (30 days) and are passed in cookies.
- **`exp`**: Expiration window (enforced on backend during decode).

---

## 3. Platform-Standard JSON Response Shape

All endpoints in all modules must conform to the unified platform response structures.

### 3.1 Standard Success Payload (HTTP 200/201)
```json
{
  "success": true,
  "message": "Descriptive success string (optional)",
  "data": {
    "key": "value"
  }
}
```

### 3.2 Standard Failure Payload (HTTP 400/401/403/409/429/500)
```json
{
  "success": false,
  "message": "Global descriptive error message",
  "errors": {
    "field": "Field-specific validation failure reason"
  }
}
```
*Note: Even if there are no field-specific errors, the `"errors": {}` dictionary MUST be included in the payload to ensure parsing consistency on the client.*

---

## 4. Cross-Module Data Handoff

### 4.1 Do Not Duplicate User Lookups
Any downstream module (e.g. Orders, Reviews) that requires user profile details (such as showing the name of a customer on a review or shipping details on an order) must **not** query the database or access the `users` collection directly.

Instead, import and invoke the `UserService.get_public_profile(user_id)` helper:
```python
from app.services.user_service import UserService

# Returns dictionary with safe fields only (name, email, phone)
# Omits password_hash and saved addresses.
public_user = UserService.get_public_profile(user_id)
```
