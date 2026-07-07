# GALXY - Module 1: API Standards & Governance Guidelines

This document details the naming conventions, validation constraints, request structures, and error standards governing the API endpoints and models of the GALXY platform.

---

## 1. Naming & Case Conventions

To ensure consistent integration, all codebase components must align with the following standards:

### 1.1 Python Code Conventions
- **Variable & Function Names**: Snake_case (e.g. `generate_access_token`, `validate_password`).
- **Class Names**: PascalCase (e.g. `AdminAuthService`, `ExpiredTokenError`).
- **File Names**: Snake_case (e.g. `token_helper.py`, `auth_middleware.py`).
- **Blueprint Prefix**: Prefix blueprints clearly with domain scopes (e.g., `auth_bp`, `admin_auth_bp`).

### 1.2 Frontend Code Conventions (TypeScript/React)
- **Component & Layout Files**: PascalCase (e.g. `AuthForm.tsx`, `AuthGuard.tsx`).
- **Helper & Context Files**: PascalCase or camelCase (e.g. `AdminAuthContext.tsx`, `validators.ts`).
- **API URLs**: Lowercase kebab-case (e.g. `/api/admin/auth/login`, `/api/auth/forgot-password`).

---

## 2. Request & Response Payload Standards

### 2.1 JSON Format
All POST, PUT, and DELETE payloads must use valid JSON and set `Content-Type: application/json`.

### 2.2 Standard Success Shape
All successful routes must return the following JSON structure:
- **Structure**:
  ```json
  {
    "success": true,
    "message": "Descriptive message detailing what was done (optional)",
    "data": {}
  }
  ```
- **Example (Customer Login 200)**:
  ```json
  {
    "success": true,
    "data": {
      "user": {
        "_id": "64bfad28f09d2e1c945a6c11",
        "name": "Dilip Velayutham",
        "email": "dilip@example.com",
        "phone": "9876543210",
        "is_verified": false
      },
      "access_token": "eyJhbGciOi..."
    }
  }
  ```

### 2.3 Standard Failure Shape
All failed routes must return:
- **Structure**:
  ```json
  {
    "success": false,
    "message": "Descriptive error message",
    "errors": {}
  }
  ```
- **Example (Validation Error 400)**:
  ```json
  {
    "success": false,
    "message": "Invalid password format",
    "errors": {
      "password": "Password must be at least 8 characters long and contain at least one number."
    }
  }
  ```

---

## 3. Data & Validation Constraints

Backend services must validate fields according to these strict rules. Frontends must replicate these rules locally to provide instant feedback while relying on backend enforcement as the ground truth.

| Field | Validation Type | Constraint Description | Regex/Rule |
| :--- | :--- | :--- | :--- |
| **Email** | Format & Case | Standard email format; converted to lowercase before evaluation or lookup | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` |
| **Password** | Strength | Minimum 8 characters; must contain at least 1 letter and 1 number | `min_len = 8`, `contains(alpha)`, `contains(digit)` |
| **Phone** | Indian Format | Must represent a valid 10-digit Indian mobile number starting with 6-9 | `^[6-9]\d{9}$` |
| **Pincode** | Format | Exactly 6 numeric digits | `^\d{6}$` |

---

## 4. Error Handling and Logging Policies

### 4.1 No Sensitive Data Leakage
- Never print, log, or include sensitive user information (passwords, JWT secrets, reset tokens, password hashes) in application log files or debug traces.
- Catch domain errors via custom exceptions (e.g. `AuthServiceError`, `AdminAuthServiceError`) and return readable error payloads instead of exposing raw MongoDB error details or raw stack traces.

### 4.2 DB Integrity
- Validate fields before initiating insert operations. For uniqueness (such as user email), query the collection index beforehand to return a clear `409 Conflict` response instead of throwing a generic unhandled MongoDB write exception.
