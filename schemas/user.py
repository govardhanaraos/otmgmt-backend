from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    full_name: str
    role: str
    department_id: int | None = None
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    department_id: int | None

    class Config:
        orm_mode = True