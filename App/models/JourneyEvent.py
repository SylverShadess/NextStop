from App.database import db
from datetime import datetime

class JourneyEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('journey.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    
    journey = db.relationship('Journey', back_populates='events')
    
    def __init__(self, journey, lat, lng, time=None):
        self.journey_id = journey.id
        self.lat = lat
        self.lng = lng
        self.time = time if time else datetime.utcnow()
    
    def get_json(self):
        return {
            'id': self.id,
            'journey_id': self.journey_id,
            'time': self.time.isoformat(),
            'lat': self.lat,
            'lng': self.lng
        } 