from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True