from bson import ObjectId

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
