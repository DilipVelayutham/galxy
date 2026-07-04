# Module 1 Test Report - Auth & User Accounts

This report details the execution and results of the Module 1 QA testing suite, validating customer identity, password recovery, profile and address management, admin isolation, and rate-limiting.

## Test Execution Summary

* **Execution Environment**: Python 3.13.7, pytest 9.1.1, mongomock 4.3.0
* **Total Tests Executed**: 32
* **Total Tests Passed**: 32
* **Total Failures / Errors**: 0
* **Status**: **PASS (100% SUCCESS)**

---

## 1. Test Coverage Areas

### 1.1 Customer Signup, Login, and Tokens (Dilip)
* **Tests**: `tests/test_auth.py`
  * `test_signup_and_login_service`: Validates signup inputs (valid email/phone/password), prevents duplicate email signups (returns 409 Conflict), confirms login successes and fails on invalid credentials, and enforces deactivation blocks (returns 403).
  * `test_token_refresh_service`: Confirms token rotation, silent refreshes with valid tokens, and forces re-login on expired/invalid signatures.
  * `test_routes_signup_login_logout`: Validates the signup and login routes, ensuring HTTP-only, secure, sameSite session cookies are attached and deleted correctly on logout.

### 1.2 Password Recovery & Hashing (Tharani)
* **Tests**: `tests/test_in3.py`
  * `test_password_helper`: Validates bcrypt hashing (cost factor of 12) and verification.
  * `test_validators`: Checks Indian phone format validations, standard email regex checks, password rules (min 8 chars, 1 letter, 1 number), and 6-digit numeric pincode constraints.
  * `test_forgot_password_user_exists`: Verifies reset tokens are created in `password_resets` and a reset link is logged or sent via SMTP.
  * `test_forgot_password_user_not_exists`: Confirms email-enumeration protection by simulating standard bcrypt execution delays (timing-attack mitigation) and always returning a generic response.
  * `test_reset_password_success`: Confirms valid tokens successfully hash and overwrite passwords and mark the token as used (single-use constraint).
  * `test_reset_password_expired_token`: Rejects expired or double-used tokens.

### 1.3 User Profile & Addresses (Naresh)
* **Tests**: `tests/test_profile_address.py`
  * `test_get_profile_requires_auth` & `test_get_profile_success`: Verifies access token checks for profile access.
  * `test_update_profile_success`: Validates updating user's display name and phone number.
  * `test_update_profile_rejects_email`: Verifies that email updates are rejected at profile endpoints.
  * `test_address_invariants`:
    * First added address is automatically set as the default address.
    * Adding a new default address unsets the `is_default` claim on all other addresses.
    * A user must retain at least one address once they have added one (blocks deletion of the last remaining address).
  * `test_delete_default_address_changes_default`: Deleting the current default address automatically promotes another saved address to default.
  * `test_delete_default_address_blocked_by_pending_order`: Soft invariant checking that blocks deleting the default address if the user has a pending order (`received`, `confirmed`, etc.).

### 1.4 Admin Authentication & Role Isolation (Arun)
* **Tests**: `tests/test_admin_auth.py` and `tests/test_auth.py::test_middleware_role_isolation`
  * `test_admin_user_model`: Asserts `AdminUser` document creation, role seeding, and safe public serialization (password hash popped).
  * `test_admin_login_service_success` & `test_admin_login_service_failures`: Validates that administrators authenticate securely, deactivation blocks are respected, and super-admin token claims are attached.
  * `test_admin_routes_login_logout_me_refresh`: Verifies that admin routes (`/me`, `/refresh`, `/logout`) work end-to-end, scoped specifically to the separate `admin_refresh_token` cookie.
  * `test_middleware_role_isolation`: **Critical isolation test** ensuring:
    * A valid customer token is rejected with a `403 Forbidden` on all `@require_admin` endpoints.
    * A valid admin token is rejected with a `403 Forbidden` on all customer `@require_auth` endpoints.
  * `test_admin_rate_limiter`: Verifies that rate-limiting blocks brute force login attempts (5 attempts per 15 minutes window).

---

## 2. Resolved Edge Cases and Fixes

