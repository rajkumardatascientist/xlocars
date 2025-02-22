#image.py
from extensions import db
from sqlalchemy import Column, Integer, String, ForeignKey

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)

    def __repr__(self):
        return f'<Image {self.url}>'