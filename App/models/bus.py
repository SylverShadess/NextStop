from App.database import db
from App.models.route import Route
from App.models.bus_event import BusEvent
from App.models.board_event import BoardEvent

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_num = db.Column(db.String(20), nullable=False, unique=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    passenger_count = db.Column(db.Integer, nullable=False, default=0)
    
    driver = db.relationship('User', backref='buses')
    route = db.relationship('Route', backref='buses')
    
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
    
    def select_route(self, route_id):
        self.route_id = route_id
    
    def update_passenger_count(self, type, qty, stop_id):
        if(type == "Enter"):
            self.passenger_count += qty
            board_event = BoardEvent(self, "Enter", qty, stop_id)
            db.session.add(board_event)
            db.session.commit()
        elif(type == "Exit"):
            self.passenger_count -= qty
            board_event = BoardEvent(self, "Exit", qty, stop_id)
            db.session.add(board_event)
            db.session.commit()

    def log_bus_position(self, lat, lng):
        bus_event = BusEvent(self, lat, lng)
        db.session.add(bus_event)
        db.session.commit()

        
    def query_arrival_times(self):
        # Call the bus location events for when the bus was at a stop on the route to compare if the bus is on time
        pass
    
    def query_total_boards(self):
        # Call the board events for the bus to get the total number of boards during the route
        pass 

    # Temp name; needs to change to something more clear
    # Supposed to be the process of the bus on the route
    # Dunno what to name it tbh 
    def query_busline(self):
        pass 