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


class UserFavourite(db.Model):
    __tablename__ = "user_favourites"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="favourites")
    train = db.relationship("Train", back_populates="favourites")
    station = db.relationship("Station", back_populates="favourites")
