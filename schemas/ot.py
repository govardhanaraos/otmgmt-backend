from pydantic import BaseModel
from datetime import date

class OTCreate(BaseModel):
    ot_name: str
    status_id: int
    amount: float
    comments: str | None
    ot_date: date
    department_id: int
    invoice_number: str | None

class OTUpdate(OTCreate):
    pass