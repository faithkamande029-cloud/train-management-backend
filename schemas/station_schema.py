"""Request validation and response serialization for the API."""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class StationSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    train_number = fields.String(required=True, validate=validate.Length(min=1, max=10))
    city = fields.String(required=True, validate=validate.Length(min=1, max=50))
    platform = fields.Integer(required=True, validate=validate.Range(min=1))
    description = fields.String(allow_none=True)
