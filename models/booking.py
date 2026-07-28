from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from enum import Enum
from datetime import datetime

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_ref = db.Column(db.Text, nullable=False, unique=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey("schedules.id"), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    fare = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(BookingStatus), nullable=False)
    from_station = db.Column(db.String(100), nullable=False)
    to_station = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    train = db.relationship("Train", back_populates="bookings")
    schedule = db.relationship("Schedule", back_populates="bookings")
    payments = db.relationship("Payment", back_populates="booking")
