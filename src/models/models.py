from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import String, DateTime
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    pass


class UserOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[bytes]
    email: Mapped[str] = mapped_column(String, unique=True)
    active: Mapped[bool]
	 role: Mapped[str]
    laptops: Mapped[list['LaptopOrm']] = relationship('LaptopOrm', back_populates='user')
    activities: Mapped[list['ActvityOrm']] = relationship('ActvityOrm', back_populates='user')
    

class LaptopOrm(Base):
    __tablename__ = 'laptops'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    brand: Mapped[str]
    cpu: Mapped[str]
    gpu: Mapped[str]
	 igpu: Mapped[str]
	 ram: Mapped[int]
	 storage: Mapped[int]
	 diagonal: Mapped[float]
    min_price: Mapped[int]
    max_price: Mapped[int]

    user: Mapped[UserOrm] = relationship('UserOrm', back_populates='laptops')


class ActivityOrm(Base):
    __tablename__ = 'activities'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    detail: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[UserOrm] = relationship('UserOrm', back_populates='activities')