"Flask-RESTful resources for the train management service."""

from flask import Blueprint, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from models import db, Train

from schemas.train_schema import TrainSchema

class TrainListResource(Resource):
    def get(self):
        trains = db.session.scalars(db.select(Train)).all()
        return {"data": TrainSchema(many=True).dump(trains), "count": len(trains)}

    def post(self):
        train = Train(**TrainSchema().load(request.get_json()))
        db.session.add(train)
        db.session.commit()
        return {"data": TrainSchema().dump(train)}, 201


class TrainResource(Resource):
    def get(self, train_id):
        train = db.session.get(Train, train_id)
        if train is None:
            return {"error": f"Train {train_id} was not found.", "status": 404}, 404
        return {"data": TrainSchema().dump(train)}

    def patch(self, train_id):
        train = db.session.get(Train, train_id)
        if train is None:
            return {"error": f"Train {train_id} was not found.", "status": 404}, 404
        data = TrainSchema().load(request.get_json(), partial=True)
        total_seat = data.get("total_seat", train.total_seat)
        available_seat = data.get("available_seat", train.available_seat)
        if available_seat > total_seat:
            raise ValidationError({"available_seat": ["Must not exceed total_seat."]})
        for field, value in data.items():
            setattr(train, field, value)
        db.session.commit()
        return {"data": TrainSchema().dump(train)}

    def delete(self, train_id):
        train = db.session.get(Train, train_id)
        if train is None:
            return {"error": f"Train {train_id} was not found.", "status": 404}, 404
        db.session.delete(train)
        db.session.commit()
        return "", 204

