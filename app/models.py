# app/models.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Integer)
    count = Column(Integer)
    description = Column(String, nullable=False, default="No descrtiption") 