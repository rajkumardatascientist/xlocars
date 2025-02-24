# models/car.py
from extensions import db
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from flask import current_app
from datetime import datetime, timezone

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)

    # ADD THESE TWO LINES
    body_type = db.Column(db.String(50))  # Added body_type
    fuel_type = db.Column(db.String(50))  # Added fuel_type

    transmission = db.Column(db.String(50))
    kilometers = db.Column(db.Integer)  # Added kilometers
    exterior_color = db.Column(db.String(50))
    interior_color = db.Column(db.String(50))
    vin = db.Column(db.String(17), nullable=True)
    license_plate = db.Column(db.String(20))
    registration_expiry = db.Column(db.Date)
    registration_number = db.Column(db.String(20), nullable=True)
    state = db.Column(db.String(50))  #  New field
    city = db.Column(db.String(50)) # New field
    engine_type = db.Column(db.String(50))
    engine_capacity = db.Column(db.Float)  # e.g., 2.0 for 2.0L engine
    no_of_owners = db.Column(db.Integer) # Added no_of_owners
    seller_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)  # Add the is_featured column
    date_posted = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))

    # ADD THIS LINE
    is_active = db.Column(db.Boolean, default=True)  #  Add is_active

    # Relationships
    interested_buyers = relationship('InterestedBuyers', backref='car', lazy=True)
    wishlist_entries = relationship('Wishlist', backref='car', lazy=True)
    appointments = relationship('Appointment', lazy=True)
    images = relationship("Image", backref="car")  # Add the 'images' relationship

    def __repr__(self):
        return f'<Car {self.make} {self.model}>'
