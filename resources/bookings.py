"""Flask-RESTful resources for the train management service."""

from flask import Blueprint, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from models import Booking, db
from services.booking_service import validate_booking
from schemas.booking_schema import BookingSchema


class BookingListResource(Resource):
    def get(self):
        bookings = db.session.scalars(db.select(Booking)).all()
        return {"data": BookingSchema(many=True).dump(bookings), "count": len(bookings)}

    def post(self):
        data = BookingSchema().load(request.get_json())
        validate_booking(data["train_id"], data["schedule_id"])
        booking = Booking(**data)
        db.session.add(booking)
        db.session.commit()
        return {"data": BookingSchema().dump(booking)}, 201


class BookingResource(Resource):
    def get(self, booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking is None:
            return {"error": f"Booking {booking_id} was not found.", "status": 404}, 404
        return {"data": BookingSchema().dump(booking)}

    def patch(self, booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking is None:
            return {"error": f"Booking {booking_id} was not found.", "status": 404}, 404
        data = BookingSchema().load(request.get_json(), partial=True)
        validate_booking(
            data.get("train_id", booking.train_id),
            data.get("schedule_id", booking.schedule_id),
        )
        for field, value in data.items():
            setattr(booking, field, value)
        db.session.commit()
        return {"data": BookingSchema().dump(booking)}

    def delete(self, booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking is None:
            return {"error": f"Booking {booking_id} was not found.", "status": 404}, 404
        db.session.delete(booking)
        db.session.commit()
        return "", 204