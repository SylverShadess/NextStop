from App.models import Schedule

def get_stop_schedule(stop_id):
    return Schedule.query.filter_by(stop_id=stop_id).first()