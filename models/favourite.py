from datetime import datetime

from . import db


class UserFavourite(db.Model):
    __tablename__ = "user_favourites"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="favourites")
    train = db.relationship("Train", back_populates="favourites")
    station = db.relationship("Station", back_populates="favourites")
