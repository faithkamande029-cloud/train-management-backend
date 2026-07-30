"""Flask-RESTful resources for the train management service."""

from flask import Blueprint, request
from werkzeug.security import generate_password_hash

from resources.trains import TrainListResource, TrainResource
from resources.users import UserResource, UserListResource
from resources.stations import StationListResource, StationResource
from resources.schedules import ScheduleListResource, ScheduleResource
from resources.bookings import BookingListResource, BookingResource
from resources.payments import PaymentListResource, PaymentResource
from resources.favourites import FavouriteListResource, FavouriteResource

from api.api import TrainManagementApi

api = Blueprint("api", __name__, url_prefix="/api")

rest_api = TrainManagementApi(api)

rest_api.add_resource(UserListResource, "/users")
rest_api.add_resource(UserResource, "/users/<int:user_id>")
rest_api.add_resource(TrainListResource, "/trains")
rest_api.add_resource(TrainResource, "/trains/<int:train_id>")
rest_api.add_resource(StationListResource, "/stations")
rest_api.add_resource(StationResource, "/stations/<int:station_id>")
rest_api.add_resource(ScheduleListResource, "/schedules")
rest_api.add_resource(ScheduleResource, "/schedules/<int:schedule_id>")
rest_api.add_resource(BookingListResource, "/bookings")
rest_api.add_resource(BookingResource, "/bookings/<int:booking_id>")
rest_api.add_resource(PaymentListResource, "/payments")
rest_api.add_resource(PaymentResource, "/payments/<int:payment_id>")
rest_api.add_resource(FavouriteListResource, "/favourites")
rest_api.add_resource(
    FavouriteResource, "/favourites/<int:user_id>/<int:train_id>/<int:station_id>"
)
