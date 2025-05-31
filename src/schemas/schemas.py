from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator

'''User schemas'''

class UserAddSchema(BaseModel):
	id: int
	role: str
	active: bool
	username: str
	email: EmailStr
	hashed_password: str

class UserUpdateSchema(BaseModel):
	username: Optional[str] = None
	email: Optional[EmailStr] = None
	password: Optional[str] = None

class UserUpdateSchema(BaseModel):
	id: int
	username: Optional[str] = None
	email: Optional[EmailStr] = None
	password: Optional[str] = None

class UserDeleteSchema(BaseModel):
	id: int



'''Laptop schemas'''

class LaptopAddSchema(BaseModel):
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

class LaptopUpdateSchema(BaseModel):
	brand: Optional[str] = None
	cpu: Optional[str] = None
	gpu: Optional[str] = None
	igpu: Optional[str] = None
	ram: Optional[int] = None
	storage: Optional[int] = None
	diagonal: Optional[float] = None
	min_price: Optional[int] = None
	max_price: Optional[int] = None

class LaptopUpdateInternalSchema(BaseModel):
	user_id: int
	brand: Optional[str] = None
	cpu: Optional[str] = None
	gpu: Optional[str] = None
	igpu: Optional[str] = None
	ram: Optional[int] = None
	storage: Optional[int] = None
	diagonal: Optional[float] = None
	min_price: Optional[int] = None
	max_price: Optional[int] = None

class LaptopDeleteSchema(BaseModel):
	user_id: int



'''Activity schemas'''

class ActivityAddInternalSchema(BaseModel):
	user_id: int
	detail: str
	timestamp: datetime



'''Auth schemas'''

class LoginSchema(BaseModel):
	username: str
	password: str

class UserRegisterSchema(BaseModel):
	username: str
	email: EmailStr
	password: str

class LaptopRegisterSchema(BaseModel):
	brand: str
	cpu: str
	gpu: str
	igpu: str
	ram: int
	storage: int
	diagonal: float
	min_price: int
	max_price: int