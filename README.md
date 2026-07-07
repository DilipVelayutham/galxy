# GALXY - Module 1: Auth & User Accounts

## Branch
`dev`

## Purpose

This is the **integration branch** for Module 1.

All completed work from individual intern branches must be merged into this branch after review by the Team Lead.

---

## Team

| Intern | Branch | Responsibility |
|---------|--------|----------------|
| Dilip Velayutham (TL) | in1-dilip | Authentication Core & Integration |
| Naresh Kumar | in2-naresh | User Profile & Address Management |
| Tharani Jayaprakash | in3-tharani | Password Recovery & Validation |
| Arun Kumar | in4-arun | Admin Authentication & Testing |

---

## Workflow

```
Individual Branch
        ↓
Pull Request
        ↓
Team Lead Review
        ↓
Merge into dev
        ↓
Module Testing
        ↓
Merge into main
```

---

## Rules

- ❌ Never develop directly on `dev`
- ❌ Never force push
- ✅ Merge only after review
- ✅ Keep `dev` stable

---

## Module Status

- [x] Authentication
- [x] Profile
- [x] Address
- [x] Password Reset
- [x] Admin Authentication
- [x] Testing
- [x] Documentation

---

## Architectural Decisions & Scope Deferrals (v1)

### 1. Cookie SameSite Directive ('Lax')
The JWT session refresh cookies are configured with `sameSite='Lax'` instead of `'strict'`. This is a deliberate decision to support cross-port local developer configurations (e.g. frontend running on `http://localhost:3000` and backend running on `http://localhost:5000`), allowing correct cookie transmission across origins during local integration.

### 2. Google OAuth Deferral
While the `users` collection model includes an `auth_provider` schema field, Google OAuth authentication is not in scope for the v1 delivery of this module. Users sign up and log in using email/password. Google OAuth endpoints and services are intentionally deferred to future versions.

### 3. Email Verification Flow Deferral
The `is_verified` boolean field is initialized to `false` for user accounts. Active email validation flows and verification endpoints are intentionally deferred for v1.

### 4. Admin Invite Flow Deferral
As outlined in the specifications, admin credentials are seeded directly in the database (single account for Asil at launch). Admin invite flows and staff permission systems are deferred.

---

**Maintained by:** Dilip Velayutham (Team Lead)
