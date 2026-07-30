"""Request validation and response serialization for the API."""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

from models import (BookingStatus)

class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class BookingSchema(BaseSchema):
    booking_ref = fields.String(required=True, validate=validate.Length(min=1))
    passenger_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    phone = fields.String(required=True, validate=validate.Length(min=7, max=20))
    train_id = fields.Integer(required=True, validate=validate.Range(min=1))
    schedule_id = fields.Integer(required=True, validate=validate.Range(min=1))
    seat_number = fields.String(required=True, validate=validate.Length(min=1, max=10))
    fare = fields.Decimal(required=True, as_string=True, places=2, validate=validate.Range(min=0))
    status = fields.Enum(BookingStatus, by_value=True, required=True)
    from_station = fields.String(required=True, validate=validate.Length(min=1, max=100))
    to_station = fields.String(required=True, validate=validate.Length(min=1, max=100))
    departure_time = fields.Time(required=True)