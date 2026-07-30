"""Flask-RESTful resources for the train management service."""

from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash

from models import db, User
from schemas.user_schema import UserSchema

class UserListResource(Resource):
    def get(self):
        users = db.session.scalars(db.select(User)).all()
        return {"data": UserSchema(many=True).dump(users), "count": len(users)}

    def post(self):
        data = UserSchema().load(request.get_json())
        data["password"] = generate_password_hash(data["password"])
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return {"data": UserSchema().dump(user)}, 201


class UserResource(Resource):
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": f"User {user_id} was not found.", "status": 404}, 404
        return {"data": UserSchema().dump(user)}

    def patch(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": f"User {user_id} was not found.", "status": 404}, 404
        data = UserSchema().load(request.get_json(), partial=True)
        if "password" in data:
            data["password"] = generate_password_hash(data["password"])
        for field, value in data.items():
            setattr(user, field, value)
        db.session.commit()
        return {"data": UserSchema().dump(user)}

    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": f"User {user_id} was not found.", "status": 404}, 404
        db.session.delete(user)
        db.session.commit()
        return "", 204
