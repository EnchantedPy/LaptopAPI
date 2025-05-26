from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator

class UserAddSchema(BaseModel):
	name: str
	username: str
	email: EmailStr
	password: str
      

class UserUpdateInternalSchema(BaseModel):
      id: int
      name: Optional[str] = None
      username: Optional[str] = None
      email: Optional[EmailStr] = None
      password: Optional[str] = None
      repeat_password: Optional[str] = None
      submit_password: Optional[str] = None
      
class UserUpdateSchema(BaseModel):
      id: int
      name: Optional[str] = None
      username: Optional[str] = None
      email: Optional[EmailStr] = None
      password: Optional[str] = None

class UserUpdateRequestSchema(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    repeat_password: Optional[str] = None
    submit_password: Optional[str] = None

    @model_validator(mode='after')
    def validate_user_update(self):
        
        email = self.email
        password = self.password
        repeat_password = self.repeat_password
        submit_password = self.submit_password
        
        if email is not None:
            if submit_password is None:
                raise ValueError("Current password (submit_password) is required when changing email")

        if password is not None:
            if repeat_password is None:
                raise ValueError("Password confirmation (repeat_password) is required when changing password")
            
            if submit_password is None:
                raise ValueError("Current password (submit_password) is required when changing password")
            
            if password != repeat_password:
                raise ValueError("New password and password confirmation do not match")

        if repeat_password is not None and password is None:
            raise ValueError("repeat_password can only be provided when changing password")

        if submit_password is not None and email is None and password is None:
            raise ValueError("Current password provided but nothing to confirm - no email or password change requested")
        
        return self


class UserDeleteSchema(BaseModel):
	user_id: int


class LaptopAddSchema(BaseModel):
	user_id: int
	brand: str
	cpu: str
	gpu: str
	min_price: int
	max_price: int

class LaptopUpdateSchema(BaseModel):
	user_id: int
	laptop_id: int
	brand: Optional[str] = None
	cpu: Optional[str] = None
	gpu: Optional[str] = None
	min_price: Optional[int] = None
	max_price: Optional[int] = None

class LaptopDeleteSchema(BaseModel):
	user_id: int
	laptop_id: int


class UserActivityAddSchema(BaseModel):
	user_id: int
	action: str
	timestamp: datetime
	detail: Optional[str] = None


class UserActivityDeleteSchema(BaseModel):
	user_id: int
	activity_id: int


class UserLoginSchema(BaseModel):
	username: str
	password: str

class AdminLoginSchema(BaseModel):
	name: str
	password: str
	admin_secret: str