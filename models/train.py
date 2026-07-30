from enum import Enum
from datetime import datetime

from . import db


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
