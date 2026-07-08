import datetime
from app.db import db
from app.services.auth_service import AuthService
from bson import ObjectId

def seed_db():
    print("Starting database seeding...")
    
    # 1. Clear existing collections
    db.users.delete_many({})
    db.admin_users.delete_many({})
    db.categories.delete_many({})
    db.products.delete_many({})
    db.carts.delete_many({})
    db.wishlists.delete_many({})
    db.orders.delete_many({})
    db.reviews.delete_many({})
    db.testimonials.delete_many({})
    db.site_content.delete_many({})
    db.notifications.delete_many({})
    db.ai_generations.delete_many({})
    
    # Create indexes for optimized queries & constraints
    db.reviews.create_index([("product_id", 1)])
    db.reviews.create_index([("is_approved", 1)])
    db.reviews.create_index([("user_id", 1), ("order_id", 1)])
    db.testimonials.create_index([("is_active", 1), ("display_order", 1)])
    
    # 2. Create Admin Account
    admin_hash = AuthService.hash_password("Password123")
    admin_user = {
        "_id": ObjectId("60c72b2f9b1d8b1f88888888"),
        "name": "Asil",
        "email": "asil@galxy.in",
        "password_hash": admin_hash,
        "role": "super_admin",
        "created_at": datetime.datetime.utcnow()
    }
    db.admin_users.insert_one(admin_user)
    print("Admin account created (asil@galxy.in / Password123).")
    
    # 3. Create Categories with Attribute Schemas
    cat_neon_id = ObjectId("60c72b2f9b1d8b1f00000001")
    cat_quill_id = ObjectId("60c72b2f9b1d8b1f00000002")
    cat_lamp_id = ObjectId("60c72b2f9b1d8b1f00000003")
    cat_magnet_id = ObjectId("60c72b2f9b1d8b1f00000004")
    
    categories = [
        {
            "_id": cat_neon_id,
            "slug": "neon-boards",
            "name": "Neon Name Boards",
            "description": "Premium glowing LED neon signage crafted to order.",
            "cover_image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=600",
            "banner_image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=1200",
            "accent_color": "blue",
            "display_order": 1,
            "is_active": True,
            "ai_prompt_template": "A glowing neon name board reading '{text}' in a {font} neon font with {color} glow, hanging on a dark brick wall mockup.",
            "attribute_schema": [
                {
                    "key": "text",
                    "label": "Custom Text",
                    "type": "text_input",
                    "required": True,
                    "display_order": 1,
                    "affects_ai_preview": True
                },
                {
                    "key": "font",
                    "label": "Font Style",
                    "type": "select",
                    "required": True,
                    "display_order": 2,
                    "affects_ai_preview": True,
                    "options": [
                        {"value": "cursive", "label": "Cursive Script", "price_delta": 0},
                        {"value": "bold", "label": "Bold Neon Block", "price_delta": 200},
                        {"value": "modern", "label": "Modern Serif", "price_delta": 150}
                    ]
                },
                {
                    "key": "color",
                    "label": "Neon Glow Color",
                    "type": "color_swatch",
                    "required": True,
                    "display_order": 3,
                    "affects_ai_preview": True,
                    "options": [
                        {"value": "pink", "label": "Pink / Magenta (#FF2E8A)", "price_delta": 0},
                        {"value": "blue", "label": "Electric Blue (#18E7FF)", "price_delta": 0},
                        {"value": "violet", "label": "Deep Violet (#9B5CFF)", "price_delta": 100},
                        {"value": "yellow", "label": "Signal Yellow (#FFD84D)", "price_delta": 50}
                    ]
                },
                {
                    "key": "backing",
                    "label": "Acrylic Backing Cut",
                    "type": "select",
                    "required": True,
                    "display_order": 4,
                    "affects_ai_preview": False,
                    "options": [
                        {"value": "cut_to_shape", "label": "Contoured / Cut-to-Shape", "price_delta": 0},
                        {"value": "whole_board", "label": "Whole Rectangular Board", "price_delta": 150}
                    ]
                },
                {
                    "key": "chain",
                    "label": "Hanging Chain Set",
                    "type": "toggle",
                    "required": False,
                    "display_order": 5,
                    "affects_ai_preview": False,
                    "options": [
                        {"value": "true", "label": "Included Hanging Chain (+100)", "price_delta": 100}
                    ]
                }
            ],
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "_id": cat_quill_id,
            "slug": "quilling-art",
            "name": "Quilling Art Frames",
            "description": "Bespoke handcrafted paper quilling artwork.",
            "cover_image": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=600",
            "banner_image": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=1200",
            "accent_color": "pink",
            "display_order": 2,
            "is_active": True,
            "ai_prompt_template": "Paper quilled flower frame showing name '{text}' surrounded by colorful paper scrolls inside an elegant frame.",
            "attribute_schema": [
                {
                    "key": "text",
                    "label": "Engraved Initials/Name",
                    "type": "text_input",
                    "required": True,
                    "display_order": 1,
                    "affects_ai_preview": True
                },
                {
                    "key": "frame_size",
                    "label": "Frame Size",
                    "type": "select",
                    "required": True,
                    "display_order": 2,
                    "affects_ai_preview": False,
                    "options": [
                        {"value": "A4", "label": "Standard A4 Size", "price_delta": 0},
                        {"value": "A3", "label": "Large A3 Size Frame", "price_delta": 500}
                    ]
                },
                {
                    "key": "flower_density",
                    "label": "Floral density",
                    "type": "slider",
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "required": True,
                    "display_order": 3,
                    "affects_ai_preview": True
                }
            ],
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "_id": cat_lamp_id,
            "slug": "acrylic-lamps",
            "name": "Acrylic Moonlight Lamps",
            "description": "Engraved acrylic lamps with customizable lighting stands.",
            "cover_image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&q=80&w=600",
            "banner_image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&q=80&w=1200",
            "accent_color": "violet",
            "display_order": 3,
            "is_active": True,
            "ai_prompt_template": "An acrylic circular lamp engraved with name '{text}', glowing warmly on a matching {base_type} base.",
            "attribute_schema": [
                {
                    "key": "text",
                    "label": "Engraved Name/Line",
                    "type": "text_input",
                    "required": True,
                    "display_order": 1,
                    "affects_ai_preview": True
                },
                {
                    "key": "base_type",
                    "label": "Stand Base Type",
                    "type": "select",
                    "required": True,
                    "display_order": 2,
                    "affects_ai_preview": True,
                    "options": [
                        {"value": "wooden_warm", "label": "Natural Wood (Warm Light)", "price_delta": 0},
                        {"value": "wooden_rgb", "label": "Natural Wood (Multicolor RGB)", "price_delta": 250}
                    ]
                }
            ],
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "_id": cat_magnet_id,
            "slug": "fridge-magnets",
            "name": "Custom Fridge Magnets",
            "description": "Personalized magnets featuring custom text and prints.",
            "cover_image": "https://images.unsplash.com/photo-1590480397754-3838a5572575?auto=format&fit=crop&q=80&w=600",
            "banner_image": "https://images.unsplash.com/photo-1590480397754-3838a5572575?auto=format&fit=crop&q=80&w=1200",
            "accent_color": "yellow",
            "display_order": 4,
            "is_active": True,
            "ai_prompt_template": "A cute polaroid-style fridge magnet with text '{text}'.",
            "attribute_schema": [
                {
                    "key": "text",
                    "label": "Caption Text",
                    "type": "text_input",
                    "required": True,
                    "display_order": 1,
                    "affects_ai_preview": True
                },
                {
                    "key": "shape",
                    "label": "Magnet Shape",
                    "type": "select",
                    "required": True,
                    "display_order": 2,
                    "affects_ai_preview": False,
                    "options": [
                        {"value": "polaroid", "label": "Polaroid Snapshot", "price_delta": 0},
                        {"value": "circular", "label": "Classic Circular Badge", "price_delta": 0},
                        {"value": "square", "label": "Classic Square Board", "price_delta": 0}
                    ]
                }
            ],
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
    ]
    
    db.categories.insert_many(categories)
    print("Categories seeded successfully.")
    
    # 4. Create Products
    products = [
        {
            "_id": ObjectId("60c72b2f9b1d8b1f00000101"),
            "category_id": cat_neon_id,
            "title": "Bespoke Custom Neon Sign",
            "slug": "custom-neon-sign",
            "type": "fully_custom",
            "base_price": 1500.00,
            "images": ["https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=600"],
            "thumbnail": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=600",
            "description": "Design your own custom LED neon board. Type your name, select a glowing neon color, pick a font, and order your personalized art.",
            "specifications": {
                "Material": "Flexible LED Neon Tubing",
                "Backing": "High Quality transparent Acrylic",
                "Volt": "12V Adapter included"
            },
            "default_attributes": {
                "text": "Dream",
                "font": "cursive",
                "color": "pink",
                "backing": "cut_to_shape",
                "chain": False
            },
            "stock_status": "made_to_order",
            "tags": ["neon", "custom", "lighting", "room-decor"],
            "is_featured": True,
            "is_active": True,
            "views": 250,
            "rating_avg": 5.0,
            "rating_count": 1,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "_id": ObjectId("60c72b2f9b1d8b1f00000102"),
            "category_id": cat_quill_id,
            "title": "Quilled Floral Initials Frame",
            "slug": "quilled-floral-frame",
            "type": "fully_custom",
            "base_price": 1200.00,
            "images": ["https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=600"],
            "thumbnail": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=600",
            "description": "Intricate paper quilled designs outlining your name or couple initials. Handcrafted with colorful high-grade paper coils in Chennai.",
            "specifications": {
                "Material": "Premium Art Board, Solid Frame",
                "Dimensions": "21 x 29.7 cm (A4)"
            },
            "default_attributes": {
                "text": "A & S",
                "frame_size": "A4",
                "flower_density": 3
            },
            "stock_status": "made_to_order",
            "tags": ["quilling", "craft", "gift", "frame"],
            "is_featured": True,
            "is_active": True,
            "views": 180,
            "rating_avg": 0,
            "rating_count": 0,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "_id": ObjectId("60c72b2f9b1d8b1f00000103"),
            "category_id": cat_lamp_id,
            "title": "Custom Acrylic Moonlight Lamp",
            "slug": "custom-moonlight-lamp",
            "type": "fully_custom",
            "base_price": 1800.00,
            "images": ["https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&q=80&w=600"],
            "thumbnail": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&q=80&w=600",
            "description": "Engraved circular moon lamps resting on natural wooden bases. Casts a warm glowing engraving of your customizable message.",
            "specifications": {
                "Material": "Shatterproof transparent acrylic",
                "Base": "Solid Warm Pine Wood stand"
            },
            "default_attributes": {
                "text": "A&S",
                "base_type": "wooden_warm"
            },
            "stock_status": "made_to_order",
            "tags": ["lamp", "acrylic", "nightlight", "moonlight"],
            "is_featured": False,
            "is_active": True,
            "views": 95,
            "rating_avg": 0,
            "rating_count": 0,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
    ]
    
    db.products.insert_many(products)
    print("Products seeded successfully.")
    
    # 5. Seed Site Content (CMS)
    site_content = [
        {
            "section": "hero",
            "content": {
                "title": "CRAFTING NEON GLOWS",
                "tagline": "BESPOKE LIGHTING & ART STUDIO",
                "description": "Transform your space with handcrafted glowing neon signs, customized quilled frames, and acrylic nightlights made to order.",
                "cta_text": "START DESIGNING",
                "cta_link": "/categories/neon-boards"
            },
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "section": "about",
            "content": {
                "story": "Welcome to GALXY, a custom lighting and craft studio based in Chennai. Led by Asil, we build stunning custom neon designs, Moonlight Acrylic Lamps, paper quilling gifts, and storefront board signage.",
                "artist_profile": "Every neon sign and quilling artwork is hand-bent, framed, and tested directly in our studio."
            },
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "section": "contact",
            "content": {
                "phone": "+91 98401 23456",
                "email": "asil@galxy.in",
                "instagram": "@galxy.in",
                "whatsapp": "919840123456"
            },
            "updated_at": datetime.datetime.utcnow()
        },
        {
            "section": "footer",
            "content": {
                "copyright": "© 2026 GALXY Studio. Handcrafted in India.",
                "links": [
                    {"label": "Terms of Inquiry", "url": "/terms"},
                    {"label": "Privacy Policy", "url": "/privacy"}
                ]
            },
            "updated_at": datetime.datetime.utcnow()
        }
    ]
    db.site_content.insert_many(site_content)
    print("CMS site content seeded.")
    
    # 6. Seed Sample Review (Delivered order mock reviewer)
    mock_review = {
        "product_id": ObjectId("60c72b2f9b1d8b1f00000101"),
        "user_id": ObjectId("60c72b2f9b1d8b1f99999999"),
        "order_id": ObjectId("60c72b2f9b1d8b1f77777777"),
        "order_number": "GLX-2026-00001",
        "rating": 5,
        "comment": "Absolutely spectacular! The pink glow looks incredibly vibrant in my gaming room. Asil confirmed all specifications with me over WhatsApp, and the shipping was fast. Handcraft quality at its finest!",
        "images": ["https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=300"],
        "customer_name": "Rohan",
        "is_approved": True,
        "is_featured": True,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }
    db.reviews.insert_one(mock_review)
    
    # Seed Testimonial
    db.testimonials.insert_one({
        "source": "review",
        "review_id": mock_review["_id"],
        "customer_name": "Rohan",
        "customer_location": "Chennai",
        "quote": "Absolutely spectacular! The pink glow looks incredibly vibrant. Handcraft quality at its finest!",
        "rating": 5,
        "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=300",
        "display_order": 1,
        "is_active": True,
        "created_at": datetime.datetime.utcnow()
    })
    print("Sample reviews and testimonials seeded.")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_db()
