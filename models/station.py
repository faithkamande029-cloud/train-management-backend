from enum import Enum
from datetime import datetime

from . import db


class StationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


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
        "Schedule",
        foreign_keys="Schedule.from_station_id",
        back_populates="from_station",
    )
    arriving_schedules = db.relationship(
        "Schedule", foreign_keys="Schedule.to_station_id", back_populates="to_station"
    )
    favourites = db.relationship(
        "UserFavourite", back_populates="station", cascade="all, delete-orphan"
    )
