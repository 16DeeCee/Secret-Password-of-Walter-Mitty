from sqlalchemy.orm import DeclarativeBase, Mapped,  mapped_column, relationship
from sqlalchemy import create_engine, ForeignKey, String
from typing import List

engine = create_engine("", echo=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(12))
    master_password: Mapped[str] = mapped_column(String(100))

    passwords: Mapped[List["Passwords"]] = relationship(back_populates="user")

    def __init__(self, user, master_password):
        self.user = user
        self.master_password = master_password

    def __repr__(self):
        return f"ID: {self.id} - USER: {self.user} - MASTER_PASSWORD: {self.master_password}"

class Passwords(Base):
    __tablename__ = "user_passwords"

    pid: Mapped[int] = mapped_column(primary_key=True)
    site_url: Mapped[str] = mapped_column(String(100))
    image_path: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped["User"] = relationship(back_populates="passwords")

    def __init__(self, site_url, image_path, user_id):
        self.site_url = site_url
        self.image_path = image_path
        self.user_id = user_id

    def __repr__(self):
        return f"ID: {self.pid} - SITE: {self.site_url} - IMAGE PATH: {self.image_path} - USER: {self.user_id}"

