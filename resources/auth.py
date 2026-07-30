from flask import request, session
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from models import  db, User
from schemas.user_schema import UserSchema
from schemas.auth_schema import login_schema


class RegistrationResource(Resource):
    def post(self):
        print("REGISTER ENDPOINT HIT")
        data = UserSchema().load(request.get_json())

        if db.session.scalar(
            db.select(User).filter_by(email=data["email"])
        ):
            return {
                "error": "An account with this email already exists.",
                "status": 409,
            }, 409
        
        if db.session.scalar(
            db.select(User).filter_by(phone_number=data["phone_number"])
        ): 
            return{
                "error": "The phone number is already registered",
                "status": 409
            }, 409
        data["password"] = generate_password_hash(data["password"])

        user = User(**data)

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["role"] = user.role.value

        return {
            "message": "Account created successfully",
            "data": UserSchema().dump(user)
        }, 201

class LoginResource(Resource):
    def post(self):
        data = login_schema.load(request.get_json())

        user = db.session.scalar(
            db.select(User).filter_by(email=data["email"])
        )    

        if user is None or not check_password_hash(
            user.password,
            data["password"],
        ): 
            return {
                "error": "Invalid email or password",
                "status": 401
            }, 401

        session["user_id"] = user.id
        session["role"] = user.role.value

        return {
            "message": "Login successful.",
            "data": UserSchema().dump(user),
        }, 200   


class LogoutResource(Resource):
    def delete(self):
        session.clear()
        return {}, 204

class CheckSessionResource(Resource):
    def get(self):
        user_id = session.get("user_id")

        if user_id is None:
            return {
                "error": "You are not authenticated",
                "status": 401,                
            }, 401

        user = db.session.get(User, user_id)

        if user is None:
            session.clear()
            return {
                "error": "Session is invalid.",
                "status": 401
            }, 401
        return {
            "data": UserSchema().dump(user)
        }, 200