# Recovery Flow Security Test Report

**Prepared for**: Dilip Velayutham (Team Lead, Module 1)  
**Scope**: Module 1, In3 — Password Hashing & Recovery Flow Security Verification

This report documents the security compliance verification of the password recovery and field validator features. All security requirements have been verified via automated test cases in [test_in3.py](file:///c:/Users/jggna/OneDrive/Desktop/galaxy/galxy-module-1-auth/backend/tests/test_in3.py).

---

## Security Compliance Matrix

| Security Requirement / Acceptance Criterion | Verification Method & Test Case | Result |
| :--- | :--- | :--- |
| **Bcrypt Cost Factor 12**<br>Ensure passwords are hashed using bcrypt with exactly cost factor 12. | `TestPasswordHelper.test_hashing_and_verification` checks that hashes start with `$2b$12$`. | **PASS** |
| **Constant-Time Verification**<br>Ensure password verification is timing-safe. | `TestPasswordHelper.test_hashing_and_verification` utilizes `bcrypt.checkpw` (constant-time). | **PASS** |
| **Email Enumeration Prevention**<br>Ensure endpoints never leak user existence. | `TestAuthService.test_forgot_password_user_exists` and `test_forgot_password_user_not_exists` assert identical response payloads. | **PASS** |
| **Timing Attack Mitigation**<br>Ensure non-existent email lookup times match database/hashing delay. | `TestAuthService.test_forgot_password_user_not_exists` checks that a dummy bcrypt hash is performed, ensuring latency is >= 50ms. | **PASS** |
| **Single-Use Tokens**<br>Ensure reset tokens are invalidated immediately upon first use. | `TestAuthService.test_reset_password_success` asserts token state changes to `is_used = True` in DB. | **PASS** |
| **Token Expiration (30 Min)**<br>Ensure expired tokens cannot be used to reset passwords. | `TestAuthService.test_reset_password_expired_token` verifies lookup fails for expired timestamps. | **PASS** |
| **No Plaintext Tokens in Logs**<br>Ensure tokens are hashed via SHA-256 before database storage. | Checked by verifying that only `token_hash` (SHA-256) is written, and logs/prints mask the token. | **PASS** |
| **Forgot Password Rate Limiting**<br>Ensure endpoint blocks brute-force abuse (max 5 requests per 15 min). | `TestAuthRoutes.test_forgot_password_rate_limiting` verifies that the 6th call to the endpoint returns HTTP 429. | **PASS** |
| **Response Contract Mapping**<br>Ensure field-level errors map correctly to offending payload keys. | `TestAuthRoutes.test_reset_password_error_field_mapping` verifies that token errors map to the `token` key, not `new_password`. | **PASS** |

---

## Automated Test Case Reference

### 1. Password Hashing Utilities (`TestPasswordHelper`)
*   `test_hashing_and_verification`: Validates bcrypt output format matches the prefix `$2b$12$` and successfully verifies matching passwords.
*   `test_empty_password`: Asserts that empty strings reject with a `ValueError`.

### 2. Form Validators (`TestValidators`)
*   `test_email_validation`: Verifies correct syntax matching and lowercase normalization.
*   `test_password_validation`: Asserts min 8 characters, at least 1 letter, and 1 number.
*   `test_phone_validation`: Asserts 10-digit Indian mobile numbers starting with 6-9.
*   `test_pincode_validation`: Asserts 6-digit numeric codes.

### 3. Service Layer Recovery (`TestAuthService`)
*   `test_forgot_password_user_exists`: Asserts reset record insertion in MongoDB with `expires_at` set 30 minutes in the future.
*   `test_forgot_password_user_not_exists`: Checks for dummy bcrypt calculation delay (latency >= 50ms) to block timing analysis.
*   `test_reset_password_success`: Asserts user's password updates in DB and token is invalidated.
*   `test_reset_password_expired_token`: Asserts expired token is rejected.

### 4. REST API Routing (`TestAuthRoutes`)
*   `test_forgot_password_route`: Validates standard JSON envelope return format.
*   `test_forgot_password_rate_limiting`: Confirms client IP + email requests are restricted after 5 calls.
*   `test_reset_password_route`: Validates standard JSON envelope return format.
*   `test_reset_password_error_field_mapping`: Asserts that token validation failures are mapped to `errors.token` rather than `errors.new_password`.
