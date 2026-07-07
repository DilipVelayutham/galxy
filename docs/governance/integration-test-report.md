# GALXY - Module 1: Integration & Unit Test Report

This report summarizes the testing coverage, suite configuration, and validation assertions for the Module 1 Authentication engine.

---

## 1. Test Suite Configuration

All tests are implemented using Python's standard `unittest` framework and run using `mongomock` to simulate database operations without requiring a live MongoDB server instance.

- **Test File**: `backend/tests/test_auth.py`
- **Execution Command**: `.\.venv\Scripts\python -m unittest tests/test_auth.py`
- **Mock DB Adapter**: `mongomock.MongoClient`

---

## 2. Test Coverage Summary

Our test suite covers all cryptographic helpers, domain format validators, token encoders, backend service layers, middleware decorators, HTTP-level endpoint routes, and security limits.

| Test Function | Component Under Test | Scope & Assertions |
| :--- | :--- | :--- |
| `test_password_helper` | `password_helper.py` | Validates BCrypt hash generation, matching password verification, mismatch rejection, and blank password assertions. |
| `test_validators` | `validators.py` | Asserts correct regex checks for email structures, password complexity, 10-digit Indian mobile formats, and 6-digit pincodes. |
| `test_token_helper` | `token_helper.py` | Verifies access/refresh token generation, expiries, token decode operations, and expired/invalid token exception raising. |
| `test_signup_and_login_service` | `auth_service.py` | Checks backend customer signup, duplicate checks, login validations, last login updates, and account deactivation blocks. |
| `test_token_refresh_service` | `auth_service.py` | Asserts refresh token decoding, role isolation, user status check, and token rotation during refresh. |
| `test_routes_signup_login_logout` | `auth_routes.py` | Tests HTTP customer registration, login response headers (setting httpOnly refresh cookies), and logout cookie clearing. |
| `test_middleware_role_isolation` | `auth_middleware.py` | Validates role isolation (customer token gets 403 on admin routes, admin token gets 403 on customer routes). |
| `test_rate_limiter` | `rate_limiter.py` | Asserts that exceeding 5 attempts locks out the IP+Email combo, and that the lockout resets after the time window. |
| `test_admin_login_and_refresh_http` | `admin_auth_routes.py` & `admin_auth_service.py` | Verifies HTTP admin login, token properties (type, role), refresh cookie issuance, and HTTP refresh token rotation. |
| `test_token_type_mismatch_refresh` | `token_helper.py` & refresh routes | Confirms that access tokens submitted to customer or admin refresh endpoints are rejected with a type-claim error. |

---

## 3. Test Run Execution Results

```
..........
----------------------------------------------------------------------
Ran 10 tests in 6.012s

OK
```

All 10 integration and unit tests pass with zero failures or errors, verifying functional, structural, and security correctness.
