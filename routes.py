"""Flask-RESTful resources for the train management service."""

from flask import Blueprint, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

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
    train = db.session.get(Train, train_id)
    if train is None:
        raise ValidationError({"train_id": ["Train does not exist."]})
    schedule = db.session.get(Schedule, schedule_id)
    if schedule is None:
        raise ValidationError({"schedule_id": ["Schedule does not exist."]})
    if schedule.train_id != train_id:
        raise ValidationError({"train_id": ["Must match the selected schedule's train."]})


# ─── User Resources ────────────────────────────────────────────
class UserListResource(Resource):
    def get(self):
        users = db.session.scalars(db.select(User)).all()
        return {"data": UserSchema(many=True).dump(users), "count": len(users)}

    def post(self):
        schema = UserSchema(session=db.session)
        user = schema.load(request.get_json())
        user.password = generate_password_hash(user.password)
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
        schema = UserSchema(session=db.session)
        schema.load(request.get_json(), instance=user, partial=True)
        db.session.commit()
        return {"data": UserSchema().dump(user)}

    def put(self, user_id):
        return self.patch(user_id)

    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": f"User {user_id} was not found.", "status": 404}, 404
        db.session.delete(user)
        db.session.commit()
        return "", 204


# ─── Login ──────────────────────────────────────────────────
class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return {"error": "Email and password are required."}, 400

        user = User.query.filter_by(email=email).first()
        if user is None:
            return {"error": "Invalid credentials."}, 401

        # In production, verify password with check_password_hash(user.password, password)
        return {
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": user.role.value
            },
            "accessToken": "fake-jwt-token",
            "refreshToken": "fake-refresh-token"
        }, 200


class MeResource(Resource):
    def get(self):
        return {
            "id": 1,
            "name": "Admin User",
            "email": "admin@railms.com",
            "role": "admin"
        }


# ─── Trains ──────────────────────────────────────────────────
class TrainListResource(Resource):
    def get(self):
        trains = db.session.scalars(db.select(Train)).all()
        return {"data": TrainSchema(many=True).dump(trains), "count": len(trains)}

    def post(self):
        schema = TrainSchema(session=db.session)
        train = schema.load(request.get_json())
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
        schema = TrainSchema(session=db.session)
        schema.load(request.get_json(), instance=train, partial=True)
        db.session.commit()
        return {"data": TrainSchema().dump(train)}

    def put(self, train_id):
        return self.patch(train_id)

    def delete(self, train_id):
        train = db.session.get(Train, train_id)
        if train is None:
            return {"error": f"Train {train_id} was not found.", "status": 404}, 404
        db.session.delete(train)
        db.session.commit()
        return "", 204


# ─── Stations ────────────────────────────────────────────────
class StationListResource(Resource):
    def get(self):
        stations = db.session.scalars(db.select(Station)).all()
        return {"data": StationSchema(many=True).dump(stations), "count": len(stations)}

    def post(self):
        schema = StationSchema(session=db.session)
        station = schema.load(request.get_json())
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
        schema = StationSchema(session=db.session)
        schema.load(request.get_json(), instance=station, partial=True)
        db.session.commit()
        return {"data": StationSchema().dump(station)}

    def put(self, station_id):
        return self.patch(station_id)

    def delete(self, station_id):
        station = db.session.get(Station, station_id)
        if station is None:
            return {"error": f"Station {station_id} was not found.", "status": 404}, 404
        db.session.delete(station)
        db.session.commit()
        return "", 204


