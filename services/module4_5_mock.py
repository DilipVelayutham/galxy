# Mock integrations with Module 4 (Product & Price verification) and Module 5 (Catalog metadata)

def validate_attributes(product_id, selected_attributes):
    """
    Simulates Module 4's attribute validation logic.
    Raises ValueError for known invalid cases, returns True otherwise.
    """
    if not product_id:
        raise ValueError("product_id is required.")
        
    if product_id == "invalid_product_id":
        raise ValueError("Product not found in catalog.")
        
    if selected_attributes is not None and not isinstance(selected_attributes, dict):
        raise ValueError("selected_attributes must be a dictionary.")

    # Specific test cases for validation failures
    if selected_attributes:
        for key, val in selected_attributes.items():
            if val == "invalid_value":
                raise ValueError(f"Invalid attribute value '{val}' for attribute '{key}'.")
            if key == "invalid_key":
                raise ValueError(f"Attribute key '{key}' is not allowed for this product.")
                
    return True

def calculate_price(product_id, selected_attributes):
    """
    Simulates Module 4's price calculation logic.
    Returns a dictionary of price breakdown components.
    Every price value returned is sourced here, never trusted from the client's payload.
    """
    if product_id == "invalid_product_id":
        raise ValueError("Product not found in catalog.")

    # Baseline product pricing rules
    base_price = 100.0
    if product_id == "premium_product":
        base_price = 500.0
    elif product_id == "budget_product":
        base_price = 20.0

    # Surcharges for customizable attributes
    surcharges = 0.0
    if selected_attributes:
        for attr, val in selected_attributes.items():
            # Add surcharge depending on the selected attribute
            if val == "Gold":
                surcharges += 50.0
            elif val == "X-Large":
                surcharges += 15.0
            else:
                surcharges += 5.0 # default surcharge per attribute
                
    unit_price = base_price + surcharges
    
    return {
        "base_price": round(float(base_price), 2),
        "surcharges": round(float(surcharges), 2),
        "unit_price": round(float(unit_price), 2)
    }

def get_product_snapshot(product_id):
    """
    Simulates Module 5's catalog product retrieval for snapshots.
    """
    if product_id == "invalid_product_id":
        raise ValueError("Product not found in catalog.")
        
    name = f"Mock Product {product_id}"
    category = "General Category"
    
    if product_id == "premium_product":
        name = "Premium Gold Edition Watch"
        category = "Electronics/Watches"
    elif product_id == "budget_product":
        name = "Budget Eco Tee"
        category = "Apparel/T-Shirts"

    return {
        "name": name,
        "category": category,
        "thumbnail": f"https://example.com/assets/{product_id}_thumb.jpg",
        "description": "This is a detailed mock description of the product snapshot."
    }
