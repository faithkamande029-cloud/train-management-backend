from flask import request, session
from flask_restful import Resource

from models import Payment, db
from schemas.payment_schema import PaymentSchema
from services.auth_service import login_required


class PaymentListResource(Resource):
    def get(self):
        payments = db.session.scalars(db.select(Payment)).all()
        return {"data": PaymentSchema(many=True).dump(payments), "count": len(payments)}

    @login_required
    def post(self):
        payload = request.get_json() or {}
        if "user_id" not in payload:
            payload["user_id"] = session.get("user_id")
        payment = Payment(**PaymentSchema().load(payload))
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
