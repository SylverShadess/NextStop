from App.database import db
from datetime import datetime

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    arrivalTime = db.Column(db.DateTime, nullable=False)
    departureTime = db.Column(db.DateTime, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    
    stop = db.relationship('Location', back_populates='schedules')
    route = db.relationship('Route', back_populates='schedules')
    
    def __init__(self, stop, route, arrivalTime, departureTime):
        self.stop = stop
        self.route = route
        self.arrivalTime = arrivalTime
        self.departureTime = departureTime
    
    def get_json(self):
        return {
            'id': self.id,
            'stop': self.stop.get_json() if self.stop else None,
            'route': self.route.get_json() if self.route else None,
            'arrivalTime': self.arrivalTime.isoformat(),
            'departureTime': self.departureTime.isoformat()
        } 