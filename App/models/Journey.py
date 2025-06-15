from App.database import db
from datetime import datetime
from App.models import Route, BoardEvent, JourneyEvent

class Journey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    startTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    endTime = db.Column(db.DateTime, nullable=True)
    
    bus = db.relationship('Bus', backref='journeys')
    driver = db.relationship('Driver', backref='journeys')
    route = db.relationship('Route', backref='journeys')
    events = db.relationship('JourneyEvent', back_populates='journey', cascade='all, delete-orphan')
    
    def __init__(self, driver, route, bus, startTime=None):
        self.driver = driver
        self.route = route
        self.bus = bus
        self.startTime = startTime if startTime else datetime.utcnow()
    
    def getRoutes(self):
        return Route.query.all()
    
    def startJourney(self):
        db.session.add(self)
        db.session.commit()
        
    def trackEvent(self, lat, lng):
        event = JourneyEvent(self, lat, lng)
        db.session.add(event)
        db.session.commit()
        return event
    
    def boardEvent(self, type, qty, stop):
        event = BoardEvent(self.bus, type, qty, stop)
        db.session.add(event)
        db.session.commit()
        return event
    
    def completeJourney(self):
        self.endTime = datetime.utcnow()
        db.session.commit()
    
    def getStats(self):
        # Get all board events for this journey's bus during the journey timeframe
        board_events = BoardEvent.query.filter(
            BoardEvent.bus_id == self.bus_id,
            BoardEvent.time >= self.startTime,
            BoardEvent.time <= (self.endTime or datetime.utcnow())
        ).all()
        
        # Calculate passenger statistics
        total_entries = 0
        total_exits = 0
        
        for event in board_events:
            if event.type == "Enter":
                total_entries += event.qty
            elif event.type == "Exit":
                total_exits += event.qty
        
        # Calculate revenue based on route cost and passengers
        revenue = total_entries * self.route.cost if self.route else 0
        
        # Calculate journey duration
        if self.endTime:
            minutes = (self.endTime - self.startTime).total_seconds() // 60  
            seconds = (self.endTime - self.startTime).total_seconds() % 60
            duration = f"{minutes}m {seconds}s"
        else:
            minutes = (datetime.utcnow() - self.startTime).total_seconds() // 60  
            seconds = (datetime.utcnow() - self.startTime).total_seconds() % 60
            duration = f"{minutes}m {seconds}s"
        
        # Get stop delays - comparing actual arrival times with scheduled times
        stop_delays = []
        if self.route and self.route.stops:
            for stop in self.route.stops:
                # Find board events at this stop
                stop_events = [e for e in board_events if e.stop_id == stop.id]
                if stop_events:
                    # Get the first arrival at this stop
                    arrival_time = min(e.time for e in stop_events)
                    
                    # Get scheduled time if available
                    schedule = stop.getSchedule(self.route_id)
                    if schedule:
                        # Calculate delay in minutes
                        scheduled_time = schedule.time
                        delay = (arrival_time - scheduled_time).total_seconds() / 60
                        stop_delays.append({
                            'stop_name': stop.name,
                            'scheduled_time': scheduled_time.isoformat(),
                            'actual_time': arrival_time.isoformat(),
                            'delay_minutes': round(delay, 2)
                        })
        
        return {
            'journey_id': self.id,
            'route_name': self.route.name if self.route else None,
            'start_time': self.startTime.isoformat(),
            'end_time': self.endTime.isoformat() if self.endTime else None,
            'duration': duration,
            'total_passengers': total_entries,
            'revenue': revenue,
            'stop_delays': stop_delays
        }
    
    def get_json(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'driver_id': self.driver_id,
            'route_id': self.route_id,
            'startTime': self.startTime.isoformat(),
            'endTime': self.endTime.isoformat() if self.endTime else None
        } 