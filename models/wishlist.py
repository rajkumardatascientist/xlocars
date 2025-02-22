from flask import current_app
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db



class Wishlist(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)

    def __repr__(self):
        return f"Wishlist(user_id={self.user_id}, car_id={self.car_id})"

    def get_db(self):
        with current_app.app_context():
            from app import db
            return db