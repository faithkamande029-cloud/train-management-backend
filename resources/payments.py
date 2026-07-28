from flask import Blueprint, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from models import Payment, db 

from schemas.payment_schema import PaymentSchema

class PaymentListResource(Resource):
    def get(self):
        payments = db.session.scalars(db.select(Payment)).all()
        return {"data": PaymentSchema(many=True).dump(payments), "count": len(payments)}

    def post(self):
        payment = Payment(**PaymentSchema().load(request.get_json()))
        db.session.add(payment)
        db.session.commit()
        return {"data": PaymentSchema().dump(payment)}, 201


class PaymentResource(Resource):
    def get(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        return {"data": PaymentSchema().dump(payment)}

    def patch(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        data = PaymentSchema().load(request.get_json(), partial=True)
        for field, value in data.items():
            setattr(payment, field, value)
        db.session.commit()
        return {"data": PaymentSchema().dump(payment)}

    def delete(self, payment_id):
        payment = db.session.get(Payment, payment_id)
        if payment is None:
            return {"error": f"Payment {payment_id} was not found.", "status": 404}, 404
        db.session.delete(payment)
        db.session.commit()
        return "", 204
