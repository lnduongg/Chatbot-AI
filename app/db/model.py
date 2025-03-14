from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()

class Product(Base):
    __tablename__ = os.getenv("TB_NAME", "products")

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    colors = Column(JSON, nullable=False)
    price = Column(Float, nullable=False)