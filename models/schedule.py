from enum import Enum
from datetime import datetime

from . import db


class ScheduleStatus(Enum):
    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), nullable=False)
    from_station_id = db.Column(
        db.Integer, db.ForeignKey("stations.id"), nullable=False
    )
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
