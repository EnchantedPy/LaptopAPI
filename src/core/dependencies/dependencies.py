from fastapi import Depends
from typing import Annotated
from src.utils.UnitOfWork import SQLAlchemyUoWInterface, SQLAlchemyUoW

SqlUoWDep = Annotated[SQLAlchemyUoWInterface, Depends(SQLAlchemyUoW)]