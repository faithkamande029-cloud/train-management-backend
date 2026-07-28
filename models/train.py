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
