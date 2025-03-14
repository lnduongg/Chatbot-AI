from sqlalchemy.orm import Session
from app.db.model import Product

def get_recommendations(db: Session, category: str):
    return db.query(Product).filter(Product.category == category).limit(5).all()
