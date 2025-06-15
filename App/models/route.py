from App.database import db
from App.models.Area import Area
from App.models.Location import Location

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    start_area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    end_area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    
    start_area = db.relationship('Area', foreign_keys=[start_area_id])
    end_area = db.relationship('Area', foreign_keys=[end_area_id])
    stops = db.relationship('Location', secondary='route_stop', order_by='RouteStop.stop_index')
    buses = db.relationship('Bus', back_populates='route')
    journeys = db.relationship('Journey', back_populates='route')
    schedules = db.relationship('Schedule', back_populates='route')
    
    def __init__(self, name, cost, start_area, end_area):
        self.name = name
        self.cost = cost
        self.start_area = start_area
        self.end_area = end_area
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'start_area': self.start_area.get_json() if self.start_area else None,
            'end_area': self.end_area.get_json() if self.end_area else None,
            'stops': [stop.get_json() for stop in self.stops]
        }