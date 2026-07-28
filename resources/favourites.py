from flask import Blueprint, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from models import  UserFavourite, db
from schemas.favourite_schema import  UserFavouriteSchema

class FavouriteListResource(Resource):
    def get(self):
        favourites = db.session.scalars(db.select(UserFavourite)).all()
        return {"data": UserFavouriteSchema(many=True).dump(favourites), "count": len(favourites)}

    def post(self):
        favourite = UserFavourite(**UserFavouriteSchema().load(request.get_json()))
        db.session.add(favourite)
        db.session.commit()
        return {"data": UserFavouriteSchema().dump(favourite)}, 201


class FavouriteResource(Resource):
    def delete(self, user_id, train_id, station_id):
        favourite = db.session.get(UserFavourite, (user_id, train_id, station_id))
        if favourite is None:
            return {"error": "Favourite was not found.", "status": 404}, 404
        db.session.delete(favourite)
        db.session.commit()
        return "", 204

