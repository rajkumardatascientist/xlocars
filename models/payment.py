# models/payment.py
from flask import current_app
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, String, Enum
from extensions import db
import enum  # Import enum


class PaymentStatus(enum.Enum):
    PENDING_PAYMENT = 'pending_payment'
    PAYMENT_FAILED = 'payment_failed'
    PAYMENT_SUCCESSFUL = 'payment_successful'
    PAYMENT_REFUNDED = 'payment_refunded'


class FeaturedPayments(db.Model):  # Inherit from db model
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    # Replace boolean to payment status enum
    payment_status = Column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING_PAYMENT
    )  # Replace Boolean with Enum
    is_featured = Column(Boolean, default=False)  # True if car is featured after approval
    # ADD THE FOLLOWING LINE
    transaction_id = Column(String(255))  # Changed to String

    def __repr__(self):
        return (
            f'<FeaturedPayments {self.id} - Car {self.car_id} - Seller {self.seller_id}>'
        )

    def get_db(self):
        with current_app.app_context():
            from app import db

            return db


class BuyerPayments(db.Model):  # Inherit from db model
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    seller_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    # Replace boolean to payment status enum
    payment_status = Column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING_PAYMENT
    )  # Replace Boolean with Enum
    is_contact_unlocked = Column(Boolean, default=False)
    # ADD THE FOLLOWING LINE
    transaction_id = Column(String(255))  # Changed to String

    def __repr__(self):
        return f'<BuyerPayments {self.id} - Car {self.car_id} - Buyer {self.buyer_id}>'

    def get_db(self):
        with current_app.app_context():
            from app import db

            return db