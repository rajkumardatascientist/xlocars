# models/appointment.py
from extensions import db
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Add the status column here:
    status = db.Column(db.String(50),
                       default='pending')  # Or another appropriate default

    # Relationships
    # Explicitly defined relationships from appointment to user through user_id keys
    # Buyer is the buyer, and seller is the seller
    buyer = relationship("User", foreign_keys=[buyer_id],
                           back_populates="buying_appointments")
    seller = relationship("User", foreign_keys=[seller_id],
                             back_populates="selling_appointments")
    car = relationship("Car", foreign_keys=[car_id],
                          back_populates="appointments")

    def __repr__(self):
        return (f"Appointment(Buyer: {self.buyer_id}, Seller: {self.seller_id},"
                f" Car: {self.car_id}, Time: {self.appointment_time})")
