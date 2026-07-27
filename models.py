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


class UserRole(Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    PASSENGER = "passenger"


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TrainType(Enum):
    PASSENGER = "passenger"
    EXPRESS = "express"
    FREIGHT = "freight"
    HIGH_SPEED = "high_speed"


class TrainStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DELAYED = "delayed"


class ScheduleStatus(Enum):
    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentMethod(Enum):
    CARD = "card"
    MPESA = "mpesa"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.PASSENGER, nullable=False)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    payments = db.relationship("Payment", back_populates="user")
    favourites = db.relationship(
        "UserFavourite", back_populates="user", cascade="all, delete-orphan"
    )


class Train(db.Model):
    __tablename__ = "trains"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(TrainType), nullable=False)
    total_seat = db.Column(db.Integer, nullable=False)
    available_seat = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(TrainStatus), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    schedules = db.relationship("Schedule", back_populates="train")
    bookings = db.relationship("Booking", back_populates="train")
    favourites = db.relationship(
        "UserFavourite", back_populates="train", cascade="all, delete-orphan"
    )


class Station(db.Model):
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    train_number = db.Column(db.String(10), nullable=False, unique=True)
    city = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    departing_schedules = db.relationship(
        "Schedule", foreign_keys="Schedule.from_station_id", back_populates="from_station"
    )
    arriving_schedules = db.relationship(
        "Schedule", foreign_keys="Schedule.to_station_id", back_populates="to_station"
    )
    favourites = db.relationship(
        "UserFavourite", back_populates="station", cascade="all, delete-orphan"
    )


class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), nullable=False)
    from_station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    to_station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(ScheduleStatus), nullable=False)
    platform = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    train = db.relationship("Train", back_populates="schedules")
    from_station = db.relationship(
        "Station", foreign_keys=[from_station_id], back_populates="departing_schedules"
    )
    to_station = db.relationship(
        "Station", foreign_keys=[to_station_id], back_populates="arriving_schedules"
    )
    bookings = db.relationship("Booking", back_populates="schedule")


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


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.Enum(PaymentMethod), nullable=False)
    card_last4 = db.Column(db.String(4))
    status = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    booking = db.relationship("Booking", back_populates="payments")
    user = db.relationship("User", back_populates="payments")


class UserFavourite(db.Model):
    __tablename__ = "user_favourites"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="favourites")
    train = db.relationship("Train", back_populates="favourites")
    station = db.relationship("Station", back_populates="favourites")
