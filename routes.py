"""Flask-RESTful resources for the train management service."""

from flask import Blueprint, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from models import Booking, Payment, Schedule, Station, Train, User, UserFavourite, db
from schemas import (
    BookingSchema,
    PaymentSchema,
    ScheduleSchema,
    StationSchema,
    TrainSchema,
    UserFavouriteSchema,
    UserSchema,
)

api = Blueprint("api", __name__, url_prefix="/api")


class TrainManagementApi(Api):
    """Return JSON errors for all API resources."""

    def handle_error(self, error):
        if isinstance(error, ValidationError):
            return {
                "error": "Validation failed.",
                "status": 400,
                "details": error.messages,
            }, 400
        if isinstance(error, IntegrityError):
            db.session.rollback()
            return {"error": "The request conflicts with an existing record.", "status": 409}, 409
        if isinstance(error, HTTPException):
            return {"error": error.description, "status": error.code}, error.code

        db.session.rollback()
        api.logger.exception("Unhandled API error", exc_info=error)
        return {"error": "An unexpected server error occurred.", "status": 500}, 500


rest_api = TrainManagementApi(api)


def validate_booking(train_id, schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if schedule is None:
        raise ValidationError({"schedule_id": ["Schedule does not exist."]})
    if schedule.train_id != train_id:
        raise ValidationError({"train_id": ["Must match the selected schedule's train."]})


class UserListResource(Resource):
    def get(self):
        users = db.session.scalars(db.select(User)).all()
        return {"data": UserSchema(many=True).dump(users), "count": len(users)}

    def post(self):
        data = UserSchema().load(request.get_json())
        data["password"] = generate_password_hash(data["password"])
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return {"data": UserSchema().dump(user)}, 201


class UserResource(Resource):
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": f"User {user_id} was not found.", "status": 404}, 404
        return {"data": UserSchema().dump(user)}

    def patch(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": f"User {user_id} was not found.", "status": 404}, 404
        data = UserSchema().load(request.get_json(), partial=True)
        if "password" in data:
            data["password"] = generate_password_hash(data["password"])
        for field, value in data.items():
            setattr(user, field, value)
        db.session.commit()
        return {"data": UserSchema().dump(user)}

    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": f"User {user_id} was not found.", "status": 404}, 404
        db.session.delete(user)
        db.session.commit()
        return "", 204


class TrainListResource(Resource):
    def get(self):
        trains = db.session.scalars(db.select(Train)).all()
        return {"data": TrainSchema(many=True).dump(trains), "count": len(trains)}

    def post(self):
        train = Train(**TrainSchema().load(request.get_json()))
        db.session.add(train)
        db.session.commit()
        return {"data": TrainSchema().dump(train)}, 201


class TrainResource(Resource):
    def get(self, train_id):
        train = db.session.get(Train, train_id)
        if train is None:
            return {"error": f"Train {train_id} was not found.", "status": 404}, 404
        return {"data": TrainSchema().dump(train)}

    def patch(self, train_id):
        train = db.session.get(Train, train_id)
        if train is None:
            return {"error": f"Train {train_id} was not found.", "status": 404}, 404
        data = TrainSchema().load(request.get_json(), partial=True)
        total_seat = data.get("total_seat", train.total_seat)
        available_seat = data.get("available_seat", train.available_seat)
        if available_seat > total_seat:
            raise ValidationError({"available_seat": ["Must not exceed total_seat."]})
        for field, value in data.items():
            setattr(train, field, value)
        db.session.commit()
        return {"data": TrainSchema().dump(train)}

    def delete(self, train_id):
        train = db.session.get(Train, train_id)
        if train is None:
            return {"error": f"Train {train_id} was not found.", "status": 404}, 404
        db.session.delete(train)
        db.session.commit()
        return "", 204


class StationListResource(Resource):
    def get(self):
        stations = db.session.scalars(db.select(Station)).all()
        return {"data": StationSchema(many=True).dump(stations), "count": len(stations)}

    def post(self):
        station = Station(**StationSchema().load(request.get_json()))
        db.session.add(station)
        db.session.commit()
        return {"data": StationSchema().dump(station)}, 201


class StationResource(Resource):
    def get(self, station_id):
        station = db.session.get(Station, station_id)
        if station is None:
            return {"error": f"Station {station_id} was not found.", "status": 404}, 404
        return {"data": StationSchema().dump(station)}

    def patch(self, station_id):
        station = db.session.get(Station, station_id)
        if station is None:
            return {"error": f"Station {station_id} was not found.", "status": 404}, 404
        data = StationSchema().load(request.get_json(), partial=True)
        for field, value in data.items():
            setattr(station, field, value)
        db.session.commit()
        return {"data": StationSchema().dump(station)}

    def delete(self, station_id):
        station = db.session.get(Station, station_id)
        if station is None:
            return {"error": f"Station {station_id} was not found.", "status": 404}, 404
        db.session.delete(station)
        db.session.commit()
        return "", 204


class ScheduleListResource(Resource):
    def get(self):
        schedules = db.session.scalars(db.select(Schedule)).all()
        return {"data": ScheduleSchema(many=True).dump(schedules), "count": len(schedules)}

    def post(self):
        schedule = Schedule(**ScheduleSchema().load(request.get_json()))
        db.session.add(schedule)
        db.session.commit()
        return {"data": ScheduleSchema().dump(schedule)}, 201


class ScheduleResource(Resource):
    def get(self, schedule_id):
        schedule = db.session.get(Schedule, schedule_id)
        if schedule is None:
            return {"error": f"Schedule {schedule_id} was not found.", "status": 404}, 404
        return {"data": ScheduleSchema().dump(schedule)}

    def patch(self, schedule_id):
        schedule = db.session.get(Schedule, schedule_id)
        if schedule is None:
            return {"error": f"Schedule {schedule_id} was not found.", "status": 404}, 404
        data = ScheduleSchema().load(request.get_json(), partial=True)
        from_station_id = data.get("from_station_id", schedule.from_station_id)
        to_station_id = data.get("to_station_id", schedule.to_station_id)
        if from_station_id == to_station_id:
            raise ValidationError({"to_station_id": ["Must differ from from_station_id."]})
        departure_time = data.get("departure_time", schedule.departure_time)
        arrival_time = data.get("arrival_time", schedule.arrival_time)
        if arrival_time <= departure_time:
            raise ValidationError({"arrival_time": ["Must be after departure_time."]})
        for field, value in data.items():
            setattr(schedule, field, value)
        db.session.commit()
        return {"data": ScheduleSchema().dump(schedule)}

    def delete(self, schedule_id):
        schedule = db.session.get(Schedule, schedule_id)
        if schedule is None:
            return {"error": f"Schedule {schedule_id} was not found.", "status": 404}, 404
        db.session.delete(schedule)
        db.session.commit()
        return "", 204


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


class PaymentListResource(Resource):
    def get(self):
        payments = db.session.scalars(db.select(Payment)).all()
        return {"data": PaymentSchema(many=True).dump(payments), "count": len(payments)}

    def post(self):
        payment = Payment(**PaymentSchema().load(request.get_json()))
        db.session.add(payment)
        db.session.commit()
        return {"data": PaymentSchema().dump(payment)}, 201


class PaymentResource(Resource):
    def get(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        return {"data": PaymentSchema().dump(payment)}

    def patch(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        data = PaymentSchema().load(request.get_json(), partial=True)
        for field, value in data.items():
            setattr(payment, field, value)
        db.session.commit()
        return {"data": PaymentSchema().dump(payment)}

    def delete(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        db.session.delete(payment)
        db.session.commit()
        return "", 204


class FavouriteListResource(Resource):
    def get(self):
        favourites = db.session.scalars(db.select(UserFavourite)).all()
        return {"data": UserFavouriteSchema(many=True).dump(favourites), "count": len(favourites)}

    def post(self):
        favourite = UserFavourite(**UserFavouriteSchema().load(request.get_json()))
        db.session.add(favourite)
        db.session.commit()
        return {"data": UserFavouriteSchema().dump(favourite)}, 201


class FavouriteResource(Resource):
    def delete(self, user_id, train_id, station_id):
        favourite = db.session.get(UserFavourite, (user_id, train_id, station_id))
        if favourite is None:
            return {"error": "Favourite was not found.", "status": 404}, 404
        db.session.delete(favourite)
        db.session.commit()
        return "", 204


rest_api.add_resource(UserListResource, "/users")
rest_api.add_resource(UserResource, "/users/<int:user_id>")
rest_api.add_resource(TrainListResource, "/trains")
rest_api.add_resource(TrainResource, "/trains/<int:train_id>")
rest_api.add_resource(StationListResource, "/stations")
rest_api.add_resource(StationResource, "/stations/<int:station_id>")
rest_api.add_resource(ScheduleListResource, "/schedules")
rest_api.add_resource(ScheduleResource, "/schedules/<int:schedule_id>")
rest_api.add_resource(BookingListResource, "/bookings")
rest_api.add_resource(BookingResource, "/bookings/<int:booking_id>")
rest_api.add_resource(PaymentListResource, "/payments")
rest_api.add_resource(PaymentResource, "/payments/<int:payment_id>")
rest_api.add_resource(FavouriteListResource, "/favourites")
rest_api.add_resource(
    FavouriteResource, "/favourites/<int:user_id>/<int:train_id>/<int:station_id>"
)
