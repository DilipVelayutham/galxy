# Handoff Notes - Module 1: Auth & User Accounts

This document contains integration instructions for all other module teams (Modules 2 through 12) to protect their routes, retrieve authenticated sessions, and build on top of Module 1.

---

## 1. Backend Integration

### 1.1 Protecting Route Endpoints
Import and use the decorators provided in `app.utils.auth_middleware` to protect endpoints.

```python
from app.utils.auth_middleware import require_auth, require_admin, optional_auth
```

1. **`@require_auth`**: Enforces a valid customer session.
   * If missing or invalid, returns `401 Unauthorized`.
   * If role is not `customer`, returns `403 Forbidden`.
   * Attaches the authenticated user document to the Flask request context as **`request.user`**.
2. **`@require_admin`**: Enforces a valid super_admin session.
   * If missing or invalid, returns `401 Unauthorized`.
   * If role is not `super_admin`, returns `403 Forbidden`.
   * Attaches the authenticated administrator document to the Flask request context as **`request.admin`**.
3. **`@optional_auth`**: Attempts to authenticate customer context without enforcing it.
   * If a valid customer token is present in the headers, populates **`request.user`**.
   * If missing, invalid, or expired, **`request.user`** remains `None`.

### 1.2 Accessing Session Context
Inside a decorated route, access the user/admin ID or properties directly:

```python
@app.route('/api/cart', methods=['GET'])
@require_auth
def get_cart():
    user_id = request.user['_id']  # ObjectId of the customer
    # ...
```

```python
@app.route('/api/admin/categories', methods=['POST'])
@require_admin
def create_category():
    admin_id = request.admin['_id']  # ObjectId of the admin
    # ...
```

### 1.3 Fetching Public Profiles (No Duplication)
If your module needs to return or show user details (e.g., reviews showing the reviewer name, or order invoices showing customer email), **do not query the users collection directly**. Call the helper:

```python
from app.services.user_service import get_public_profile

profile = get_public_profile(user_id)
# Returns: { "_id": "...", "name": "...", "email": "...", "phone": "...", "addresses": [...] }
# Guarantees that sensitive data like password_hash is never leaked.
```

### 1.4 Frozen Token Shape
Our signed JWT tokens carry the following claims:
```json
{
  "sub": "string (ObjectId)",
  "role": "customer | super_admin",
  "exp": "timestamp"
}
```

---

## 2. Frontend Integration (Next.js)

### 2.1 Protecting Pages (`AuthGuard`)
To protect pages requiring an active customer session, wrap the page layout or component in `AuthGuard`.
Example inside a page:

```tsx
import { AuthGuard } from "@/components/auth/AuthGuard";

export default function MyDashboard() {
  return (
    <AuthGuard>
      <main>Protected Customer Content</main>
    </AuthGuard>
  );
}
```

### 2.2 Consuming Authentication Context
Import and use `useAuth` to retrieve the current user session or invoke logouts.
*Note: Customer auth state is held in-memory (React Context) to avoid XSS token theft.*

```tsx
import { useAuth } from "@/context/AuthContext";

const { user, login, logout, isLoading } = useAuth();
```

### 2.3 Input Validation Module
Re-use client-side validators directly to keep UI feedback consistent with server validation policies:

```tsx
import { validateEmail, validatePassword, validatePhone, validatePincode } from "@/lib/validators";

const result = validateEmail(emailInput);
if (!result.isValid) {
  console.log(result.error); // "Invalid email format"
} else {
  console.log(result.value); // Lowercased normalized email
}
```

---

## 3. Active Coordination Items

1. **SMTP Configuration (Module 11 - Notifications)**:
   * Module 1 uses environment variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD`) for sending password-reset emails. Ensure these credentials match the centralized notification server definitions to avoid conflicts.
2. **Order Address Deletion (Module 8 - Orders)**:
   * In `address_service.py`, deleting the default address is blocked if there are pending orders in the `orders` collection (`status` not in `delivered`/`cancelled`). Ensure your Order schemas match `status` values for smooth integration.
