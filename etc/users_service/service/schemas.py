from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator

class UserNameUpdateSchema(BaseModel):
	new_name: str



class SensitiveDataUpdateSchema(BaseModel):
     current_password: str
     
class PasswordUpdateSchema(SensitiveDataUpdateSchema):
    new_password: str
    
class EmailUpdateSchema(SensitiveDataUpdateSchema):
    new_email: EmailStr