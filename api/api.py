from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from flask_restful import Api, Resource
from flask import current_app

from models import db


class TrainManagementApi(Api):
    """Return JSON errors for all API resources."""

    def handle_error(self, error):
        if isinstance(error, ValidationError):
            return {
                "error": "Validation failed.",
                "status": 400,
                "details": error.messages,
            }, 400
        if isinstance(error, IntegrityError):
            db.session.rollback()
            return {"error": "The request conflicts with an existing record.", "status": 409}, 409
        if isinstance(error, HTTPException):
            return {"error": error.description, "status": error.code}, error.code

        db.session.rollback()
        current_app.logger.exception("Unhandled API error", exc_info=error)
        return {"error": "An unexpected server error occurred.", "status": 500}, 500
