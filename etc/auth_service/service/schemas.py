from pydantic import BaseModel, EmailStr


class LoginUserSchema(BaseModel):
    username: str
    password: str
    

class RegiesterUserSchema(BaseModel):
    name: str
    password: str
    email: EmailStr