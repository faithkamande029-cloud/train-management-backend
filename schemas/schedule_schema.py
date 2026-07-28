"""Request validation and response serialization for the API."""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

from models import (ScheduleStatus)


class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ScheduleSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    train_id = fields.Integer(required=True, validate=validate.Range(min=1))
    from_station_id = fields.Integer(required=True, validate=validate.Range(min=1))
    to_station_id = fields.Integer(required=True, validate=validate.Range(min=1))
    departure_time = fields.Time(required=True)
    arrival_time = fields.Time(required=True)
    status = fields.Enum(ScheduleStatus, by_value=True, required=True)
    platform = fields.Integer(required=True, validate=validate.Range(min=1))

    @validates_schema
    def validate_stations_and_times(self, data, **kwargs):
        errors = {}
        if (
            data.get("from_station_id") is not None
            and data.get("from_station_id") == data.get("to_station_id")
        ):
            errors["to_station_id"] = ["Must differ from from_station_id."]
        if (
            data.get("departure_time") is not None
            and data.get("arrival_time") is not None
            and data["arrival_time"] <= data["departure_time"]
        ):
            errors["arrival_time"] = ["Must be after departure_time."]
        if errors:
            raise ValidationError(errors)
