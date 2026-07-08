from bson import ObjectId

def serialize_doc(doc):
    """Converts MongoDB documents into JSON-serializable dicts, renaming _id to id."""
    if doc is None:
        return None
    
    serialized = {}
    for key, value in doc.items():
        if key == "_id":
            serialized["id"] = str(value)
        elif isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, dict):
            serialized[key] = serialize_doc(value)
        elif isinstance(value, list):
            serialized[key] = [
                serialize_doc(item) if isinstance(item, dict)
                else (str(item) if isinstance(item, ObjectId) else item)
                for item in value
            ]
        else:
            serialized[key] = value
            
    return serialized

def serialize_docs(docs):
    """Converts MongoDB cursor/list of docs to serialized form."""
    return [serialize_doc(doc) for doc in docs]

def paginate_query(collection, query, page=1, limit=20, sort_by=None, sort_order=1):
    """Paginates MongoDB query according to Galxy's standard response contract."""
    try:
        page = max(1, int(page))
        limit = max(1, min(100, int(limit)))
    except (ValueError, TypeError):
        page = 1
        limit = 20

    total_records = collection.count_documents(query)
    total_pages = (total_records + limit - 1) // limit if total_records > 0 else 0

    cursor = collection.find(query)
    if sort_by:
        cursor = cursor.sort(sort_by, sort_order)
    
    skip = (page - 1) * limit
    cursor = cursor.skip(skip).limit(limit)

    results = serialize_docs(cursor)

    return {
        "data": results,
        "page": page,
        "limit": limit,
        "total": total_records,
        "totalPages": total_pages
    }
