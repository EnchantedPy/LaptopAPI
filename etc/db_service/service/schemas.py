from typing import List, Optional, TypedDict
from pydantic import BaseModel, EmailStr


class UserAddSchema(BaseModel):
    name: str
    password: str
    email: EmailStr


class UserUpdateSchema(BaseModel):
    name: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
    id: int


class UserDeleteSchema(BaseModel):
    id: int


class LaptopSchema(BaseModel):
    brand: str
    cpu: str
    gpu: str
    price_range: List[int]
