"""Request validation and response serialization for the API."""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

from models import (UserRole, UserStatus,)


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
