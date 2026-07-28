"""Request validation and response serialization for the API."""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserFavouriteSchema(Schema):
    user_id = fields.Integer(required=True, validate=validate.Range(min=1))
    train_id = fields.Integer(required=True, validate=validate.Range(min=1))
    station_id = fields.Integer(required=True, validate=validate.Range(min=1))
    created_at = fields.DateTime(dump_only=True)
