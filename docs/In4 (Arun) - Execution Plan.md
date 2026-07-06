**GALXY — MODULE 1: AUTH & USER ACCOUNTS**

**ARUN KUMAR — ADMIN AUTHENTICATION, QA & DOCUMENTATION**

**MODULE EXECUTION DOCUMENT**


# Intern Information

**Intern Code: **GLX-M1-04

**Role: **Backend Developer — Admin Identity, Testing & Documentation

**Team: **Module 1 — Auth & User Accounts

**Branch Name: **in4-arun

**Primary Responsibility:**

Admin Authentication, Admin Routes, Admin Service, Module Testing, Module Documentation.

**Reports To: **Dilip Velayutham (Team Lead, Module 1)

**Review Cycle: **Continuous — per milestone review

**Timeline: **Module 1 delivery cycle (parallel with 11 other module teams)

**Priority Level: **HIGH

# Your Role In The Project

You own a track that is deliberately isolated from the rest of the module: Asil's identity as the platform's single administrator. Admin auth uses a separate collection, a separate login route, and a separate token role — it must never be reachable with a customer credential, and a customer route must never be reachable with an admin credential.

You are also the module's quality gate. By the time Module 1 is handed off to the other 11 teams, you are the one who has actually run every endpoint, confirmed every rule in the spec, and written the documentation the rest of the project will read instead of re-deriving the module's behavior from source.

**Without your work:**

Asil has no way to log into the CMS at all

The entire Admin CMS (Categories, Products, Orders, Site Content, Analytics — Modules 2, 3, 8, 10, 12) has no identity layer to sit behind

Nobody has verified that customer and admin tokens are actually isolated from each other

No other module team has documentation to integrate against — only source code


**Your responsibility is NOT:**

Building signup, login, tokens, or middleware for customers (owned by in1)

Building profile or address CRUD (owned by in2)

Building password recovery or SMTP integration (owned by in3)

Building any frontend component in the customer-facing auth/profile/address domain (owned by in1, in2, in3) — your only frontend build is the admin login screen


**Your responsibility IS:**

Building the fully isolated admin authentication service and routes

Enforcing that no public admin signup endpoint exists

Testing every endpoint across the whole module, not only your own

Writing the module's handoff documentation for the other 11 teams

Confirming role isolation between customer and admin tokens before sign-off

Building the /admin/login page, isolated from the customer session

Testing every frontend page and component across the whole module (in1, in2, in3), not only your own

Documenting the frontend routes and component contracts alongside your existing API documentation

Confirming frontend role isolation: a customer session can never reach the admin frontend, and an admin session is never usable on customer-facing pages

# Module Mission

By the end of this module, the following must all be true:

✓  Admin login, logout, and session-check endpoints function correctly

✓  Admin identity is fully isolated from customer identity — separate collection, separate token role

✓  No public admin signup endpoint exists anywhere in the codebase

✓  Every endpoint across the whole module has been tested, not only the admin track

✓  A documented test report exists covering success and failure cases for every route

✓  Module documentation is written and ready for the other 11 module teams to consume

✓  Your work is fully merged into in1's integrated Flask app with no conflicts

***✓  /admin/login functions correctly and is isolated from the customer AuthContext/session***

***✓  Every frontend page and component across the module (in1, in2, in3) has been tested, not only the admin track***

***✓  Frontend role isolation is confirmed: no session bleed between customer and admin***

# Repository Structure Ownership

backend/


app/

├── models/

│   └── admin_user.py        — fully yours

│

├── services/

│   └── admin_auth_service.py — fully yours

│

├── routes/

│   └── admin_auth_routes.py  — fully yours

│

├── utils/

│   └── auth_middleware.py    — consumed, not owned (built by in1)

│   └── token_helper.py       — consumed, not owned (built by in1)

│   └── password_helper.py    — consumed, not owned (built by in3)

│

└── __init__.py               — consumed, not owned (built by in1)


docs/

└── module1/

    ├── api-reference.md      — fully yours

    ├── test-report.md        — fully yours

    └── handoff-notes.md      — fully yours


models/admin_user.py, services/admin_auth_service.py, and routes/admin_auth_routes.py are entirely yours — no other member should need to edit these. Everything you build calls into in1's token_helper.py and in3's password_helper.py rather than duplicating their logic.


***frontend/ (Next.js)***


