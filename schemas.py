from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import (
    User, Train, Station, Schedule, Booking, Payment, UserFavourite,
    UserRole, UserStatus, TrainType, TrainStatus,
    ScheduleStatus, BookingStatus, PaymentMethod
)


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_relationships = False
        include_fk = False
        fields = (
            "id", "first_name", "last_name", "email",
            "password", "phone_number", "date_of_birth",
            "role", "status", "created_at", "updated_at"
        )
        dump_only = ("id", "created_at", "updated_at")
        load_only = ("password",)

    role = fields.Method(serialize="get_role", deserialize="load_role")
    status = fields.Method(serialize="get_status", deserialize="load_status")

    def get_role(self, obj):
        return obj.role.value if obj.role else None

    def load_role(self, value):
        if isinstance(value, str):
            for member in UserRole:
                if member.value == value.lower():
                    return member
        return value

    def get_status(self, obj):
        return obj.status.value if obj.status else None

    def load_status(self, value):
        if isinstance(value, str):
            for member in UserStatus:
                if member.value == value.lower():
                    return member
        return value


class TrainSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Train
        load_instance = True
        include_relationships = False
        include_fk = False
        fields = (
            "id", "name", "type", "total_seat", "available_seat",
            "status", "description", "created_at", "updated_at"
        )
        dump_only = ("id", "created_at", "updated_at")

    type = fields.Method(serialize="get_type", deserialize="load_type")
    status = fields.Method(serialize="get_status", deserialize="load_status")

    def get_type(self, obj):
        return obj.type.value if obj.type else None

    def load_type(self, value):
        if isinstance(value, str):
            for member in TrainType:
                if member.value == value.lower():
                    return member
        return value

    def get_status(self, obj):
        return obj.status.value if obj.status else None

    def load_status(self, value):
        if isinstance(value, str):
            for member in TrainStatus:
                if member.value == value.lower():
                    return member
        return value


class StationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Station
        load_instance = True
        include_relationships = False
        include_fk = False
        fields = (
            "id", "name", "train_number", "city",
            "platform", "description", "created_at", "updated_at"
        )
        dump_only = ("id", "created_at", "updated_at")


class ScheduleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Schedule
        load_instance = True
        include_relationships = False
        include_fk = True
        fields = (
            "id", "name", "train_id", "from_station_id", "to_station_id",
            "departure_time", "arrival_time", "status",
            "platform", "created_at", "updated_at"
        )
        dump_only = ("id", "created_at", "updated_at")

    status = fields.Method(serialize="get_status", deserialize="load_status")

    def get_status(self, obj):
        return obj.status.value if obj.status else None

    def load_status(self, value):
        if isinstance(value, str):
            for member in ScheduleStatus:
                if member.value == value.lower():
                    return member
        return value


class BookingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True
        include_relationships = False
        include_fk = True
        fields = (
            "id", "booking_ref", "passenger_name", "email", "phone",
            "train_id", "schedule_id", "seat_number", "fare",
            "status", "from_station", "to_station", "departure_time",
            "created_at", "updated_at"
        )
        dump_only = ("id", "created_at", "updated_at")

    status = fields.Method(serialize="get_status", deserialize="load_status")

    def get_status(self, obj):
        return obj.status.value if obj.status else None

    def load_status(self, value):
        if isinstance(value, str):
            for member in BookingStatus:
                if member.value == value.lower():
                    return member
        return value


class PaymentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True
        include_relationships = False
        include_fk = True
        fields = (
            "id", "booking_id", "user_id", "amount",
            "method", "card_last4", "status", "transaction_id",
            "created_at", "updated_at"
        )
        dump_only = ("id", "created_at", "updated_at")

    method = fields.Method(serialize="get_method", deserialize="load_method")

    def get_method(self, obj):
        return obj.method.value if obj.method else None

    def load_method(self, value):
        if isinstance(value, str):
            for member in PaymentMethod:
                if member.value == value.lower():
                    return member
        return value


class UserFavouriteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserFavourite
        load_instance = True
        include_relationships = False
        include_fk = True
        fields = ("id", "user_id", "train_id", "station_id", "created_at")
        dump_only = ("id", "created_at")