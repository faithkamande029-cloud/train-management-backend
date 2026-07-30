from flask_sqlalchemy import SQLAlchemy

from .user import User, UserRole, UserStatus
from .train import Train, TrainType, TrainStatus
from .station import Station, StationStatus
from .schedule import Schedule, ScheduleStatus
from .booking import Booking, BookingStatus
from .payment import Payment, PaymentMethod
from .favourite import UserFavourite

db = SQLAlchemy()
