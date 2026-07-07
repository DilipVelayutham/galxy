# API Reference - Module 1: Auth & User Accounts

This document contains the complete and frozen API contracts for Module 1. Use this reference to integrate frontend components and other backend services (e.g. protected CMS or order checkout routes) with the identity layer.

## Authentication Strategy

* **Access Token**: Short-lived (15 minutes). Exchanged via the `Authorization: Bearer <token>` header.
* **Refresh Token**: Long-lived (30 days). Exchanged via an `httpOnly`, `Secure` cookie.
  * Customer Cookie: `refresh_token` (scoped to `/api/auth`)
  * Admin Cookie: `admin_refresh_token` (scoped to `/api/admin/auth`)

---

## 1. Customer Authentication Endpoints

### 1.1 Customer Signup
Create a new shopping customer account.
* **Method**: `POST`
* **Route**: `/api/auth/signup`
* **Authentication Required**: None
* **Request Body**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "9876543210",
    "password": "Password123"
  }
  ```
* **Success Response (201 Created)**:
  * *Cookie set*: `refresh_token=<jwt>`
  ```json
  {
    "success": true,
    "message": "Account created",
    "data": {
      "user": {
        "_id": "603d29a7c3df9b21f0000001",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "9876543210",
        "addresses": [],
        "auth_provider": "email",
        "is_verified": false,
        "is_active": true,
        "created_at": "2026-07-04T12:00:00.000Z",
        "updated_at": "2026-07-04T12:00:00.000Z",
        "last_login": null
      },
      "access_token": "eyJhbGciOiJIUzI1Ni..."
    }
  }
  ```
* **Error Responses**:
  * **400 Bad Request**: Invalid email/phone format or weak password.
  * **409 Conflict**: Email is already registered.

### 1.2 Customer Login
Authenticate customer credentials.
* **Method**: `POST`
* **Route**: `/api/auth/login`
* **Authentication Required**: None (Rate limited: 5 attempts per 15 mins per IP+email combo)
* **Request Body**:
  ```json
  {
    "email": "jane@example.com",
    "password": "Password123"
  }
  ```
* **Success Response (200 OK)**:
  * *Cookie set*: `refresh_token=<jwt>`
  ```json
  {
    "success": true,
    "data": {
      "user": {
        "_id": "603d29a7c3df9b21f0000001",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "9876543210",
        "addresses": [],
        "auth_provider": "email",
        "is_verified": false,
        "is_active": true,
        "created_at": "2026-07-04T12:00:00.000Z",
        "updated_at": "2026-07-04T12:00:00.000Z",
        "last_login": "2026-07-04T13:30:00.000Z"
      },
      "access_token": "eyJhbGciOiJIUzI1Ni..."
    }
  }
  ```
* **Error Responses**:
  * **401 Unauthorized**: Invalid credentials.
  * **403 Forbidden**: Account deactivated.
  * **429 Too Many Requests**: Rate limited.

### 1.3 Customer Logout
Clear the active session.
* **Method**: `POST`
* **Route**: `/api/auth/logout`
* **Authentication Required**: None (Clears the cookie client-side and server-side)
* **Success Response (200 OK)**:
  * *Cookie cleared*: `refresh_token=; Max-Age=0`
  ```json
  {
    "success": true,
    "message": "Logged out"
  }
  ```

### 1.4 Customer Silent Refresh
Acquire a new access token without re-prompting credentials.
* **Method**: `POST`
* **Route**: `/api/auth/refresh`
* **Authentication Required**: Valid `refresh_token` cookie.
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "access_token": "eyJhbGciOiJIUzI1Ni..."
    }
  }
  ```
* **Error Responses**:
  * **401 Unauthorized**: Refresh token missing or expired.
  * **403 Forbidden**: Associated account deactivated.

---

## 2. Password Recovery Endpoints (Tharani)

### 2.1 Forgot Password Request
Request a recovery link. Always returns 200 on correctly formatted inputs.
* **Method**: `POST`
* **Route**: `/api/auth/forgot-password`
* **Request Body**:
  ```json
  {
    "email": "jane@example.com"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "If the email is registered, a password reset link has been sent.",
    "data": {}
  }
  ```
* **Error Responses**:
  * **400 Bad Request**: Invalid email format.

### 2.2 Reset Password Submit
Submit a new password with the token received by email.
* **Method**: `POST`
* **Route**: `/api/auth/reset-password`
* **Request Body**:
  ```json
  {
    "token": "reset_token_from_email",
    "new_password": "NewSecurePassword123"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Password updated successfully",
    "data": {}
  }
  ```
* **Error Responses**:
  * **400 Bad Request**: Missing arguments or weak password (e.g. less than 8 chars).
  * **400 Bad Request**: Token invalid or expired.

---

## 3. Customer Profile & Address Endpoints (Naresh)

