from pydantic import BaseModel, EmailStr

class User(BaseModel):
	id: int
	name: str
	hashed_password: bytes
	email: EmailStr
	active: bool