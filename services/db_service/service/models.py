from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    password: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True)
    laptop_templates: Mapped[list['LaptopTemplateModel']] = relationship('LaptopTemplateModel', back_populates='user')


class LaptopTemplateModel(Base):
    __tablename__ = 'laptop_templates'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    template_data: Mapped[str]

    user: Mapped[UserModel] = relationship('UserModel', back_populates='laptop_templates')