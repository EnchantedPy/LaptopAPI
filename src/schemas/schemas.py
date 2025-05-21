from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserAddSchema(BaseModel):
	name: str
	email: EmailStr
	password: str

class UserUpdateSchema(BaseModel):
	user_id: int
	name: Optional[str] = None
	email: Optional[EmailStr] = None
	password: Optional[str] = None

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
	name: str
	password: str

class AdminLoginSchema(BaseModel):
	name: str
	password: str
	admin_secret: str