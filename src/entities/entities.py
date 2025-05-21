from typing import List, Optional
import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Laptop(BaseModel):
      id: int
      user_id: int
      brand: str
      cpu: str
      gpu: str
      min_price: int
      max_price: int
      
      class Config:
        from_attributes = True
      

class UserActivity(BaseModel):
      id: int
      user_id: int
      action: str
      timestamp: datetime
      detail: str
      
      class Config:
        from_attributes = True
      

class User(BaseModel):
       id: int
       username: str
       name: str
       hashed_password: bytes
       email: EmailStr
       active: bool
       laptop_templates: List[Laptop]
       user_activity: List[UserActivity]
       
       class Config:
        from_attributes = True
        

class TokenPayload(BaseModel):
    sub: int
    name: Optional[str]
    email: Optional[EmailStr]
    role: str
    exp: int
    iat: int
    jti: uuid.UUID