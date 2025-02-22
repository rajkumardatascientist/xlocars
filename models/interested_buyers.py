# models/interested_buyers.py
from extensions import db
from sqlalchemy import Column, Integer, ForeignKey

class InterestedBuyers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, ForeignKey('car.id'), nullable=False)

    def __repr__(self):
        return f"<InterestedBuyer User: {self.user_id}, Car: {self.car_id}>"