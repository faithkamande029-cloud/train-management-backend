"Flask-RESTful resources for the train management service."""

from flask import request
from flask_restful import  Resource

from models import db, Station
from schemas.station_schema import StationSchema

class StationListResource(Resource):
    def get(self):
        stations = db.session.scalars(db.select(Station)).all()
        return {"data": StationSchema(many=True).dump(stations), "count": len(stations)}

    def post(self):
        station = Station(**StationSchema().load(request.get_json()))
        db.session.add(station)
        db.session.commit()
        return {"data": StationSchema().dump(station)}, 201


class StationResource(Resource):
    def get(self, station_id):
        station = db.session.get(Station, station_id)
        if station is None:
            return {"error": f"Station {station_id} was not found.", "status": 404}, 404
        return {"data": StationSchema().dump(station)}

    def patch(self, station_id):
        station = db.session.get(Station, station_id)
        if station is None:
            return {"error": f"Station {station_id} was not found.", "status": 404}, 404
        data = StationSchema().load(request.get_json(), partial=True)
        for field, value in data.items():
            setattr(station, field, value)
        db.session.commit()
        return {"data": StationSchema().dump(station)}

    def delete(self, station_id):
        station = db.session.get(Station, station_id)
        if station is None:
            return {"error": f"Station {station_id} was not found.", "status": 404}, 404
        db.session.delete(station)
        db.session.commit()
        return "", 204
