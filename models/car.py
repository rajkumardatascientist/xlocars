# models/car.py
from extensions import db
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    body_type = db.Column(db.String(50))
    fuel_type = db.Column(db.String(50))
    transmission = db.Column(db.String(50))
    kilometers = db.Column(db.Integer)
    exterior_color = db.Column(db.String(50))
    interior_color = db.Column(db.String(50))
    vin = db.Column(db.String(17), nullable=True)
    license_plate = db.Column(db.String(20))
    registration_expiry = db.Column(db.DateTime)
    registration_number = db.Column(db.String(20), nullable=True)
    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    engine_type = db.Column(db.String(50))
    engine_capacity = db.Column(db.Float)
    no_of_owners = db.Column(db.Integer)
    seller_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    seller_phone = db.Column(db.String(20))
    is_approved = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    is_sold = db.Column(db.Boolean, default=False)  # Add is_sold field

    # Relationships
    interested_buyers = relationship('InterestedBuyers', backref='car', lazy=True, cascade="all, delete-orphan")
    wishlist_entries = relationship('Wishlist', backref='car', lazy=True, cascade="all, delete-orphan")
    appointments = relationship('Appointment', lazy=True, cascade="all, delete-orphan")
    images = relationship("Image", backref="car", cascade="all, delete-orphan")

    # FIXED: Use back_populates instead of backref to match User.cars
    seller = relationship('User', back_populates='cars')

    def __repr__(self):
        return f'<Car {self.make} {self.model}>'
