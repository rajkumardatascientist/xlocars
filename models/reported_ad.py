from flask import current_app
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from extensions import db


class ReportedAds(db.Model):
    id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)
    reported_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    reason = Column(Text, nullable=False)
    report_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    def car(self):
        from app import db  # Load it here instead of importing from top
        return relationship('Car', backref='reports')

    def reporter(self):
        from app import db  # Load it here instead of importing from top
        return relationship('User', backref='reported_ads')

    def __repr__(self):
        return f"<Reported Ad: Car {self.car_id} by User {self.reported_by}>"

    def get_db(self):
        with current_app.app_context():
            from app import db
            return db