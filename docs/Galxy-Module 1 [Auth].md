**GALXY**

**Website Project — Module Contract & Development Spec**

**MODULE 1**

**Auth & User Accounts**

*Customer & Admin Identity · JWT Session Management · Profiles & Addresses*


Prepared by LTI Technology  |  Learn · Think · Innovate

Stack: Flask · MongoDB · JWT · bcrypt

Document Date: July 2026


# **1. Scope**

Everything related to identity: customer signup/login, session management, profile data, and saved addresses. This module is a dependency for almost every other module — Cart, Wishlist, Orders, Reviews, and the entire Admin side all sit behind auth — so it should be one of the first modules functionally complete, even though all 12 teams are working in parallel.

This module owns two separate identity tracks that must not be conflated:

Customer auth — public-facing users who shop

Admin auth — Asil's login into the CMS (separate collection, separate permissions, separate token scope)

# **2. Collections Owned by This Module**

## **2.1 users**

| {   "_id": ObjectId,   "name": "string",   "email": "string (unique, lowercase)",   "phone": "string",   "password_hash": "string (bcrypt)",   "addresses": [     {       "_id": ObjectId,       "label": "Home | Work | Other",       "line1": "string",       "line2": "string",       "city": "string",       "state": "string",       "pincode": "string",       "is_default": true     }   ],   "auth_provider": "email | google",   "is_verified": false,   "is_active": true,   "created_at": "datetime",   "updated_at": "datetime",   "last_login": "datetime" } |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |


## **2.2 admin_users**

| {   "_id": ObjectId,   "name": "string",   "email": "string (unique)",   "password_hash": "string (bcrypt)",   "role": "super_admin",   "is_active": true,   "created_at": "datetime",   "last_login": "datetime" } |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |


## **2.3 Indexes Required**

users.email — unique

admin_users.email — unique

users.phone — non-unique index (used for lookups/support)

# **3. Folder Structure (Flask)**

| app/   models/     user.py     admin_user.py     address.py   services/     auth_service.py         — signup, login, token issuance, password reset     user_service.py         — profile CRUD     address_service.py      — address CRUD     admin_auth_service.py   — separate admin login/session logic   routes/     auth_routes.py     user_routes.py     admin_auth_routes.py   configs/     jwt_config.py           — JWT_SECRET, JWT_EXPIRE, JWT_REFRESH_EXPIRE   utils/     password_helper.py      — hashing/verification (bcrypt)     token_helper.py         — encode/decode/verify JWT     validators.py           — email format, password strength, phone format     auth_middleware.py      — @require_auth, @require_admin decorators |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

# **4. Environment Variables**

| JWT_SECRET= JWT_ACCESS_EXPIRE_MINUTES=15 JWT_REFRESH_EXPIRE_DAYS=30 SMTP_HOST= SMTP_PORT= SMTP_EMAIL= SMTP_PASSWORD= |
| -------------------------------------------------------------------------------------------------------------------- |


| **Coordination Note** SMTP is needed here for password-reset emails and optional email verification — coordinate with the Module 11 (Notifications) team on shared SMTP config so it isn't duplicated. |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

# **5. Auth Strategy**

JWT-based, access token + refresh token pair.

Access token: short-lived (15 min), sent in Authorization: Bearer <token> header.

Refresh token: long-lived (30 days), stored as httpOnly, secure cookie — never exposed to JS, protects against XSS token theft.

On access token expiry, frontend silently calls /api/auth/refresh using the cookie to get a new access token.

Admin tokens must be structurally distinguishable from customer tokens — include a role claim in the JWT payload ("role": "customer" vs "role": "super_admin"). Every protected route checks the expected role, not just token validity. A valid customer token must never pass an admin-only check.

Passwords hashed with bcrypt (cost factor 12), never stored or logged in plaintext.

# **6. API Contract**

All responses follow the platform-standard shape:

| { "success": true, "message": "", "data": {} } { "success": false, "message": "", "errors": {} } |
| ------------------------------------------------------------------------------------------------ |

## **6.1 Customer Signup**

**  POST  **   **/api/auth/signup**

| Body: { "name", "email", "phone", "password" } |
| ---------------------------------------------- |

Success 201:

| { "success": true, "message": "Account created", "data": { "user": {...}, "access_token": "..." } } (refresh token set as httpOnly cookie) |
| ------------------------------------------------------------------------------------------------------------------------------------------ |

| **Code** | **Error Condition**                                            |
| -------- | -------------------------------------------------------------- |
| **400**  | Validation failure (weak password, invalid email/phone format) |
| **409**  | Email already registered                                       |

## **6.2 Customer Login**

**  POST  **   **/api/auth/login**

| Body: { "email", "password" } |
| ----------------------------- |

Success 200:

| { "success": true, "data": { "user": {...}, "access_token": "..." } } |
| --------------------------------------------------------------------- |

| **Code** | **Error Condition** |
| -------- | ------------------- |
| **401**  | Invalid credentials |
| **403**  | Account deactivated |

## **6.3 Logout**

**  POST  **   **/api/auth/logout**

Clears refresh token cookie server-side.

| Success 200: { "success": true, "message": "Logged out" } |
| --------------------------------------------------------- |

## **6.4 Refresh Token**

**  POST  **   **/api/auth/refresh**

Reads httpOnly refresh cookie.

