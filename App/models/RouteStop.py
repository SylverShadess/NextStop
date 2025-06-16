from App.database import db

class RouteStop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    stop_index = db.Column(db.Integer, nullable=False)
    
    location = db.relationship('Location')
    route = db.relationship('Route', back_populates='stops')
    board_events = db.relationship('BoardEvent', back_populates='stop')
    
    def __init__(self, route, location, stop_index):
        self.route = route
        self.location = location
        self.stop_index = stop_index
        
    def get_json(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'location': self.location.get_json() if self.location else None,
            'stop_index': self.stop_index
        } 