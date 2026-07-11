import re
from bson import ObjectId


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


class Address:
    @staticmethod
    def create_document(label, line1, line2, city, state, pincode, is_default=False):
        """
        Creates a dictionary representation of an address subdocument.
        """
        return {
            "_id": ObjectId(),
            "label": label.strip() if label else "Home",
            "line1": line1.strip() if line1 else "",
            "line2": line2.strip() if line2 else "",
            "city": city.strip() if city else "",
            "state": state.strip() if state else "",
            "pincode": pincode.strip() if pincode else "",
            "is_default": bool(is_default)
        }

    @staticmethod
    def to_dict(address_doc):
        """
        Converts ObjectId _id to string for JSON exposure.
        """
        if not address_doc:
            return None

        doc = dict(address_doc)

        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

        return doc


def validate_address_data(data, partial=False):
    """
    Validates address payload.
    Returns a cleaned dictionary or raises ValidationError.
    """
    errors = {}

    required_fields = [
        "label",
        "line1",
        "city",
        "state",
        "pincode",
    ]

    if not partial:
        for field in required_fields:
            if (
                field not in data
                or data[field] is None
                or not str(data[field]).strip()
            ):
                errors[field] = f"{field.capitalize()} is required."

    if "label" in data:
        if data["label"] not in ["Home", "Work", "Other"]:
            errors["label"] = "Label must be one of: Home, Work, Other."

    if "pincode" in data:
        pincode = str(data["pincode"]).strip()

        if not re.match(r"^\d{6}$", pincode):
            errors["pincode"] = "Pincode must be a 6-digit numeric code."

    for field in ["line1", "city", "state"]:
        if field in data:
            value = data[field]

            if value is not None and not str(value).strip():
                errors[field] = f"{field.capitalize()} cannot be empty."

    if errors:
        raise ValidationError(errors)

    validated = {}

    for field in [
        "label",
        "line1",
        "line2",
        "city",
        "state",
        "pincode",
        "is_default",
    ]:
        if field in data:
            if field == "is_default":
                validated[field] = bool(data[field])
            else:
                validated[field] = (
                    str(data[field]).strip()
                    if data[field] is not None
                    else ""
                )

    return validated