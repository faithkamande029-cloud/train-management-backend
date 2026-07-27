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

RESOURCES = {
    "users": (User, UserSchema),
    "trains": (Train, TrainSchema),
    "stations": (Station, StationSchema),
    "schedules": (Schedule, ScheduleSchema),
    "bookings": (Booking, BookingSchema),
    "payments": (Payment, PaymentSchema),
}


class TrainManagementApi(Api):
    """Keep API errors consistent for every Flask-RESTful resource."""

    def handle_error(self, error):
        if isinstance(error, ApiRequestError):
            return {"error": error.message, "status": error.status}, error.status
        if isinstance(error, ValidationError):
            return {"error": "Validation failed.", "status": 400, "details": error.messages}, 400
        if isinstance(error, IntegrityError):
            db.session.rollback()
            return {"error": "The request conflicts with an existing record.", "status": 409}, 409
        if isinstance(error, HTTPException):
            return {"error": error.description, "status": error.code}, error.code

        db.session.rollback()
        api.logger.exception("Unhandled API error", exc_info=error)
        return {"error": "An unexpected server error occurred.", "status": 500}, 500


rest_api = TrainManagementApi(api)


class ApiRequestError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


def json_body():
    if not request.is_json:
        raise ApiRequestError(415, "Content-Type must be application/json.")
    payload = request.get_json(silent=True)
    if payload is None:
        raise ApiRequestError(400, "Request body must contain valid JSON.")
    if not isinstance(payload, dict):
        raise ApiRequestError(400, "Request body must be a JSON object.")
    return payload


def get_resource(resource):
    try:
        return RESOURCES[resource]
    except KeyError:
        return None, None


def get_record(resource, record_id):
    model, _ = get_resource(resource)
    if model is None:
        return None
    return db.session.get(model, record_id)


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


class CollectionResource(Resource):
    def get(self, resource):
        model, schema_class = get_resource(resource)
        if model is None:
            return {"error": "Resource not found.", "status": 404}, 404
        records = db.session.scalars(db.select(model)).all()
        return {"data": schema_class(many=True).dump(records), "count": len(records)}

    def post(self, resource):
        model, schema_class = get_resource(resource)
        if model is None:
            return {"error": "Resource not found.", "status": 404}, 404
        data = prepare_data(resource, schema_class().load(json_body()))
        record = model(**data)
        db.session.add(record)
        db.session.commit()
        return {"data": schema_class().dump(record)}, 201


class ItemResource(Resource):
    def get(self, resource, record_id):
        record = get_record(resource, record_id)
        if record is None:
            return self.not_found(resource, record_id)
        return {"data": get_resource(resource)[1]().dump(record)}

    def patch(self, resource, record_id):
        record = get_record(resource, record_id)
        if record is None:
            return self.not_found(resource, record_id)
        _, schema_class = get_resource(resource)
        data = schema_class().load(json_body(), partial=True)
        self.validate_update(resource, record, data)
        for field, value in prepare_data(resource, data).items():
            setattr(record, field, value)
        db.session.commit()
        return {"data": schema_class().dump(record)}

    def delete(self, resource, record_id):
        record = get_record(resource, record_id)
        if record is None:
            return self.not_found(resource, record_id)
        db.session.delete(record)
        db.session.commit()
        return "", 204

    @staticmethod
    def not_found(resource, record_id):
        model, _ = get_resource(resource)
        name = model.__name__ if model is not None else "Resource"
        return {"error": f"{name} {record_id} was not found.", "status": 404}, 404

    @staticmethod
    def validate_update(resource, record, data):
        if resource == "trains":
            total = data.get("total_seat", record.total_seat)
            available = data.get("available_seat", record.available_seat)
            if available > total:
                raise ValidationError({"available_seat": ["Must not exceed total_seat."]})
        elif resource == "schedules":
            from_station = data.get("from_station_id", record.from_station_id)
            to_station = data.get("to_station_id", record.to_station_id)
            if from_station == to_station:
                raise ValidationError({"to_station_id": ["Must differ from from_station_id."]})
            departure_time = data.get("departure_time", record.departure_time)
            arrival_time = data.get("arrival_time", record.arrival_time)
            if arrival_time <= departure_time:
                raise ValidationError({"arrival_time": ["Must be after departure_time."]})
        elif resource == "bookings":
            validate_booking({
                "train_id": data.get("train_id", record.train_id),
                "schedule_id": data.get("schedule_id", record.schedule_id),
            })


class FavouriteCollectionResource(Resource):
    def get(self):
        records = db.session.scalars(db.select(UserFavourite)).all()
        return {"data": UserFavouriteSchema(many=True).dump(records), "count": len(records)}

    def post(self):
        record = UserFavourite(**UserFavouriteSchema().load(json_body()))
        db.session.add(record)
        db.session.commit()
        return {"data": UserFavouriteSchema().dump(record)}, 201


class FavouriteResource(Resource):
    def delete(self, user_id, train_id, station_id):
        record = db.session.get(UserFavourite, (user_id, train_id, station_id))
        if record is None:
            return {"error": "Favourite was not found.", "status": 404}, 404
        db.session.delete(record)
        db.session.commit()
        return "", 204


rest_api.add_resource(CollectionResource, "/<string:resource>")
rest_api.add_resource(ItemResource, "/<string:resource>/<int:record_id>")
rest_api.add_resource(FavouriteCollectionResource, "/favourites")
rest_api.add_resource(
    FavouriteResource, "/favourites/<int:user_id>/<int:train_id>/<int:station_id>"
)
