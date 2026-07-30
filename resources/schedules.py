from flask import  request
from flask_restful import Resource
from marshmallow import ValidationError

from models import Schedule, db 
from schemas.schedule_schema import ScheduleSchema



class ScheduleListResource(Resource):
    def get(self):
        schedules = db.session.scalars(db.select(Schedule)).all()
        return {"data": ScheduleSchema(many=True).dump(schedules), "count": len(schedules)}

    def post(self):
        schedule = Schedule(**ScheduleSchema().load(request.get_json()))
        db.session.add(schedule)
        db.session.commit()
        return {"data": ScheduleSchema().dump(schedule)}, 201


class ScheduleResource(Resource):
    def get(self, schedule_id):
        schedule = db.session.get(Schedule, schedule_id)
        if schedule is None:
            return {"error": f"Schedule {schedule_id} was not found.", "status": 404}, 404
        return {"data": ScheduleSchema().dump(schedule)}

    def patch(self, schedule_id):
        schedule = db.session.get(Schedule, schedule_id)
        if schedule is None:
            return {"error": f"Schedule {schedule_id} was not found.", "status": 404}, 404
        data = ScheduleSchema().load(request.get_json(), partial=True)
        from_station_id = data.get("from_station_id", schedule.from_station_id)
        to_station_id = data.get("to_station_id", schedule.to_station_id)
        if from_station_id == to_station_id:
            raise ValidationError({"to_station_id": ["Must differ from from_station_id."]})
        departure_time = data.get("departure_time", schedule.departure_time)
        arrival_time = data.get("arrival_time", schedule.arrival_time)
        if arrival_time <= departure_time:
            raise ValidationError({"arrival_time": ["Must be after departure_time."]})
        for field, value in data.items():
            setattr(schedule, field, value)
        db.session.commit()
        return {"data": ScheduleSchema().dump(schedule)}

    def delete(self, schedule_id):
        schedule = db.session.get(Schedule, schedule_id)
        if schedule is None:
            return {"error": f"Schedule {schedule_id} was not found.", "status": 404}, 404
        db.session.delete(schedule)
        db.session.commit()
        return "", 204

