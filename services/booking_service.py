from marshmallow import ValidationError
from models import Schedule, db


def validate_booking(train_id, schedule_id):
    schedule = db.session.get(Schedule, schedule_id)

    if schedule is None:
        raise ValidationError({
            "schedule_id": ["Schedule does not exist."]
        })
    if schedule.train_id != train_id:
        raise ValidationError({
            "train_id": ["Must match the selected schedule's train."]
        })

