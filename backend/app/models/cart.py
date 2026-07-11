"""
Cart Model Schema for MongoDB.

Collection Name: `carts`

Document Shape:
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "items": [
    {
      "_id": ObjectId,
      "product_id": ObjectId,
      "category_id": ObjectId,
      "product_title": "string (snapshot)",
      "category_name": "string (snapshot)",
      "thumbnail": "cloudinary_url (snapshot)",
      "selected_attributes": {},
      "quantity": 1,
      "unit_price_estimate": 1799,
      "line_total_estimate": 1799,
      "price_breakdown": [
        {
          "name": "string",
          "price": 100
        }
      ],
      "ai_preview_image": "cloudinary_url or null",
      "custom_text": "string or null",
      "added_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "updated_at": "datetime"
}

Indexes:
- user_id (unique, enforces one cart document per authenticated user)
"""

COLLECTION_NAME = "carts"
