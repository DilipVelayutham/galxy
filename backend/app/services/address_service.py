from bson import ObjectId
from app.models.address import validate_address_data, ValidationError

def add_address(user_id, data):
    """
    Adds a new address to the user's addresses array.
    If it is the user's first address, forces is_default to True.
    If is_default is set to True, unsets it on all other addresses.
    """
    from app import db
    try:
        user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except Exception:
        raise ValidationError({"user_id": "Invalid user ID format."})
        
    validated = validate_address_data(data, partial=False)
    
    user = db.users.find_one({"_id": user_oid})
    if not user:
        raise ValidationError({"message": "User not found."})
        
    addresses = user.get('addresses', [])
    
    if not addresses:
        validated['is_default'] = True
    elif validated.get('is_default', False):
        # Set is_default to False for all other addresses
        for addr in addresses:
            addr['is_default'] = False
            
    validated['_id'] = ObjectId()
    addresses.append(validated)
    
    db.users.update_one(
        {"_id": user_oid},
        {"$set": {"addresses": addresses}}
    )
    return validated

def update_address(user_id, address_id, data):
    """
    Updates an address sub-document for a user.
    If is_default is set to True, unsets it on all other addresses.
    If is_default is set to False on the default address, selects another address to make default.
    """
    from app import db
    try:
        user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
        addr_oid = ObjectId(address_id) if isinstance(address_id, str) else address_id
    except Exception:
        raise ValidationError({"message": "Invalid user ID or address ID format."})
        
    validated = validate_address_data(data, partial=True)
    
    user = db.users.find_one({"_id": user_oid})
    if not user:
        raise ValidationError({"message": "User not found."})
        
    addresses = user.get('addresses', [])
    
    # Locate the target address
    target_addr = None
    for addr in addresses:
        if addr['_id'] == addr_oid:
            target_addr = addr
            break
            
    if not target_addr:
        raise ValidationError({"message": "Address not found."})
        
    if validated.get('is_default', False):
        # Set is_default to False for all other addresses
        for addr in addresses:
            addr['is_default'] = (addr['_id'] == addr_oid)
    elif 'is_default' in validated and not validated.get('is_default', False):
        # If client wants to set is_default to False on the current default address
        if target_addr.get('is_default', False):
            other_addresses = [a for a in addresses if a['_id'] != addr_oid]
            if not other_addresses:
                # If it's the only address, it must stay default
                validated['is_default'] = True
            else:
                # Set first other address as default
                other_addresses[0]['is_default'] = True
                target_addr['is_default'] = False
                
    # Apply updates
    for key, value in validated.items():
        target_addr[key] = value
        
    db.users.update_one(
        {"_id": user_oid},
        {"$set": {"addresses": addresses}}
    )
    return target_addr

def delete_address(user_id, address_id):
    """
    Deletes an address sub-document for a user.
    Enforces minimum count of 1.
    Blocks deleting default address if there's a pending order.
    If deleting default address and no pending order, makes another address default.
    """
    from app import db
    try:
        user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
        addr_oid = ObjectId(address_id) if isinstance(address_id, str) else address_id
    except Exception:
        raise ValidationError({"message": "Invalid user ID or address ID format."})
        
    user = db.users.find_one({"_id": user_oid})
    if not user:
        raise ValidationError({"message": "User not found."})
        
    addresses = user.get('addresses', [])
    
    target_addr = None
    for addr in addresses:
        if addr['_id'] == addr_oid:
            target_addr = addr
            break
            
    if not target_addr:
        raise ValidationError({"message": "Address not found."})
        
    if len(addresses) <= 1:
        raise ValidationError({"message": "A user must retain at least one address once they have added one."})
        
    if target_addr.get('is_default', False):
        # Check for pending orders
        pending_statuses = ['received', 'reviewed', 'quote_sent', 'confirmed', 'in_production', 'ready', 'out_for_delivery']
        pending_order = db.orders.find_one({
            "user_id": {"$in": [user_oid, str(user_oid)]},
            "status": {"$in": pending_statuses}
        })
        if pending_order:
            raise ValidationError({"message": "Cannot delete the default address while you have a pending order."})
            
        # Promote another address to default
        other_addresses = [a for a in addresses if a['_id'] != addr_oid]
        other_addresses[0]['is_default'] = True
        
    # Remove the address from the array
    new_addresses = [a for a in addresses if a['_id'] != addr_oid]
    
    db.users.update_one(
        {"_id": user_oid},
        {"$set": {"addresses": new_addresses}}
    )
    return True

def set_default(user_id, address_id):
    """
    Sets the specified address as default, unsetting all others.
    """
    from app import db
    try:
        user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
        addr_oid = ObjectId(address_id) if isinstance(address_id, str) else address_id
    except Exception:
        raise ValidationError({"message": "Invalid user ID or address ID format."})
        
    user = db.users.find_one({"_id": user_oid})
    if not user:
        raise ValidationError({"message": "User not found."})
        
    addresses = user.get('addresses', [])
    
    found = False
    for addr in addresses:
        if addr['_id'] == addr_oid:
            found = True
            break
            
    if not found:
        raise ValidationError({"message": "Address not found."})
        
    for addr in addresses:
        addr['is_default'] = (addr['_id'] == addr_oid)
        
    db.users.update_one(
        {"_id": user_oid},
        {"$set": {"addresses": addresses}}
    )
    return True
