from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import String, DateTime
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    name: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[bytes]
    email: Mapped[str] = mapped_column(String, unique=True)
    active: Mapped[bool]
    laptop_templates: Mapped[list['LaptopTemplateModel']] = relationship('LaptopTemplateModel', back_populates='user')
    user_activity: Mapped[list['UserActivityModel']] = relationship('UserActivityModel', back_populates='user')
    

class LaptopTemplateModel(Base):
    __tablename__ = 'laptops'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    brand: Mapped[str]
    cpu: Mapped[str]
    gpu: Mapped[str]
    min_price: Mapped[int]
    max_price: Mapped[int]

    user: Mapped[UserModel] = relationship('UserModel', back_populates='laptop_templates')


class UserActivityModel(Base):
    __tablename__ = 'user_activity'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    action: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    detail: Mapped[str]

    user: Mapped[UserModel] = relationship('UserModel', back_populates='user_activity')