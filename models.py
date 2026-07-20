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


class User(db.Model):
    __table_name__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.PASSENGER, nullable=False)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
