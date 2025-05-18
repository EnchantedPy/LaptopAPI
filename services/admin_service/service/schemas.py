from pydantic import BaseModel, EmailStr, Field

class SearchUserByEmailSchema(BaseModel):
	search_query: EmailStr

class SearchUserByNameSchema(BaseModel):
	search_query: str

class SearchUserByIdSchema(BaseModel):
	search_query: int

class UserPaginationSchema(BaseModel):
	offset: int = Field(0, ge=0, description="Offset for pagination")
	limit: int = Field(5, gt=0, le=100, description="Number of items maximum to return")