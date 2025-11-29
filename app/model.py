from sqlalchemy import (create_engine, Column, Integer, String,
                     Text, Boolean, Numeric)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.database import SessionLocal

engine = create_engine("postgresql://postgres:1@localhost:5432/postgres",
                       echo=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db = Session()
Base = declarative_base()





class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    gmail = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    confirm_password = Column(String, nullable=False)
    generate_code = Column(String)
    is_active = Column(Boolean, default=False)


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    subject = Column(String)
    text = Column(Text)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, nullable=False)

    address = Column(String)

    price = Column(Numeric( 10, 2),
                   nullable=False, index=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(engine)