### 3.1 Get Profile
* **Method**: `GET`
* **Route**: `/api/user/profile`
* **Authentication Required**: Yes (`@require_auth`, role: customer)
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Profile retrieved successfully.",
    "data": {
      "_id": "603d29a7c3df9b21f0000001",
      "name": "Jane Doe",
      "email": "jane@example.com",
      "phone": "9876543210",
      "addresses": [
        {
          "_id": "603d29a7c3df9b21f0000099",
          "label": "Home",
          "line1": "123 Neon Road",
          "line2": "Apt 4B",
          "city": "Chennai",
          "state": "Tamil Nadu",
          "pincode": "600001",
          "is_default": true
        }
      ],
      "auth_provider": "email",
      "is_verified": false,
      "is_active": true,
      "created_at": "2026-07-04T12:00:00.000Z",
      "updated_at": "2026-07-04T12:00:00.000Z"
    }
  }
  ```

### 3.2 Update Profile
Update editable fields (`name` and `phone`). Email changes are explicitly blocked.
* **Method**: `PUT`
* **Route**: `/api/user/profile`
* **Authentication Required**: Yes (`@require_auth`, role: customer)
* **Request Body**:
  ```json
  {
    "name": "Jane Miller",
    "phone": "9876543211"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Profile updated successfully.",
    "data": {
      "_id": "603d29a7c3df9b21f0000001",
      "name": "Jane Miller",
      "email": "jane@example.com",
      "phone": "9876543211",
      "addresses": [...],
      ...
    }
  }
  ```
* **Error Responses**:
  * **400 Bad Request**: Attempting to change `email` or input validation failure.

### 3.3 Add Address
* **Method**: `POST`
* **Route**: `/api/user/addresses`
* **Authentication Required**: Yes (`@require_auth`, role: customer)
* **Request Body**:
  ```json
  {
    "label": "Work",
    "line1": "456 Office Towers",
    "line2": "Floor 12",
    "city": "Bangalore",
    "state": "Karnataka",
    "pincode": "560001",
    "is_default": false
  }
  ```
* **Success Response (201 Created)**:
  ```json
  {
    "success": true,
    "message": "Address added successfully.",
    "data": {
      "_id": "603d29a7c3df9b21f0000092",
      "label": "Work",
      "line1": "456 Office Towers",
      "line2": "Floor 12",
      "city": "Bangalore",
      "state": "Karnataka",
      "pincode": "560001",
      "is_default": false
    }
  }
  ```

### 3.4 Update Address
* **Method**: `PUT`
* **Route**: `/api/user/addresses/<address_id>`
* **Authentication Required**: Yes (`@require_auth`, role: customer)
* **Request Body**: Partial address payload.
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Address updated successfully.",
    "data": {
      "_id": "603d29a7c3df9b21f0000092",
      "label": "Work",
      "line1": "456 Office Towers (New Wing)",
      "line2": "Floor 12",
      "city": "Bangalore",
      "state": "Karnataka",
      "pincode": "560001",
      "is_default": true
    }
  }
  ```

### 3.5 Delete Address
* **Method**: `DELETE`
* **Route**: `/api/user/addresses/<address_id>`
* **Authentication Required**: Yes (`@require_auth`, role: customer)
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Address deleted successfully.",
    "data": {}
  }
  ```
* **Error Responses**:
  * **400 Bad Request**: Trying to delete the only saved address, or trying to delete the default address while an order is pending.

---

## 4. Admin Authentication Endpoints (Arun)

### 4.1 Admin Login
Authenticate platform administrators.
* **Method**: `POST`
* **Route**: `/api/admin/auth/login`
* **Authentication Required**: None (Rate limited: 5 attempts per 15 mins per IP+email combo)
* **Request Body**:
  ```json
  {
    "email": "admin@galxy.in",
    "password": "AdminPassword123"
  }
  ```
* **Success Response (200 OK)**:
  * *Cookie set*: `admin_refresh_token=<jwt>`
  ```json
  {
    "success": true,
    "data": {
      "admin": {
        "_id": "603d29a7c3df9b21f0000055",
        "name": "Admin Asil",
        "email": "admin@galxy.in",
        "role": "super_admin",
        "is_active": true,
        "created_at": "2026-07-04T12:00:00.000Z",
        "last_login": "2026-07-04T13:45:00.000Z"
      },
      "access_token": "eyJhbGciOiJIUzI1Ni..."
    }
  }
  ```
* **Error Responses**:
  * **401 Unauthorized**: Invalid credentials.
  * **403 Forbidden**: Admin account deactivated.
  * **429 Too Many Requests**: Rate limited.

### 4.2 Admin Logout
* **Method**: `POST`
* **Route**: `/api/admin/auth/logout`
* **Authentication Required**: None
* **Success Response (200 OK)**:
  * *Cookie cleared*: `admin_refresh_token=; Max-Age=0`
  ```json
  {
    "success": true,
    "message": "Logged out"
  }
  ```

### 4.3 Get Admin Profile
Fetch authenticated admin session details.
* **Method**: `GET`
* **Route**: `/api/admin/auth/me`
* **Authentication Required**: Yes (`@require_admin`, role: super_admin)
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "admin": {
        "_id": "603d29a7c3df9b21f0000055",
        "name": "Admin Asil",
        "email": "admin@galxy.in",
        "role": "super_admin",
        "is_active": true,
        "created_at": "2026-07-04T12:00:00.000Z",
        "last_login": "2026-07-04T13:45:00.000Z"
      }
    }
  }
  ```

### 4.4 Admin Silent Refresh
* **Method**: `POST`
* **Route**: `/api/admin/auth/refresh`
* **Authentication Required**: Valid `admin_refresh_token` cookie.
* **Success Response (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "access_token": "eyJhbGciOiJIUzI1Ni..."
    }
  }
  ```
* **Error Responses**:
  * **401 Unauthorized**: Missing or expired admin refresh token.
