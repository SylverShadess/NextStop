from App.database import db
from enum import Enum

class LocationType(Enum):
    STOP = "Stop"
    TERMINAL = "Terminal"

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Integer, nullable=False)
    lng = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    
    def __init__(self, name, lat, lng, type):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.type = type.value if isinstance(type, LocationType) else type
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'lat': self.lat,
            'lng': self.lng,
            'type': self.type
        } 