# ─── Schedules ──────────────────────────────────────────────
class ScheduleListResource(Resource):
    def get(self):
        schedules = db.session.scalars(db.select(Schedule)).all()
        return {"data": ScheduleSchema(many=True).dump(schedules), "count": len(schedules)}

    def post(self):
        schema = ScheduleSchema(session=db.session)
        schedule = schema.load(request.get_json())
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
        schema = ScheduleSchema(session=db.session)
        updated = schema.load(request.get_json(), instance=schedule, partial=True)
        # Additional validations
        if updated.from_station_id == updated.to_station_id:
            raise ValidationError({"to_station_id": ["Must differ from from_station_id."]})
        if updated.arrival_time <= updated.departure_time:
            raise ValidationError({"arrival_time": ["Must be after departure_time."]})
        db.session.commit()
        return {"data": ScheduleSchema().dump(updated)}

    def put(self, schedule_id):
        return self.patch(schedule_id)

    def delete(self, schedule_id):
        schedule = db.session.get(Schedule, schedule_id)
        if schedule is None:
            return {"error": f"Schedule {schedule_id} was not found.", "status": 404}, 404
        db.session.delete(schedule)
        db.session.commit()
        return "", 204


# ─── Bookings (FIXED with PUT) ─────────────────────────────────
class BookingListResource(Resource):
    def get(self):
        bookings = db.session.scalars(db.select(Booking)).all()
        data = BookingSchema(many=True).dump(bookings)
        for item in data:
            if 'fare' in item:
                item['fare'] = float(item['fare'])
        return {"data": data, "count": len(bookings)}

    def post(self):
        data = request.get_json()

        train_id = data.get("trainId")
        if train_id is None:
            return {"error": "trainId is required."}, 400
        try:
            train_id = int(train_id)
        except (ValueError, TypeError):
            return {"error": "trainId must be an integer."}, 400

        schedule_id = data.get("scheduleId")
        if schedule_id is None:
            return {"error": "scheduleId is required."}, 400
        try:
            schedule_id = int(schedule_id)
        except (ValueError, TypeError):
            return {"error": "scheduleId must be an integer."}, 400

        schedule = db.session.get(Schedule, schedule_id)
        if not schedule:
            return {"error": "Schedule not found."}, 400

        seat_numbers = data.get("seatNumbers", [])
        seat_number = seat_numbers[0] if seat_numbers else ""

        booking_ref = f"BK-{int(datetime.now().timestamp())}-{random.randint(100, 999)}"

        payload = {
            "booking_ref": booking_ref,
            "passenger_name": data.get("passengerName", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "train_id": train_id,
            "schedule_id": schedule_id,
            "seat_number": seat_number,
            "fare": data.get("fare", 0),
            "status": "confirmed",
            "from_station": schedule.from_station.name if schedule.from_station else "",
            "to_station": schedule.to_station.name if schedule.to_station else "",
            "departure_time": schedule.departure_time.strftime("%H:%M") if schedule.departure_time else "",
        }

        schema = BookingSchema(session=db.session)
        try:
            booking = schema.load(payload)
        except ValidationError as err:
            print("Validation errors:", err.messages)
            return {"error": "Validation failed.", "details": err.messages}, 400

        validate_booking(booking.train_id, booking.schedule_id)

        try:
            db.session.add(booking)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {"error": "Could not create booking. The email might be duplicated or the booking reference already exists.", "details": str(e)}, 409

        booking_data = BookingSchema().dump(booking)
        if 'fare' in booking_data:
            booking_data['fare'] = float(booking_data['fare'])
        return {"data": booking_data}, 201


class BookingResource(Resource):
    def get(self, booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking is None:
            return {"error": f"Booking {booking_id} was not found.", "status": 404}, 404
        booking_data = BookingSchema().dump(booking)
        if 'fare' in booking_data:
            booking_data['fare'] = float(booking_data['fare'])
        return {"data": booking_data}

    def patch(self, booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking is None:
            return {"error": f"Booking {booking_id} was not found.", "status": 404}, 404

        data = request.get_json()
        payload = {}
        if "passengerName" in data:
            payload["passenger_name"] = data["passengerName"]
        if "email" in data:
            payload["email"] = data["email"]
        if "phone" in data:
            payload["phone"] = data["phone"]
        if "trainId" in data:
            try:
                payload["train_id"] = int(data["trainId"])
            except (ValueError, TypeError):
                return {"error": "trainId must be an integer."}, 400
        if "scheduleId" in data:
            try:
                payload["schedule_id"] = int(data["scheduleId"])
            except (ValueError, TypeError):
                return {"error": "scheduleId must be an integer."}, 400
        if "seatNumbers" in data:
            seats = data["seatNumbers"]
            payload["seat_number"] = seats[0] if seats else ""
        if "fare" in data:
            payload["fare"] = data["fare"]
        if "status" in data:
            payload["status"] = data["status"]
        if "booking_ref" in data:
            payload["booking_ref"] = data["booking_ref"]
        if "fromStation" in data:
            payload["from_station"] = data["fromStation"]
        if "toStation" in data:
            payload["to_station"] = data["toStation"]
        if "departureTime" in data:
            payload["departure_time"] = data["departureTime"]

        schema = BookingSchema(session=db.session)
        try:
            updated = schema.load(payload, instance=booking, partial=True)
        except ValidationError as err:
            print("Validation errors:", err.messages)
            return {"error": "Validation failed.", "details": err.messages}, 400

        validate_booking(updated.train_id, updated.schedule_id)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {"error": "Update failed due to a conflict.", "details": str(e)}, 409

        booking_data = BookingSchema().dump(updated)
        if 'fare' in booking_data:
            booking_data['fare'] = float(booking_data['fare'])
        return {"data": booking_data}

    def put(self, booking_id):
        """Handle PUT requests by delegating to PATCH."""
        return self.patch(booking_id)

    def delete(self, booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking is None:
            return {"error": f"Booking {booking_id} was not found.", "status": 404}, 404
        db.session.delete(booking)
        db.session.commit()
        return "", 204


# ─── Payments ──────────────────────────────────────────────
class PaymentListResource(Resource):
    def get(self):
        payments = db.session.scalars(db.select(Payment)).all()
        data = PaymentSchema(many=True).dump(payments)
        for item in data:
            if 'amount' in item:
                item['amount'] = float(item['amount'])
        return {"data": data, "count": len(payments)}

    def post(self):
        schema = PaymentSchema(session=db.session)
        payment = schema.load(request.get_json())
        db.session.add(payment)
        db.session.commit()
        payment_data = PaymentSchema().dump(payment)
        if 'amount' in payment_data:
            payment_data['amount'] = float(payment_data['amount'])
        return {"data": payment_data}, 201


class PaymentResource(Resource):
    def get(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        payment_data = PaymentSchema().dump(payment)
        if 'amount' in payment_data:
            payment_data['amount'] = float(payment_data['amount'])
        return {"data": payment_data}

    def patch(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        schema = PaymentSchema(session=db.session)
        schema.load(request.get_json(), instance=payment, partial=True)
        db.session.commit()
        payment_data = PaymentSchema().dump(payment)
        if 'amount' in payment_data:
            payment_data['amount'] = float(payment_data['amount'])
        return {"data": payment_data}

    def put(self, payment_id):
        return self.patch(payment_id)

    def delete(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        db.session.delete(payment)
        db.session.commit()
        return "", 204


# ─── Favourites ─────────────────────────────────────────────
class FavouriteListResource(Resource):
    def get(self):
        favourites = db.session.scalars(db.select(UserFavourite)).all()
        return {"data": UserFavouriteSchema(many=True).dump(favourites), "count": len(favourites)}

    def post(self):
        schema = UserFavouriteSchema(session=db.session)
        favourite = schema.load(request.get_json())
        db.session.add(favourite)
        db.session.commit()
        return {"data": UserFavouriteSchema().dump(favourite)}, 201


class FavouriteResource(Resource):
    def delete(self, favourite_id):
        favourite = db.session.get(UserFavourite, favourite_id)
        if favourite is None:
            return {"error": "Favourite was not found.", "status": 404}, 404
        db.session.delete(favourite)
        db.session.commit()
        return "", 204


# ─── Register ──────────────────────────────────────────────
rest_api.add_resource(UserListResource, "/users")
rest_api.add_resource(UserResource, "/users/<int:user_id>")
rest_api.add_resource(LoginResource, "/login")
rest_api.add_resource(MeResource, "/me")
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
rest_api.add_resource(FavouriteResource, "/favourites/<int:favourite_id>")