***app/***

***└── (admin)/***

***    └── login/page.tsx        — fully yours***


***You own (admin)/login/page.tsx entirely. It must not import or reuse in1’s customer AuthContext instance — the admin session is architecturally separate, matching the backend isolation you already enforce.***

# System Architecture Responsibilities

***Admin Identity Domain Architecture***

Modules within your domain:

Admin Login / Logout

Admin Session Verification

Admin Identity Isolation

Module-Wide Testing & Documentation

***Technical Architecture***

Define, within the boundaries in1 has set for the module:

The admin_users collection shape and its single role value (super_admin) for v1

How admin_auth_service.py reuses in1's token_helper.py without duplicating JWT logic

The structure of your test suite and documentation set so they're usable by every other module team

***Identity Isolation Architecture (Critical Compliance)***

Implement:

A completely separate login route (/api/admin/auth/login) and service function from the customer track — no shared code path between the two logins beyond token_helper.py and password_helper.py.

A role claim ("role": "super_admin") on every admin token that @require_admin checks explicitly, not merely token validity.

Enforce: there is no public admin signup endpoint anywhere in the codebase. Admin accounts are seeded directly in the database — a single account for Asil at launch. Do not build an "invite admin" endpoint unless explicitly requested.

***Standards***

Follow the standards in1 has approved for the module:

Naming conventions for files, functions, and routes

The standard API response contract

Error handling conventions

# Admin Service Responsibilities

***admin_auth_service.py***

login(email, password) — verify against admin_users, issue a token with role: super_admin

logout() — clear admin session/cookie server-side

get_current_admin(admin_id) — return the identity used by /api/admin/auth/me

Every function here calls in1's token_helper.py and in3's password_helper.py directly — it does not reimplement token or hashing logic.

# Frontend Responsibilities

***Your frontend footprint mirrors your backend track: one isolated admin login screen, plus the same module-wide quality-gate role you hold on the backend, extended to every page and component the other three members build.***

***Page You Own***

/admin/login — isolated admin login screen; uses the admin dashboard’s flatter, denser visual treatment (same dark base and accent colors, less glow) per the project plan’s design system, not the glow-heavy public theme used by in1’s /login

***Frontend Testing Responsibilities (Module-Wide)***

in1: /signup, /login, AuthGuard redirect behavior, silent refresh — success and failure paths

in2: /account/profile, /account/addresses, AddressCard/AddressForm, the single-default-address optimistic UI

in3: /forgot-password, /reset-password, the shared validators module, enumeration-safe UI behavior

in4 (yours): /admin/login, and the frontend customer/admin session-isolation test

***Frontend Role Isolation Test (Critical)***

Explicitly verify: a customer session in the browser cannot access /admin/login’s authenticated area, and an admin session cannot access any /account/* page

***Design System Compliance***

/admin/login still uses the dark neon palette and rounded-corner form treatment, but flatter and less glow-heavy, matching the rest of the admin CMS

# Cross-Module Integration

***in1 Integration — Auth & Tokens***

Required Contracts: token_helper.py encode/decode functions, the @require_admin decorator, and the frozen JWT payload shape ({ sub, role, exp }).

Validate: your admin tokens carry role: super_admin and are correctly rejected by any route expecting role: customer.

***Frontend: your /admin/login page must not reuse in1’s AuthContext instance or storage key — verify complete separation before integration.***

***in3 Integration — Password Hashing***

Required Contracts: password_helper.hash_password() / verify_password() — admin passwords must be hashed identically to customer passwords, same cost factor, same library.

Validate: no separate hashing logic exists anywhere in your service.

***Downstream Modules (2, 3, 8, 10, 12) — Admin CMS***

Required: these modules build their admin CRUD routes behind @require_admin, using the identity you expose via /api/admin/auth/me.

Validate: your documentation gives these teams everything they need to protect their routes without asking you individually.

# API Governance Responsibilities

***Endpoints You Own***

| **Method** | **Route**              | **Notes**                                                      |
| ---------- | ---------------------- | -------------------------------------------------------------- |
| POST       | /api/admin/auth/login  | Body: email, password. 401 on invalid credentials              |
| POST       | /api/admin/auth/logout | Clears admin session/cookie server-side                        |
| GET        | /api/admin/auth/me     | Auth required (@require_admin). Returns current admin identity |


***Response Standards***

Follow the platform-standard shape on every endpoint:

{ "success": true, "data": { "admin": {}, "access_token": "..." } }

{ "success": false, "message": "", "errors": {} }

***No Public Admin Signup***

There is intentionally no public admin signup endpoint. If more admin/staff accounts are needed later, that requires an internal-only "invite admin" endpoint restricted to an existing super_admin — explicitly out of scope for v1 unless requested.

# Testing Responsibilities (Module-Wide)

You test the entire module, not only the admin track — this is what makes Module 1 safe to hand off.

***Coverage Required***

in1: signup, login, logout, refresh — success and failure cases, including expired/invalid tokens

in2: profile read/update, address CRUD, the single-default-address invariant

in3: forgot/reset password, including the enumeration-safety check and token expiry

in4 (yours): admin login/logout/me, and the customer/admin role-isolation test

***Role Isolation Test (Critical)***

Explicitly verify: a valid customer token is rejected by every @require_admin route, and a valid admin token is rejected by every route that expects a customer-scoped resource (e.g. cannot fetch another user's profile).

# Documentation Responsibilities

***api-reference.md***

Every endpoint in the module: method, route, auth requirement, request body, response shape, status codes — written for other module teams to integrate against without reading source code.

***test-report.md***

The results of the coverage above: what was tested, what passed, what edge cases were found and how they were resolved.

***handoff-notes.md***

The frozen interfaces every other module depends on (decorators, token shape, get_public_profile()), and any open coordination items (e.g. Module 8's pending-order deletion rule, Module 11's SMTP config) still outstanding at handoff.

***Also document the frontend routes and components each member built — pages, and the props/usage contract of AuthGuard, AddressForm, and the validators module — so other module teams’ frontends can integrate without reading source code.***

# Environment Variable Definitions

| **Variable**              | **Description**                                                            | **Owner** |
| ------------------------- | -------------------------------------------------------------------------- | --------- |
| JWT_SECRET                | Consumed from in1's config — admin tokens are signed with the same secret. | in1       |
| JWT_ACCESS_EXPIRE_MINUTES | Consumed from in1's config — same expiry policy applies to admin tokens.   | in1       |

# Security Responsibilities

***Identity Isolation***

Admin and customer tokens remain structurally distinguishable via the role claim at all times

No route ever checks token validity alone without also checking the expected role

***Account Security***

Admin login rate-limited identically to customer login — 5 attempts per 15 minutes per IP+email

No public admin signup endpoint exists, verified by direct code review

***Testing Discipline***

Every reported bug is retested after the owning member's fix, not just marked resolved on their word

# What You Depend On From Others

in1: token_helper.py, @require_admin decorator, JWT payload shape

in3: password_helper.py hashing/verification functions

# What Others Depend On From You

| **Frozen Interface**                             | **Consumers**                              |
| ------------------------------------------------ | ------------------------------------------ |
| GET /api/admin/auth/me                           | Modules 2, 3, 8, 10, 12 (Admin CMS routes) |
| docs/module1/api-reference.md & handoff-notes.md | All 11 other module teams                  |

# Code Review Expectations

Your work is reviewed by Dilip Velayutham (Team Lead) as part of the module's integration review. Be ready to demonstrate:

A customer token failing against an admin-only route, live

Full test coverage results across all four members' endpoints

Documentation that another module team could integrate against without asking you a follow-up question

# Final Module Checklist

***Admin Identity***

[ ]  admin_user.py Model

[ ]  admin_auth_service.py Complete

[ ]  Admin Login / Logout / Me Endpoints

[ ]  No Public Admin Signup Endpoint Exists

***Testing***

[ ]  in1 Endpoints Tested

[ ]  in2 Endpoints Tested

[ ]  in3 Endpoints Tested

[ ]  Role Isolation Test Passed

***Documentation***

[ ]  api-reference.md Complete

[ ]  test-report.md Complete

[ ]  handoff-notes.md Complete

***Integration***

[ ]  Merged Into in1's Integrated App With No Conflicts

***Frontend***

***[ ]  /admin/login Page Built***

***[ ]  in1 Frontend Tested***

***[ ]  in2 Frontend Tested***

***[ ]  in3 Frontend Tested***

***[ ]  Frontend Role Isolation Test Passed***

# Final Deliverables

1. models/admin_user.py

2. services/admin_auth_service.py

3. routes/admin_auth_routes.py

4. Module-Wide Test Report (test-report.md)

5. API Reference Documentation (api-reference.md)

6. Handoff Notes for Other Module Teams (handoff-notes.md)

7. Role Isolation Test Results

***8. Frontend: /admin/login page***

***9. Frontend Test Report (part of test-report.md)***

# Acceptance Criteria

The task is complete only when:

Admin login, logout, and session-check work end-to-end with correct status codes and response shapes

No public admin signup endpoint exists anywhere in the codebase

A customer token is confirmed rejected by every admin-only route, and vice versa

Every endpoint across all four members' work has been tested with documented results

Module documentation is complete and understandable without reading source code

Dilip has signed off on the module as ready for the other 11 teams to consume

/admin/login works end-to-end and is confirmed isolated from the customer session

Every frontend page/component across all four members' work has been tested with documented results

Frontend role isolation is verified: no customer session can reach admin frontend state and vice versa

# Final Note

You own two things that don't show up as features but decide whether this module can actually be trusted: whether Asil's admin identity stays completely separate from every customer, and whether everyone downstream can rely on what you say the module does.

If your implementation is stable:

The Admin CMS has a secure identity layer from day one

No customer can ever reach an admin-only action, and no admin session leaks into customer flows

Every other module team can integrate against Module 1 using your documentation alone


**Goal:**

Prove, through isolation, testing, and documentation, that Module 1 is genuinely safe for the rest of the Galxy platform to build on.
