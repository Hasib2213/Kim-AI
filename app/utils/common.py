from datetime import datetime, timezone
from bson import ObjectId


def utcnow():
    return datetime.now(timezone.utc)


def stringify_id(doc):
    if doc is None:
        return None
    if isinstance(doc, list):
        return [stringify_id(x) for x in doc]
    if isinstance(doc, dict):
        out = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                out[k] = str(v)
            elif isinstance(v, dict):
                out[k] = stringify_id(v)
            elif isinstance(v, list):
                out[k] = stringify_id(v)
            else:
                out[k] = v
        return out
    return doc
