from typing import Annotated
from services.admin_service.service.schemas import UserPaginationSchema
from fastapi import Depends

PaginationDep = Annotated[UserPaginationSchema, Depends(UserPaginationSchema)]