from App.database import db
from datetime import datetime

class BusEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    
    bus = db.relationship('Bus', backref='events')
    
    def __init__(self, bus, lat, lng, time=None):
        self.bus = bus
        self.lat = lat
        self.lng = lng
        self.time = time if time else datetime.utcnow()
    
    def get_json(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'time': self.time.isoformat(),
            'lat': self.lat,
            'lng': self.lng
        }