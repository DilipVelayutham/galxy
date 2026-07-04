# Data Integrity Test Report

This report outlines the verification results of the critical database invariants and service-level constraints implemented within the Profile and Address domains. All tests were executed against an in-memory mocked database using `pytest`.

## Core Invariants Enforced

### 1. Single Default Address Invariant
* **Rule**: A user can have at most one address designated as default (`is_default = True`).
* **Implementation**:
  * If a user adds their first address, it is forced to `is_default = True`.
  * If a user adds a new address with `is_default = True` or updates an existing address to `is_default = True`, all other addresses in the user's list are automatically updated to `is_default = False` in the service layer before persistence.
  * If a user sets their default address to `is_default = False`, and they have other addresses, the default flag is automatically transferred to the first alternative address. If it is their only address, it is kept as default.
* **Test Case**: `test_address_invariants` & `test_delete_default_address_changes_default`
* **Status**: **PASSED**

### 2. Minimum Address Count Invariant
* **Rule**: Once a user has saved at least one address, they cannot delete their last remaining address.
* **Implementation**:
  * Before processing any deletion, the service layer queries the length of the user's `addresses` sub-document array.
  * If the length is `1`, the deletion request is blocked, raising a validation error.
* **Test Case**: `test_address_invariants` (Steps 4 & 5)
* **Status**: **PASSED**

### 3. Pending Order Deletion Guard
* **Rule**: Block deletion of the last default address if the user has a pending order linked to it.
* **Implementation**:
  * Before deleting an address with `is_default = True`, the service scans the `orders` collection for any order belonging to the user that is in a pending state.
  * **Pending States Checked**: `received`, `reviewed`, `quote_sent`, `confirmed`, `in_production`, `ready`, `out_for_delivery`.
  * If a pending order is found, the deletion is rejected with a validation error to prevent checkout shipping desyncs.
* **Test Case**: `test_delete_default_address_blocked_by_pending_order`
* **Status**: **PASSED**

---

## Pytest Execution Summary

A total of 7 test cases covering the entire boundary conditions of this implementation were run.

```bash
platform win32 -- Python 3.12.1, pytest-9.1.1, pluggy-1.6.0
collected 7 items

backend/tests/test_profile_address.py .......                            [100%]

======================= 7 passed, 19 warnings in 0.61s ========================
```

| Test Case | Invariant/Feature Verified | Result |
| :--- | :--- | :---: |
| `test_get_profile_requires_auth` | Route protection & authentication failure handling (401) | **PASSED** |
| `test_get_profile_success` | Retrieval of full profiles for authenticated users | **PASSED** |
| `test_update_profile_success` | Name and phone update logic on profile | **PASSED** |
| `test_update_profile_rejects_email` | Immutability constraint on email updates (400 validation error) | **PASSED** |
| `test_address_invariants` | Address creation CRUD, default auto-setting, and minimum count (1) block | **PASSED** |
| `test_delete_default_address_changes_default` | Promotion of another address to default when default is deleted | **PASSED** |
| `test_delete_default_address_blocked_by_pending_order` | Block default address deletion when user has active orders | **PASSED** |
