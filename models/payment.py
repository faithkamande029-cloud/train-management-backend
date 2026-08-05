from enum import Enum
from datetime import datetime

from . import db


class PaymentMethod(Enum):
    CARD = "card"
    MPESA = "mpesa"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


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
