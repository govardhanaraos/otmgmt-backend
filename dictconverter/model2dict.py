import uuid
from decimal import Decimal
from datetime import datetime, date

def model_to_dict(model):
    result = {}
    for c in model.__table__.columns:
        value = getattr(model, c.name)

        if isinstance(value, uuid.UUID):
            value = str(value)
        elif isinstance(value, (datetime, date)):
            value = value.isoformat()
        elif isinstance(value, Decimal):
            value = float(value)

        result[c.name] = value
    return result