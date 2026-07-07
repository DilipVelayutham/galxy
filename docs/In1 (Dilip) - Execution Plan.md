GALXY — MODULE 1: AUTH & USER ACCOUNTS
DILIP VELAYUTHAM — TEAM LEAD, AUTH ARCHITECT, INTEGRATION LEAD
MODULE EXECUTION DOCUMENT

Intern Information
Intern Code: GLX-M1-01
Role: Team Lead, Auth Architect, Integration Lead
Team: Module 1 — Auth & User Accounts
Branch Name: in1-dilip
Primary Responsibility:
JWT Architecture, Token & Session Lifecycle, Middleware Governance, Cross-Module Auth Contract, Integration & Merge Ownership.
Reports To: Project Mentor / LTI Technology Technical Lead
Review Cycle: Continuous — per milestone review
Timeline: Module 1 delivery cycle (parallel with 11 other module teams)
Priority Level: CRITICAL
Your Role In The Project
You are responsible for building and governing the complete authentication foundation of the Galxy backend.
Every other module in the platform — Cart, Wishlist, Orders, Reviews, and the entire Admin CMS across Modules 2, 3, 10, and 12 — sits behind the middleware you build. Nothing else in the system can be safely built until your contract is stable.
Without your work:
Backend routes cannot verify who is calling them
Admin and customer sessions cannot be distinguished
Cart, Wishlist, Orders, and Reviews cannot identify their owning user
The entire Admin CMS (Categories, Products, Orders, Site Content) remains unprotected
No other module can be safely integrated into the running application

Your responsibility is NOT:
Building profile or address CRUD (owned by in2)
Building password recovery or SMTP integration (owned by in3)
Building admin route logic or admin CRUD screens (owned by in4)
Building frontend components outside the auth-session domain (profile/address UI is in2’s, password-recovery pages are in3’s, admin UI is in4’s)

Your responsibility IS:
Designing the Module 1 architecture
Owning the complete JWT token lifecycle
Building and freezing the auth middleware/decorators
Integrating in2, in3, and in4's work into one running module
Defining and enforcing the module's API and security standards
Reviewing all four members' implementations
Giving final approval before Module 1 is considered handoff-ready
Building the frontend session layer: AuthContext (in-memory access token) and the AuthGuard protected-route wrapper
Building the shared AuthForm shell component and the /signup and /login pages
Implementing silent refresh on app load and the global 401-triggers-one-silent-refresh interceptor logic
Integrating in2, in3, and in4's frontend pages/components into one consistent Next.js module, matching the design system
Module Mission
By the end of this module, the following must all be true:
✓  Architecture is finalized
✓  Repository structure is finalized
✓  JWT token lifecycle (issue, verify, refresh, expire) functions correctly
✓  Auth middleware decorators function and are frozen
✓  Signup, login, logout, and refresh endpoints function end-to-end
✓  Cross-module auth contract is published to the other 11 teams
✓  Environment configuration is finalized
✓  in2, in3, and in4's work is fully integrated into one Flask app
✓  Security requirements are validated
✓  Module 1 is ready for every other module to consume
✓  AuthContext and AuthGuard function correctly and are frozen for other modules to consume
✓  /signup and /login pages work end-to-end against your backend endpoints
✓  Silent refresh on app load and on 401 works without a visible "logged out" flash
✓  in2, in3, and in4's frontend work is integrated into one Next.js app with no routing/component conflicts
Repository Structure Ownership
backend/

app/
├── models/
│   ├── user.py
│   ├── admin_user.py
│   └── address.py
│
├── services/
│   ├── auth_service.py
│   ├── user_service.py
│   ├── address_service.py
│   └── admin_auth_service.py
│
├── routes/
│   ├── auth_routes.py
│   ├── user_routes.py
│   └── admin_auth_routes.py
│
├── configs/
│   └── jwt_config.py
│
├── utils/
│   ├── password_helper.py
│   ├── token_helper.py
│   ├── validators.py
│   └── auth_middleware.py
│
└── __init__.py            — app factory, blueprint registration

