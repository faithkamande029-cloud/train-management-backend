"""Request validation and response serialization for the API."""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

from models import (TrainStatus, TrainType)

class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


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