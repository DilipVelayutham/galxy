GALXY WEBSITE PROJECT

Module 3 — Products (Public + Admin)

Team: LTI26INT07

ILAKYA S L

R.M.K. Engineering College

Role on Team: Intern

  ASSIGNED WORK AREA: BACKEND DEVELOPER — ADMIN API & VALIDATION  

Mobile: 9790781377   |   Email: ilakyasl77@gmail.com

1. Your Scope

You own the Admin-facing backend for Module 3: all @require_admin routes for creating, editing, soft-deleting, and managing images on products, plus the validation rules that keep bad data out of the storefront.

You build on top of the product model and core services — coordinate with the teammate who owns product_service.py and product_image_service.py so you call their functions rather than duplicating logic.

2. Your Folder Structure (Flask)

app/  routes/    admin_product_routes.py        <- YOU OWN (admin CRUD)  services/    product_service.py             <- shared, call don't duplicate    product_image_service.py       <- shared, call don't duplicate  utils/    validators/      product_validator.py         <- YOU OWN (validation rules below)

3. Admin Routes You Implement

GET /api/admin/products

Returns all products including inactive/out-of-stock, with admin-level filters (category, stock_status, is_active) and full pagination.

POST /api/admin/products

Body: {  "category_id","title","type","base_price","description",  "specifications":{}, "default_attributes":{}, "stock_status",  "tags":[], "is_featured"}

slug is auto-generated from title, server-side

category_slug is denormalized from category_id at creation time

images/thumbnail are set via the separate upload endpoint below — product must exist first

VALIDATION: default_attributes keys must exist in the category's attribute_schema — reject with 400 + field errors if a key doesn't match (call Module 2's schema_validator or a shared util)

Success 201: { "success": true, "data": {...product...} }

PUT /api/admin/products/:id

Accepts any subset of product fields except slug and category_id. Changing category_id after creation is intentionally disallowed — if a product genuinely belongs elsewhere, admin should deactivate and recreate it, since default_attributes would otherwise reference a stale schema.

DELETE /api/admin/products/:id

Soft-delete only (is_active: false). Existing cart items, wishlist entries, and past orders reference product_id — a hard delete would break historical order display.

POST /api/admin/products/:id/images

Multipart form upload, one or more files. Uploads to Cloudinary via product_image_service, appends resulting URLs to the images array. If the product has no thumbnail yet, the first uploaded image auto-sets as thumbnail.

DELETE /api/admin/products/:id/images

Body: { "image_url" }. Removes the image from the array and deletes it from Cloudinary. If the removed image was the thumbnail, admin must set a new one explicitly via PUT — never auto-pick, it could silently swap the featured image.

PUT /api/admin/products/:id/thumbnail

Body: { "image_url" } — must already be present in the product's images array.

4. Validation Rules You Enforce


--- Table Start ---
Field | Rule
title | Required, 3–120 characters
base_price | Required, positive number
type | Must be pre_designed or fully_custom
category_id | Must reference an existing, active category
default_attributes | Every key must exist in the category's attribute_schema; every value valid for that attribute (or within min/max for slider/number types). Reject invalid combos at create/edit time.
stock_status | Enum only, no free text
images | At least one image required before is_active can be true — soft check with admin warning, not a hard block (drafts allowed)
--- Table End ---

5. Coordination Notes

Coordinate default_attributes validation against Module 2's attribute_schema format before you start — don't guess the shape.

rating_avg / rating_count are read-only in your admin routes — never let PUT /api/admin/products/:id overwrite them, Module 9 owns writes to those two fields.

General media upload infra is shared with Module 10 — if product_image_service and Module 10's uploader duplicate Cloudinary boilerplate, consolidate into one shared cloudinary_helper.py in app/utils/.
