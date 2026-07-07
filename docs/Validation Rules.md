# Validation Rule Specification

This document details the validation constraints and rules enforced across both the frontend and backend for the Profile and Address domains in Galxy Module 1.

## Profile Validation Rules

### 1. Name
* **Context**: User Display Name.
* **Constraints**:
  * **Required**: Yes, must be present and non-empty.
  * **Sanitization**: Leading and trailing whitespaces are trimmed.
* **Error Message**: `"Name is required."`

### 2. Email
* **Context**: Registered email address for credentials and notifications.
* **Constraints**:
  * **Format**: Standard email pattern matching.
  * **Normalization**: Converted to lowercase before storage and query lookup.
  * **Immutability**: Once created, the email **cannot** be changed or updated through the profile update endpoint (`PUT /api/user/profile`).
* **Error Message**: `"Email cannot be updated through the profile endpoint."` or `"Email must be a valid email address."`

### 3. Phone (User Profile)
* **Context**: Primary contact number.
* **Constraints**:
  * **Required**: Yes (on profile creation / updates).
  * **Format**: 10-digit Indian mobile format (starts with digits 6-9, total 10 digits).
  * **Regex Pattern**: `^[6-9]\d{9}$`
* **Error Message**: `"Phone must be a valid 10-digit Indian mobile number."`

---

## Address Validation Rules

### 1. Label
* **Context**: Tag classifying the address.
* **Constraints**:
  * **Allowed Values**: Exactly one of: `Home`, `Work`, `Other`.
* **Error Message**: `"Label must be one of: Home, Work, Other."`

### 2. Street Address (Line 1)
* **Context**: Main address lines (house number, street name, block).
* **Constraints**:
  * **Required**: Yes, must be a non-empty string.
* **Error Message**: `"Line1 is required."`

### 3. Address Line 2
* **Context**: Sub-address details (apartment name, floor, wing).
* **Constraints**:
  * **Required**: No, optional string. Defaults to empty string.

### 4. City
* **Context**: Delivery city.
* **Constraints**:
  * **Required**: Yes, must be a non-empty string.
* **Error Message**: `"City is required."`

### 5. State
* **Context**: Delivery state.
* **Constraints**:
  * **Required**: Yes, must be a non-empty string.
* **Error Message**: `"State is required."`

### 6. Pincode
* **Context**: 6-digit postal code.
* **Constraints**:
  * **Required**: Yes.
  * **Format**: 6-digit numeric digits.
  * **Regex Pattern**: `^\d{6}$`
* **Error Message**: `"Pincode must be a 6-digit numeric code."`
