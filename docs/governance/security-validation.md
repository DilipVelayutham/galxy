# GALXY - Module 1: Security Validation Report

This report evaluates and certifies the cryptographic, network, session, and rate-limiting security mechanisms implemented in Module 1 (Auth & User Accounts).

---

## 1. Cryptographic Safeguards

- **Algorithm**: Passwords are hashed using the **BCrypt** adaptive hashing function (`app/utils/password_helper.py`).
- **Cost Factor**: Evaluated and set to **12** rounds. This achieves an optimal balance between server processing overhead and brute-force computational cost.
- **Data Protection**: Plaintext passwords are never stored in the database, printed to logs, or cached in variables outside transient login/registration contexts.

---

## 2. Rate-Limiting and Brute-Force Mitigation

Brute-force password guessing is throttled by a stateful memory-locked rate limiter (`app/utils/rate_limiter.py`):
- **Endpoints Protected**: `POST /api/auth/login` and `POST /api/admin/auth/login`.
- **Threshold**: Maximum **5 attempts per 15 minutes** (900 seconds).
- **Partitioning Key**: Keyed per IP Address + Lowercased Email address combo. This blocks targeting a single user from multiple IPs, while preventing a single rogue IP from locking out innocent users.
- **Fail Response**: HTTP `429 Too Many Requests` returning the standard failure shape.

---

## 3. Cookie and Network Policy

Refresh tokens are issued via HTTP cookies to shield them from client-side script inspection.

- **Cookie Flags**:
  - `httpOnly`: Enabled. Prevents access via `document.cookie` to immunize sessions against Cross-Site Scripting (XSS) token theft.
  - `secure`: Bound to `os.getenv("FLASK_ENV") == "production"`. Ensures tokens are transmitted exclusively over encrypted HTTPS connections in production.
  - `samesite`: Set to `Lax` to allow cross-origin Next.js development (localhost:3000 -> localhost:5000) while blocking malicious Cross-Site Request Forgery (CSRF) attempts.
  - `path`: Restricted to `/api/auth` for customers, and `/api/admin/auth` for admins. Prevents other API routes from receiving session-refresh cookies unnecessarily.

---

## 4. CORS Policy

CORS policies are configured using Flask-CORS to reject unauthorized domains:
- **Default configuration**: Bound to `ALLOWED_ORIGINS` environment setting.
- **Allowed Origins**: Strict list (e.g. `http://localhost:3000`). No wildcard `*` is ever allowed.
- **Credentials Support**: `supports_credentials=True` is restricted to authorized origins to permit cookie transit securely.

---

## 5. Session Token Security

- **JWT Signing**: Signed with a cryptographically secure key `JWT_SECRET` using the `HS256` HMAC algorithm.
- **Claim Isolation & Middleware Enforcement**: Access and refresh tokens are distinguished via a `"type"` claim. Access tokens are rejected at the `/refresh` endpoint (handled by `AuthService` and `AdminAuthService`). Crucially, the `@require_auth` and `@require_admin` middleware decorators explicitly verify that the bearer token possesses a `"type": "access"` claim, rejecting any refresh tokens presented as Bearer authorization credentials. This is verified by the regression test `test_refresh_token_rejected_by_middleware`, which asserts that both customer and admin refresh tokens fail middleware authentication with a 401 response.
- **Client Session Isolation**: Customer tokens are held in-memory via the customer `AuthContext`. Admin tokens are held in a separate `AdminAuthContext`. Admin tokens are never stored in `sessionStorage` or `localStorage`, neutralizing the threat of persistent XSS token theft.
- **Role Isolation**: Admin endpoints require the `role` claim to equal `super_admin`. Customer tokens are instantly rejected on admin routes, and admin tokens are rejected on customer profile routes.