1. **Token Signature Verification Issues**:
   * *Problem*: In custom tests, mock tokens generated with a local string signature failed with `401 Unauthorized` because the middleware compared them against `JWTConfig.JWT_SECRET`.
   * *Resolution*: Refactored test token generation to leverage the centralized `generate_access_token` utility from `token_helper.py`, ensuring consistent signature validation.
2. **Double Default Address Conflict**:
   * *Problem*: Adding an address with `is_default=True` could lead to multiple defaults in the array if the backend did not actively search and update.
   * *Resolution*: Implemented server-side logic in `address_service.py` that loops through user addresses and forces all other addresses to `is_default=False` when a new default is created or updated.
3. **Delete Default Address Promotion**:
   * *Problem*: Deleting the default address left the user without any default address.
   * *Resolution*: Implemented auto-promotion. If the deleted address was default, the next available address in the array is automatically flagged as default, keeping data integer.

---

## 3. Frontend Compilation Status
* **Script Run**: `node node_modules/next/dist/bin/next build`
* **Result**: **SUCCESS**
  * All pages compiled without type-checking or bundling errors.
  * Router-group paths (`/account/addresses` and `/account/profile`) were verified to resolve correctly.
  * TypeScript type parameters matching the backend payloads were verified to compile cleanly.

---

## 4. Frontend Route & Component Verification Report

As the Module 1 QA gatekeeper, we performed detailed manual testing across all integrated frontend components and paths (compiled successfully via Next.js 16.2.10):

### 4.1 Signup & Login (Dilip - In1)
* **Signup (`/signup`)**:
  * *Input validation*: Checked inline errors for blank names, improperly formatted emails, non-Indian phone formats, and weak passwords. All validated correctly client-side using `validators.ts`.
  * *Submit*: Creating an account hit the `/api/auth/signup` endpoint, successfully saved the user in MongoDB, issued JWT cookies, and redirected to home `/`.
* **Customer Login (`/login`)**:
  * *Login flow*: Verified password mask toggling, client-side validation, error handling on wrong passwords, and success redirection.
  * *Token refresh*: Verified that token is stored in React memory context (avoiding sessionStorage/localStorage exposure) and silently refreshed via `/api/auth/refresh` on page reload.

### 4.2 Profile & Address Book (Naresh - In2)
* **Profile (`/account/profile`)**:
  * *View/Update*: Verified profile loading from `/api/user/profile` and fields updating (name, phone) on submission.
  * *Email Read-Only*: Confirmed the email address field is disabled and read-only.
* **Addresses (`/account/addresses`)**:
  * *List / Cards*: Verified addresses load into beautiful dashboard cards with default markers.
  * *Address Form Modal*: Validated `AddressForm` props, pincode checks (must be 6 digits), required fields, and saving status changes.
  * *Default Address Invariants*: Checked that adding a new default address correctly resets previous defaults, and deleting the default address promotes another to default.

### 4.3 Password Recovery (Tharani - In3)
* **Forgot Password (`/forgot-password`)**:
  * *Enumeration protection*: Entered non-existent email; verified generic success alert is shown and response delay mimics hashing time.
* **Reset Password (`/reset-password?token=...`)**:
  * *Reset flow*: Verified changing password via mock token logs changes. Single-use token expiration checked.

---

## 5. Frontend Role Isolation Verification (Critical Compliance)

Role isolation checks were fully verified on the client-side context and guards (`AuthGuard.tsx` and `AdminGuard.tsx`):

| Initial Session State | Attempted Destination Path | Expected Behavior | Verification Status |
| :--- | :--- | :--- | :--- |
| Logged-in Customer | `/admin/dashboard` | Redirected to Home `/` by `AdminGuard` | **PASS** |
| Logged-in Customer | `/admin/login` | Redirected to Home `/` by `AdminGuard` | **PASS** |
| Logged-in Admin | `/account/profile` | Redirected to `/admin/dashboard` by `AuthGuard` | **PASS** |
| Logged-in Admin | `/account/addresses` | Redirected to `/admin/dashboard` by `AuthGuard` | **PASS** |
| Unauthenticated Guest | `/account/*` | Redirected to `/login` | **PASS** |
| Unauthenticated Guest | `/admin/dashboard` | Redirected to `/admin/login` | **PASS** |
