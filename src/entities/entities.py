from typing import List
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
       name: str
       hashed_password: bytes
       email: EmailStr
       active: bool
       laptop_templates: List[Laptop]
       user_activity: List[UserActivity]
       
       class Config:
        from_attributes = True