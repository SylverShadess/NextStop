from App.database import db

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_num = db.Column(db.String(20), nullable=False, unique=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    passenger_count = db.Column(db.Integer, nullable=False, default=0)
    
    driver = db.relationship('Driver', back_populates='buses')
    route = db.relationship('Route', back_populates='buses')
    board_events = db.relationship('BoardEvent', back_populates='bus')
    journeys = db.relationship('Journey', back_populates='bus')
    
    def __init__(self, plate_num, driver=None, route=None):
        self.plate_num = plate_num
        self.driver = driver
        self.route = route
        self.passenger_count = 0
    
    def get_json(self):
        return {
            'id': self.id,
            'plate_num': self.plate_num,
            'driver': self.driver.get_json() if self.driver else None,
            'route': self.route.get_json() if self.route else None,
            'passenger_count': self.passenger_count
        }
    
    def selectRoute(self, route):
        self.route = route
        bus = Bus.query.get(self.id)
        bus.route = route
        db.session.commit()