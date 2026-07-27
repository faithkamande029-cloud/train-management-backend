"""Request validation and response serialization for the API."""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

from models import (
    BookingStatus,
    PaymentMethod,
    ScheduleStatus,
    TrainStatus,
    TrainType,
    UserRole,
    UserStatus,
)


class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserSchema(BaseSchema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=150))
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8, max=255))
    phone_number = fields.String(required=True, validate=validate.Length(min=7, max=30))
    date_of_birth = fields.Date(required=True)
    role = fields.Enum(UserRole, by_value=True, load_default=UserRole.PASSENGER)
    status = fields.Enum(UserStatus, by_value=True, load_default=UserStatus.ACTIVE)


class TrainSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    type = fields.Enum(TrainType, by_value=True, required=True)
    total_seat = fields.Integer(required=True, validate=validate.Range(min=1))
    available_seat = fields.Integer(required=True, validate=validate.Range(min=0))
    status = fields.Enum(TrainStatus, by_value=True, required=True)
    description = fields.String(allow_none=True)

    @validates_schema
    def validate_capacity(self, data, **kwargs):
        total = data.get("total_seat")
        available = data.get("available_seat")
        if total is not None and available is not None and available > total:
            raise ValidationError(
                {"available_seat": ["Must not exceed total_seat."]}
            )


class StationSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    train_number = fields.String(required=True, validate=validate.Length(min=1, max=10))
    city = fields.String(required=True, validate=validate.Length(min=1, max=50))
    platform = fields.Integer(required=True, validate=validate.Range(min=1))
    description = fields.String(allow_none=True)


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


class PaymentSchema(BaseSchema):
    booking_id = fields.Integer(required=True, validate=validate.Range(min=1))
    user_id = fields.Integer(required=True, validate=validate.Range(min=1))
    amount = fields.Decimal(required=True, as_string=True, places=2, validate=validate.Range(min=0))
    method = fields.Enum(PaymentMethod, by_value=True, required=True)
    card_last4 = fields.String(allow_none=True, validate=validate.Length(equal=4))
    status = fields.String(required=True, validate=validate.Length(min=1, max=20))
    transaction_id = fields.String(required=True, validate=validate.Length(min=1, max=50))


class UserFavouriteSchema(Schema):
    user_id = fields.Integer(required=True, validate=validate.Range(min=1))
    train_id = fields.Integer(required=True, validate=validate.Range(min=1))
    station_id = fields.Integer(required=True, validate=validate.Range(min=1))
    created_at = fields.DateTime(dump_only=True)
