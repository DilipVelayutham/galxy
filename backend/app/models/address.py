import re
from bson import ObjectId

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))

def validate_address_data(data, partial=False):
    errors = {}
    
    # Required fields for full create
    required_fields = ['label', 'line1', 'city', 'state', 'pincode']
    
    if not partial:
        for field in required_fields:
            if field not in data or data[field] is None or not str(data[field]).strip():
                errors[field] = f"{field.capitalize()} is required."
                
    # Validate label if present
    if 'label' in data:
        label = data['label']
        if label not in ['Home', 'Work', 'Other']:
            errors['label'] = "Label must be one of: Home, Work, Other."
            
    # Validate pincode if present
    if 'pincode' in data:
        pincode = str(data['pincode']).strip()
        if not re.match(r'^\d{6}$', pincode):
            errors['pincode'] = "Pincode must be a 6-digit numeric code."
            
    # Validate other fields format if present
    for field in ['line1', 'city', 'state']:
        if field in data:
            val = data[field]
            if val is not None and not str(val).strip():
                errors[field] = f"{field.capitalize()} cannot be empty."

    if errors:
        raise ValidationError(errors)
        
    # Build clean validated data
    validated = {}
    for field in ['label', 'line1', 'line2', 'city', 'state', 'pincode', 'is_default']:
        if field in data:
            if field == 'is_default':
                validated[field] = bool(data[field])
            else:
                validated[field] = str(data[field]).strip() if data[field] is not None else ""
                
    return validated
