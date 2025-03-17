from sqlalchemy.orm import DeclarativeBase, Mapped,  mapped_column, relationship, sessionmaker
from sqlalchemy import create_engine, ForeignKey, String, URL, UniqueConstraint, BLOB
from sqlalchemy.exc import IntegrityError
from typing import List
from dotenv import load_dotenv, find_dotenv
import os


_ = load_dotenv(find_dotenv())

url_object = URL.create(
    "sqlite",
    # "postgresql+psycopg",
    # username="johndoe",
    # password="123abc",
    # host="127.0.0.1",
    database="passwordmanager.db"
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(12))
    master_password: Mapped[bytes] = mapped_column(BLOB)
    passwords: Mapped[List["Passwords"]] = relationship(back_populates="user")

    UniqueConstraint(username)

    def __repr__(self):
        return f"ID: {self.id} - USER: {self.username} - MASTER_PASSWORD: {self.master_password}"
    

class Passwords(Base):
    __tablename__ = "user_passwords"

    pid: Mapped[int] = mapped_column(primary_key=True)
    site_url: Mapped[str] = mapped_column(String(100))
    image_path: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped["User"] = relationship(back_populates="passwords")

    def __repr__(self):
        return f"ID: {self.pid} - SITE: {self.site_url} - IMAGE PATH: {self.image_path} - USER: {self.user_id}"


class DBQuery:
    def __init__(self):
        # self.engine = create_engine("postgresql+psycopg://scott:tiger@localhost/test")
        self.engine = create_engine(url_object)
        
        self.Session = sessionmaker(self.engine, expire_on_commit=False)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_user_data(self, user_name: str):
        session = self.Session()
        query = session.query(User).filter(User.username == user_name)

        return session.scalars(query).one_or_none()
    

    def add_user(self, user_name: str, password: bytes):

        with self.Session() as session:
            try:
                user = User(
                    username=user_name,
                    master_password=password,
                )
                session.add(user)
                session.commit()
            except IntegrityError as e:
                raise ValueError("Username already exists.")

        if user.id:
            return user.username
        
        
    def add_passwords(self, site_url: str, image_path: str, user_id: int):
        with self.Session() as session:
            password = Passwords(
                site_url=site_url,
                image_path=image_path,
                user_id=user_id
            )
            session.add(password)
            session.commit()

        return password.pid
    
    def update_password(self, user_id, site_url, new_values):
        with self.Session() as session:
            result = session.query(Passwords).filter(
                Passwords.user_id == user_id,
                Passwords.site_url == site_url
            ).update(new_values)
            
            session.commit()

            return result > 0
        
    def delete_password(self, data):
        with self.Session() as session:
            result = session.query(Passwords).filter(
                Passwords.pid == data.pid,
                Passwords.user_id == data.user_id,
                Passwords.image_path == data.image_path,
                Passwords.site_url == data.site_url,
            ).delete()

            session.commit()

            return result > 0