| Success 200: { "success": true, "data": { "access_token": "..." } } |
| ------------------------------------------------------------------- |

| **Code** | **Error Condition**                                          |
| -------- | ------------------------------------------------------------ |
| **401**  | Refresh token invalid/expired → frontend must force re-login |

## **6.5 Forgot / Reset Password**

**  POST  **   **/api/auth/forgot-password**

| Body: { "email" } |
| ----------------- |

Always returns 200 with a generic message regardless of whether the email exists (prevents email enumeration attacks). Sends a time-limited reset token link via SMTP.


**  POST  **   **/api/auth/reset-password**

| Body: { "token", "new_password" } Success 200: { "success": true, "message": "Password updated" } |
| ------------------------------------------------------------------------------------------------- |

| **Code** | **Error Condition**   |
| -------- | --------------------- |
| **400**  | Token invalid/expired |

## **6.6 Profile**

**  GET  **   **/api/user/profile**

(auth required)

| Success 200: { "success": true, "data": { "name","email","phone","addresses":[...] } } |
| -------------------------------------------------------------------------------------- |


**  PUT  **   **/api/user/profile**

(auth required)

| Body: { "name"?, "phone"? }   — email change intentionally NOT allowed here                                 (needs a separate verified-email flow if ever added) Success 200: { "success": true, "message": "Profile updated", "data": {...} } |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

## **6.7 Addresses**

**  POST  **   **/api/user/addresses**

| Body: { "label","line1","line2","city","state","pincode","is_default" } |
| ----------------------------------------------------------------------- |

**  PUT  **   **/api/user/addresses/:id**

| Body: same fields, partial allowed |
| ---------------------------------- |

**  DELETE  **   **/api/user/addresses/:id**


**Rules:**

Setting is_default: true on one address must unset it on all others for that user (enforce server-side, not trust the client).

A user must always have at least one address once they've added one — block deletion of the last remaining default if it's linked to a pending order (soft rule, confirm with the Module 8 team).

## **6.8 Admin Auth (separate, isolated)**

**  POST  **   **/api/admin/auth/login**

| Body: { "email", "password" } |
| ----------------------------- |

| Success 200: { "success": true, "data": { "admin": {...}, "access_token": "..." } } |
| ----------------------------------------------------------------------------------- |

| **Code** | **Error Condition** |
| -------- | ------------------- |
| **401**  | Invalid credentials |


**  POST  **   **/api/admin/auth/logout**


**  GET  **   **/api/admin/auth/me**

Returns current admin identity, used by the admin frontend on load to verify session.


| **No Public Admin Signup** There is intentionally no public admin signup endpoint. Admin accounts are seeded directly in the database (single account for Asil at launch). If more admin/staff accounts are needed later, add an internal-only "invite admin" endpoint restricted to existing super_admin — not built in v1 unless requested. |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

# **7. Middleware / Decorators (used by every other module)**

| @require_auth          # validates customer JWT, attaches request.user @require_admin          # validates admin JWT + role check, attaches request.admin @optional_auth          # attaches request.user if token present, else None                          # (used on public routes like /api/products where                          # logged-in users might see wishlist state, guests don't) |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |


| **Frozen Contract** Every other team (Cart, Wishlist, Orders, Reviews, Admin CRUD across Modules 2/3/10) depends directly on these decorators. This module must expose them early and treat their contract as frozen — changing the decorator signature after other teams have integrated will cause cross-team breakage. |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

# **8. Validation Rules**

| **Field**    | **Rule**                                                                                                                                      |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Email**    | Standard format check, lowercase-normalized before storage/comparison.                                                                        |
| **Password** | Minimum 8 characters, at least one letter and one number. Return specific validation error messages so the frontend can show inline feedback. |
| **Phone**    | 10-digit Indian mobile format validation (adjust if international customers expected).                                                        |
| **Pincode**  | 6-digit numeric.                                                                                                                              |

# **9. Security Requirements**

Rate-limit /api/auth/login and /api/admin/auth/login (e.g. 5 attempts per 15 min per IP+email combo) to block brute force.

Never return whether an email exists in /forgot-password responses.

Never log passwords, tokens, or password hashes — even in debug/error logs.

Reset tokens: single-use, expire in 30 minutes, invalidated after successful reset.

CORS: only allow the actual frontend origin(s) in production, not *.

Cookies: httpOnly, secure, sameSite=strict (or lax if cross-subdomain needed between admin/public frontends).

# **10. What This Module Does NOT Do**

No payment/billing data (there is no payment gateway in this project at all).

No order data (owned by Module 8, which will reference user_id).

No cart/wishlist data (Modules 6/7 own those, reference user_id).

No role granularity beyond super_admin for v1 — don't over-build a permissions system that isn't needed yet.

# **11. Handoff Contract for Other Teams**

Other modules should treat the following as stable, frozen interfaces from Day 1:

request.user._id — available in any route decorated with @require_auth

request.admin._id — available in any route decorated with @require_admin

JWT payload shape: { "sub": user_id, "role": "customer" | "super_admin", "exp": ... }

Standard error codes: 401 = not authenticated, 403 = authenticated but not authorized


| **Don't Duplicate User Lookups** Any module needing user display info (name, email) for their own responses (e.g. Orders showing customer name) should not duplicate user lookup logic — call user_service.get_public_profile(user_id) exposed by this module, which returns only safe fields (never password_hash). |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