docs/
├── architecture/          — module architecture decisions
├── api-contracts/         — frozen interface documentation
└── governance/            — standards, review notes

You own the top-level app/ skeleton, __init__.py, configs/, and utils/ entirely. models/, services/, and routes/ are shared files where you own the auth-specific sections and in2/in3/in4 own theirs — see the Cross-Module Integration section for the exact split.

frontend/ (Next.js)

app/
├── (public)/
│   ├── signup/page.tsx
│   └── login/page.tsx
│
└── (account)/               — layout wraps every nested page in AuthGuard

components/
├── auth/AuthForm.tsx
└── auth/AuthGuard.tsx

context/
└── AuthContext.tsx

You own components/auth/AuthForm.tsx, components/auth/AuthGuard.tsx, context/AuthContext.tsx, and the (public)/signup and (public)/login pages entirely. The (account)/ layout is shared: you own the AuthGuard wrapper it renders; in2 owns the pages nested inside it.
System Architecture Responsibilities
You own the complete Module 1 architecture.
Auth Domain Architecture
Modules within your domain:
Customer Authentication (Signup, Login, Logout, Refresh)
Admin Authentication (isolated login/session track)
Session & Token Management
Profile & Address Data (architecture reviewed by you, built by in2)
Password Recovery (architecture reviewed by you, built by in3)
Technical Architecture
Define:
Backend folder structure and module boundaries
Token architecture (access/refresh pair, claim shape, expiry policy)
Middleware/decorator architecture
Service-layer conventions (one service file per domain, no cross-file business logic)
Standard API response contract
Auth Security Architecture (Critical Compliance)
Implement:
A single, centralized auth middleware layer — no route may implement its own ad hoc token check.
Role-based access enforcement on every protected route via @require_auth / @require_admin.
Enforce: No route touching users, admin_users, or any dependent collection (carts, wishlists, orders, reviews) may execute without passing through @require_auth or @require_admin.
Token Payload Schema — frozen once published:
{ "sub": "<user_id>", "role": "customer" | "super_admin", "exp": <timestamp> }
Standards
Approve:
Naming standards (files, functions, routes)
Folder standards
Validation standards
API standards (request/response shape, status codes)
Error handling standards
Authentication & Token Responsibilities
You own the complete token and session lifecycle.
JWT Lifecycle
Implement:
Token encoding, decoding, and verification (token_helper.py)
Access token issuance (short-lived) and refresh token issuance (long-lived)
Expiry enforcement and distinct handling of expired vs. invalid signatures
Session Validation
Implement:
httpOnly, secure, sameSite refresh cookie handling
Silent access-token renewal via the refresh endpoint
Logout — server-side invalidation of the refresh cookie
Role Synchronization
Validate:
Customer tokens and admin tokens are structurally distinguishable via the role claim
Every protected route checks the expected role, not just token validity
A valid customer token can never pass an admin-only check, and vice versa
Protected Access
Ensure the following cannot be reached without a valid, verified token: Cart, Wishlist, Orders, Reviews (customer-facing) and Categories, Products, Orders, Site Content, Analytics (admin-facing) across Modules 2, 3, 6, 7, 8, 9, 10, 12.
Frontend Responsibilities
Per the Module 1 frontend specification, you own the session-management layer of the frontend — the part that makes every other page in the app behave as "logged in" or "logged out" correctly.
Pages & Components You Own
/signup, /login — built on the shared AuthForm shell, which swaps its field set between signup and login mode
AuthForm — shared shell component consumed by both pages
AuthGuard — wraps protected routes, redirects to /login if no valid session exists
State Management (Frozen Contract)
Access token held in memory only (React Context, e.g. AuthContext) — never in localStorage, to avoid XSS token theft
Refresh token lives in the httpOnly cookie set by your backend; the frontend never reads or touches it directly
On app load, silently call /api/auth/refresh once to hydrate the session if a valid refresh cookie exists — show a brief loading state, never a flash of "logged out"
On any 401 from any API call anywhere in the app, trigger one silent refresh attempt; if that also fails, clear auth state and redirect to /login
Key Interactions
Signup/login forms validate inline before submit (email format, password strength) — the rules come from in3’s shared validator module; you wire them into AuthForm so errors feel instant and mirror the server-side rules
AuthForm swaps its field set (signup vs. login) without a page transition flash
Design System Compliance
Forms use the dark glassmorphism panel treatment; primary CTA buttons get the neon glow
Validation errors use a warning tint, never a clashing red
You are the frontend architecture owner for the module — enforce these rules consistently across in2, in3, and in4’s components during integration
Cross-Module Integration
in2 Integration — Profile & Address (Naresh Kumar)
Required Contracts: request.user._id attachment, base models/user.py document shape, get_public_profile() as the sole external lookup.
Validate: schema consistency between your auth fields and his profile/address fields on the same document; no duplicate user lookups elsewhere in the codebase.
Frontend: in2’s /account/profile and /account/addresses pages must render inside your AuthGuard-protected (account)/ layout — confirm the redirect-to-login behavior works for both.
in3 Integration — Password Recovery & SMTP (Tharani Jayaprakash)
Required Contracts: password_helper.py hashing/verification functions consumed by your signup/login logic; forgot/reset-password handlers living inside the auth service and route files you also own.
Validate: file-section ownership inside the shared auth_service.py/auth_routes.py is agreed to avoid merge conflicts; SMTP configuration is not duplicated with Module 11 (Notifications).
Frontend: in3’s shared validators module is consumed inside your AuthForm component for signup/login — do not duplicate validation logic in AuthForm itself.
in4 Integration — Admin Authentication (Arun Kumar)
Required Contracts: reuse of your token_helper.py for encode/decode; adherence to the role-claim convention you define.
Validate: complete isolation between the customer and admin identity tracks; admin/customer role-bypass tests pass.
Frontend: in4’s /admin/login page reuses your AuthContext pattern conceptually but must be a fully separate admin session — never share the same context instance or storage key as the customer AuthContext.
Downstream Modules (2, 3, 6, 7, 8, 9, 10, 12)
Required: a stable, documented @require_auth / @require_admin contract, and the standard 401 / 403 error codes.
Validate: no downstream route bypasses the middleware layer; the contract has not changed shape since publication.
Every other module’s frontend pages that require a logged-in customer wrap themselves in your AuthGuard component; treat its usage contract as frozen once published.
Infrastructure Governance Responsibilities
Environment Setup
Configure separate values for:
Development
Testing
Production
Manage: secrets, environment variables, and runtime settings — nothing sensitive is ever hardcoded or committed.
Config Governance
jwt_config.py is the single source of truth for all token timing and secret values. No other file may read JWT settings directly from the environment.
Environment Variable Definitions
API Governance Responsibilities
Response Standards
Standardize across every endpoint in the module:
{ "success": true, "message": "", "data": {} }
{ "success": false, "message": "", "errors": {} }
Request Standards
Define: payload structure for auth requests, and pagination/filtering conventions for any list-returning endpoint added later.
Documentation Standards
Approve: endpoint contracts and integration documentation before they are shared with the other 11 module teams.
Security Responsibilities
Authentication Security
JWT signature validation on every request
Access token expiry enforced at 15 minutes
Refresh token rotation and httpOnly/secure/sameSite cookie enforcement
Infrastructure Security
Environment isolation between dev/test/production secrets
CORS restricted to the actual frontend origin(s) in production — never a wildcard
Account Security
Passwords hashed with bcrypt, cost factor 12 — never stored or logged in plaintext
Rate limiting on /api/auth/login and /api/admin/auth/login — 5 attempts per 15 minutes per IP+email
Forgot-password responses never reveal whether an email exists in the system
Reset tokens are single-use, expire in 30 minutes, and are invalidated after a successful reset
Integration & Handoff Readiness Responsibilities
Module Packaging
Confirm all blueprints (auth, user, admin_auth) register cleanly in one Flask app factory
Confirm no route or import collisions exist across in1/in2/in3/in4's files
Handoff Validation
Confirm the frozen interfaces (below) are stable and documented
Confirm the module can be safely consumed by all 11 other module teams without further changes
Code Review Responsibilities
Review work from:
Naresh Kumar → Profile & Address CRUD, User Service, Address Service
Tharani Jayaprakash → Password Recovery, Validators, SMTP Integration
Arun Kumar → Admin Authentication, Admin Routes, Testing, Documentation
Team Governance Responsibilities
Ensure:
Branch discipline across all four members
PR reviews before any merge into the shared module branch
Merge approvals — you are the final approver for Module 1
Technical consistency with the standards you defined
Handoff readiness before other module teams begin integrating against you
Approve merges only after validation against the frozen contract.
Review Expectations
Review 1 — Architecture & Middleware
Folder structure, token architecture, middleware design
Review 2 — Service Integration & Security
in2/in3/in4 integration correctness, security requirements validated
Review 3 — Full Module Integration & Handoff Readiness
End-to-end module test, frozen contract confirmed stable, ready for other teams
Final Module Checklist
Architecture
[ ]  Architecture Design
[ ]  Technical Standards
[ ]  Repository Structure
[ ]  Auth Security Architecture
Authentication
[ ]  JWT Token Lifecycle
[ ]  Auth Middleware (frozen)
[ ]  Signup / Login / Logout / Refresh
Integration
[ ]  in2 Integration (Profile & Address)
[ ]  in3 Integration (Password Recovery & SMTP)
[ ]  in4 Integration (Admin Auth)
Infrastructure
[ ]  Environment Setup
[ ]  Environment Variable Governance
[ ]  Config Governance
Governance
[ ]  API Standards
[ ]  Documentation
[ ]  Security Validation
Handoff
[ ]  Module Integration Review
[ ]  Cross-Module Contract Published
[ ]  Final Technical Approval
Frontend
[ ]  AuthContext (Session State) Built
[ ]  AuthGuard (Protected Routes) Built
[ ]  Signup / Login Pages Built
[ ]  Silent Refresh (App Load + On 401) Working
[ ]  Frontend Integration of in2/in3/in4 Complete
Final Deliverables
1. Module 1 Architecture Document
2. JWT Token Lifecycle Implementation (token_helper.py)
3. Auth Middleware / Decorators (auth_middleware.py)
4. Signup, Login, Logout, Refresh Endpoints
5. Cross-Module Auth Contract Documentation
6. Environment & Secrets Configuration
7. API Governance Documentation
8. Security Validation Report
9. Integration Test Report (in2/in3/in4 merged)
10. Handoff Readiness Report
11. Final Technical Approval
12. Frontend: AuthContext.tsx, AuthGuard.tsx, AuthForm.tsx
13. Frontend: /signup and /login pages
Acceptance Criteria
The task is complete only when:
Architecture is finalized
Token lifecycle and middleware function correctly and are frozen
Signup, login, logout, and refresh all work end-to-end
in2, in3, and in4's work is fully integrated with no route/import collisions
Security requirements are satisfied
Cross-module contract is documented and published
Module 1 is approved as ready for the other 11 module teams to consume
Signup and login pages work end-to-end against the live backend, with inline validation and correct error states
AuthGuard correctly redirects unauthenticated users and never flashes a "logged out" state on a valid session
All four members' frontend pages are integrated into one Next.js app with a consistent design system
Final Note
You are building the identity backbone of the entire Galxy platform.
If your implementation is stable:
Every other module can build and integrate independently
Customer and admin sessions stay secure and predictable
Cross-module integration remains conflict-free
The platform becomes safe to ship to production

Goal:
Build a secure, stable, and cleanly documented authentication foundation that every other Galxy module can depend on without ever needing to think about identity again.