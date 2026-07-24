"""JSON API routes for the train management service."""

from functools import wraps

from flask import Blueprint, jsonify, request
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

RESOURCES = {
    "users": (User, UserSchema),
    "trains": (Train, TrainSchema),
    "stations": (Station, StationSchema),
    "schedules": (Schedule, ScheduleSchema),
    "bookings": (Booking, BookingSchema),
    "payments": (Payment, PaymentSchema),
}


def error_response(status, message, details=None):
    payload = {"error": message, "status": status}
    if details:
        payload["details"] = details
    return jsonify(payload), status


@api.app_errorhandler(ValidationError)
def handle_validation_error(error):
    return error_response(400, "Validation failed.", error.messages)


@api.app_errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    return error_response(409, "The request conflicts with an existing record.")


@api.app_errorhandler(HTTPException)
def handle_http_error(error):
    return error_response(error.code, error.description)


@api.app_errorhandler(Exception)
def handle_unexpected_error(error):
    db.session.rollback()
    api.logger.exception("Unhandled API error", exc_info=error)
    return error_response(500, "An unexpected server error occurred.")


def json_body():
    if not request.is_json:
        return error_response(415, "Content-Type must be application/json.")
    payload = request.get_json(silent=True)
    if payload is None:
        return error_response(400, "Request body must contain valid JSON.")
    if not isinstance(payload, dict):
        return error_response(400, "Request body must be a JSON object.")
    return payload


def resource_handler(handler):
    @wraps(handler)
    def wrapped(resource, *args, **kwargs):
        if resource not in RESOURCES:
            return error_response(404, "Resource not found.")
        return handler(resource, *args, **kwargs)

    return wrapped


def load_instance(resource, record_id):
    model, _ = RESOURCES[resource]
    record = db.session.get(model, record_id)
    if record is None:
        return None, error_response(404, f"{model.__name__} {record_id} was not found.")
    return record, None


def validate_booking(data):
    schedule = db.session.get(Schedule, data.get("schedule_id"))
    if schedule is None:
        raise ValidationError({"schedule_id": ["Schedule does not exist."]})
    if schedule.train_id != data.get("train_id"):
        raise ValidationError({"train_id": ["Must match the selected schedule's train."]})


def prepare_data(resource, data):
    if resource == "users" and "password" in data:
        data["password"] = generate_password_hash(data["password"])
    if resource == "bookings" and {"train_id", "schedule_id"} <= data.keys():
        validate_booking(data)
    return data


@api.get("/<resource>")
@resource_handler
def list_records(resource):
    model, schema_class = RESOURCES[resource]
    records = db.session.scalars(db.select(model)).all()
    return jsonify({"data": schema_class(many=True).dump(records), "count": len(records)})


@api.post("/<resource>")
@resource_handler
def create_record(resource):
    payload = json_body()
    if not isinstance(payload, dict):
        return payload
    model, schema_class = RESOURCES[resource]
    data = prepare_data(resource, schema_class().load(payload))
    record = model(**data)
    db.session.add(record)
    db.session.commit()
    return jsonify({"data": schema_class().dump(record)}), 201


@api.get("/<resource>/<int:record_id>")
@resource_handler
def get_record(resource, record_id):
    record, error = load_instance(resource, record_id)
    if error:
        return error
    return jsonify({"data": RESOURCES[resource][1]().dump(record)})


@api.patch("/<resource>/<int:record_id>")
@resource_handler
def update_record(resource, record_id):
    record, error = load_instance(resource, record_id)
    if error:
        return error
    payload = json_body()
    if not isinstance(payload, dict):
        return payload
    _, schema_class = RESOURCES[resource]
    data = schema_class().load(payload, partial=True)
    if resource == "trains":
        total = data.get("total_seat", record.total_seat)
        available = data.get("available_seat", record.available_seat)
        if available > total:
            raise ValidationError({"available_seat": ["Must not exceed total_seat."]})
    if resource == "schedules":
        from_station = data.get("from_station_id", record.from_station_id)
        to_station = data.get("to_station_id", record.to_station_id)
        if from_station == to_station:
            raise ValidationError({"to_station_id": ["Must differ from from_station_id."]})
        departure_time = data.get("departure_time", record.departure_time)
        arrival_time = data.get("arrival_time", record.arrival_time)
        if arrival_time <= departure_time:
            raise ValidationError({"arrival_time": ["Must be after departure_time."]})
    if resource == "bookings":
        booking_data = {"train_id": data.get("train_id", record.train_id), "schedule_id": data.get("schedule_id", record.schedule_id)}
        validate_booking(booking_data)
    for field, value in prepare_data(resource, data).items():
        setattr(record, field, value)
    db.session.commit()
    return jsonify({"data": schema_class().dump(record)})


@api.delete("/<resource>/<int:record_id>")
@resource_handler
def delete_record(resource, record_id):
    record, error = load_instance(resource, record_id)
    if error:
        return error
    db.session.delete(record)
    db.session.commit()
    return "", 204


@api.get("/favourites")
def list_favourites():
    records = db.session.scalars(db.select(UserFavourite)).all()
    return jsonify({"data": UserFavouriteSchema(many=True).dump(records), "count": len(records)})


@api.post("/favourites")
def create_favourite():
    payload = json_body()
    if not isinstance(payload, dict):
        return payload
    data = UserFavouriteSchema().load(payload)
    record = UserFavourite(**data)
    db.session.add(record)
    db.session.commit()
    return jsonify({"data": UserFavouriteSchema().dump(record)}), 201


@api.delete("/favourites/<int:user_id>/<int:train_id>/<int:station_id>")
def delete_favourite(user_id, train_id, station_id):
    record = db.session.get(UserFavourite, (user_id, train_id, station_id))
    if record is None:
        return error_response(404, "Favourite was not found.")
    db.session.delete(record)
    db.session.commit()
    return "", 204
