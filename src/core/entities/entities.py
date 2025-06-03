from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Laptop(BaseModel):
      id: int
      user_id: int
      brand: str
      cpu: str
      gpu: str
      igpu: str
      ram: int
      storage: int
      diagonal: float
      min_price: int
      max_price: int
      
      class Config:
        from_attributes = True
      

class Activity(BaseModel):
      id: int
      user_id: int
      detail: str
      timestamp: datetime
      
      class Config:
        from_attributes = True
      

class User(BaseModel):
       id: int
       username: str
       hashed_password: bytes
       email: EmailStr
       active: bool
       role: str
       
       class Config:
        from_attributes = True
        

class TokenPayload(BaseModel):
    sub: int
    username: Optional[str] # only for access token
    email: Optional[EmailStr] # only for access token
    role: str
    exp: int
    iat: int
    jti: uuid.UUID