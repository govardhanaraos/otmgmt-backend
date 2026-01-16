from pydantic import BaseModel
from uuid import UUID
from datetime import date

class OTCreate(BaseModel):
    ot_name: str
    status_id: int
    amount: float
    comments: str | None = None
    ot_date: date
    department_id: int
    invoice_number: str | None = None

class OTUpdate(BaseModel):
    ot_name: str
    status_id: int
    amount: float
    comments: str | None = None
    ot_date: date
    department_id: int
    invoice_number: str | None = None

class OTResponse(BaseModel):
    id: UUID
    reference_number: str
    ot_name: str
    status_id: int
    amount: float
    comments: str | None
    ot_date: date
    department_id: int
    invoice_number: str | None

    class Config:
        orm_mode = True