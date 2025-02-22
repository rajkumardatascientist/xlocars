from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from extensions import db  #  Import ONLY db
from flask import current_app
import enum
import sqlalchemy as sa
from sqlalchemy.types import TypeDecorator


class UserRole(enum.Enum):
    BUYER = 'buyer'
    SELLER = 'seller'
    AGENT = 'agent'


class UserRoleType(TypeDecorator):
    impl = sa.String
    cache_ok = True

    def __init__(self):
        super().__init__(length=20)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value if isinstance(value, enum.Enum) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return UserRole(value)
        except ValueError:
            return None

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    is_admin = Column(Boolean, default=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    role = Column(UserRoleType(), default=UserRole.BUYER)  # Use UserRoleType
    # Relationships
    cars = relationship('Car', backref='seller', lazy=True)
    interested_buyers = relationship('InterestedBuyers', backref='buyer', lazy=True)
    wishlist_items = relationship('Wishlist', backref='user', lazy=True)

    # Appointments where the user is the buyer:
    buying_appointments = relationship('Appointment', foreign_keys='[Appointment.buyer_id]',
                                       back_populates='buyer', lazy=True)

    # Appointments where the user is the seller:
    selling_appointments = relationship('Appointment', foreign_keys='[Appointment.seller_id]',
                                        back_populates='seller', lazy=True)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'