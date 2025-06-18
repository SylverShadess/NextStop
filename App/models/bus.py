from App.database import db

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_num = db.Column(db.String(20), nullable=False, unique=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    passenger_count = db.Column(db.Integer, nullable=False, default=0)
    max_passenger_count = db.Column(db.Integer, nullable=False, default=50)
    
    driver = db.relationship('Driver', back_populates='buses')
    route = db.relationship('Route', back_populates='buses')
    
    def __init__(self, plate_num, driver=None, route=None, max_passenger_count=50):
        self.plate_num = plate_num
        self.driver = driver
        self.route = route
        self.passenger_count = 0
        self.max_passenger_count = max_passenger_count
    
    def get_json(self):
        return {
            'id': self.id,
            'plate_num': self.plate_num,
            'driver': self.driver.get_json() if self.driver else None,
            'route': self.route.get_json() if self.route else None,
            'passenger_count': self.passenger_count,
            'max_passenger_count': self.max_passenger_count,
            'available_seats': self.max_passenger_count - self.passenger_count
        }
    
    def selectRoute(self, route):
        self.route = route
        db.session.commit()
        
    def board_passengers(self, count):
        """Add passengers to the bus, ensuring we don't exceed max capacity"""
        if count <= 0:
            return False
            
        if self.passenger_count + count > self.max_passenger_count:
            return False
            
        self.passenger_count += count
        db.session.commit()
        return True
        
    def alight_passengers(self, count):
        """Remove passengers from the bus, ensuring we don't go below 0"""
        if count <= 0:
            return False
            
        if self.passenger_count - count < 0:
            return False
            
        self.passenger_count -= count
        db.session.commit()
        return True
        
    def get_available_seats(self):
        """Get the number of available seats on the bus"""
        return self.max_passenger_count - self.passenger_count