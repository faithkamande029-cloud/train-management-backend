"""Request validation and response serialization for the API."""

from marshmallow import (
    RAISE,
    Schema,
    ValidationError,
    fields,
    validate,
    validates_schema,
    pre_load,
)

from models import PaymentMethod


class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


def _convert_camel_to_snake(data):
    if not isinstance(data, dict):
        return data
    replacements = {
        "bookingId": "booking_id",
        "userId": "user_id",
        "cardLast4": "card_last4",
        "transactionId": "transaction_id",
    }
    return {replacements.get(k, k): _convert_camel_to_snake(v) for k, v in data.items()}


class PaymentSchema(BaseSchema):
    booking_id = fields.Integer(required=True, validate=validate.Range(min=1))
    user_id = fields.Integer(required=True, validate=validate.Range(min=1))
    amount = fields.Decimal(
        required=True, as_string=True, places=2, validate=validate.Range(min=0)
    )
    method = fields.Enum(PaymentMethod, by_value=True, required=True)
    card_last4 = fields.String(allow_none=True, validate=validate.Length(equal=4))
    status = fields.String(required=True, validate=validate.Length(min=1, max=20))
    transaction_id = fields.String(
        required=True, validate=validate.Length(min=1, max=50)
    )

    @pre_load
    def normalize_keys(self, data, **kwargs):
        return _convert_camel_to_snake(data)
