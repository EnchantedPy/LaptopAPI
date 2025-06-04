from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator

'''User schemas'''

class UserAddSchema(BaseModel):
	role: str
	active: bool
	username: str
	email: EmailStr
	hashed_password: str

class UserUpdateSchema(BaseModel):
	id: int
	username: Optional[str] = None
	email: Optional[EmailStr] = None
	hashed_password: Optional[str] = None



'''Laptop schemas'''

class LaptopAddSchema(BaseModel):
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


'''Auth schemas'''

class LoginSchema(BaseModel):
	username: str
	password: str

class UserCreateSchema(BaseModel):
	username: str
	email: EmailStr
	password: str

class UserChangeSchema(BaseModel):
	username: Optional[str] = None
	email: Optional[EmailStr] = None
	password: Optional[str] = None

class LaptopCreateSchema(BaseModel):
	brand: str
	cpu: str
	gpu: str
	igpu: str
	ram: int
	storage: int
	diagonal: float
	min_price: int
	max_price: int

class LaptopChangeSchema(BaseModel):
	brand: Optional[str] = None
	cpu: Optional[str] = None
	gpu: Optional[str] = None
	igpu: Optional[str] = None
	ram: Optional[int] = None
	storage: Optional[int] = None
	diagonal: Optional[float] = None
	min_price: Optional[int] = None
	max_price: Optional[int] = None


'''...............'''

class RegisterRequestSchema(BaseModel):
	username: str
	email: EmailStr
	password: str

class UserUpdateSchema(BaseModel):
	id: int
	username: Optional[str] = None
	email: Optional[EmailStr] = None
	password: Optional[str] = None

class UserResponseDto(BaseModel):
	id: int
	username: str
	email: EmailStr
	active: bool