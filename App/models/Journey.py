from math import floor
from App.database import db
from datetime import datetime
from .BoardEvent import BoardEvent
from .JourneyEvent import JourneyEvent
from .Route import Route


class Journey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    startTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    endTime = db.Column(db.DateTime, nullable=True)
    current_stop_index = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="In Progress")
    
    bus = db.relationship('Bus', backref='journeys')
    driver = db.relationship('Driver', back_populates='journeys')
    route = db.relationship('Route', backref='journeys')
    events = db.relationship('JourneyEvent', back_populates='journey', cascade='all, delete-orphan')
    board_events = db.relationship('BoardEvent', back_populates='journey')
    
    def __init__(self, driver, route, bus, startTime=None, endTime=None, status="In Progress"):
        self.driver = driver
        self.route = route
        self.bus = bus
        self.startTime = startTime if startTime else datetime.utcnow()
        self.endTime = endTime if endTime else None
        self.status = status
    
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
        event = BoardEvent(self, type, qty, stop)
        db.session.add(event)
        db.session.commit()
        return event
    
    def completeJourney(self):
        self.endTime = datetime.utcnow()
        self.status = "Completed"
        db.session.commit()
        
    def cancelJourney(self):
        self.endTime = datetime.utcnow()
        self.status = "Cancelled"
        db.session.commit()
        
    def getCurrentStop(self):
        """Get the current stop of the journey"""
        from .RouteStop import RouteStop
        return RouteStop.query.filter_by(
            route_id=self.route_id,
            stop_index=self.current_stop_index
        ).first()
        
    def getNextStop(self):
        """Get the next stop of the journey"""
        from .RouteStop import RouteStop
        return RouteStop.query.filter_by(
            route_id=self.route_id,
            stop_index=self.current_stop_index + 1
        ).first()
        
    def getPreviousStop(self):
        """Get the previous stop of the journey"""
        if self.current_stop_index <= 0:
            return None
            
        from .RouteStop import RouteStop
        return RouteStop.query.filter_by(
            route_id=self.route_id,
            stop_index=self.current_stop_index - 1
        ).first()
        
    def moveToNextStop(self):
        """Move to the next stop and create a journey event"""
        next_stop = self.getNextStop()
        if not next_stop:
            return False
            
        # Update current stop index
        self.current_stop_index += 1
        
        # Create journey event at the new stop's location
        lat = next_stop.location.lat
        lng = next_stop.location.lng
        self.trackEvent(lat, lng)
        
        db.session.commit()
        return True
        
    def moveToPreviousStop(self):
        """Move to the previous stop"""
        if self.current_stop_index <= 0:
            return False
            
        # Update current stop index
        self.current_stop_index -= 1
        db.session.commit()
        return True
        
    def calculateProgress(self):
        """Calculate the journey progress as a percentage"""
        from .RouteStop import RouteStop
        total_stops = RouteStop.query.filter_by(route_id=self.route_id).count()
        if total_stops == 0:
            return 0
            
        return int((self.current_stop_index / (total_stops - 1)) * 100) if total_stops > 1 else 100
    
    def getStats(self):
        # Get all board events for this journey during the journey timeframe
        board_events = BoardEvent.query.filter(
            BoardEvent.journey_id == self.id,
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
            duration = f"{int(minutes)}m {int(floor(seconds))}s"
        else:
            minutes = (datetime.utcnow() - self.startTime).total_seconds() // 60  
            seconds = (datetime.utcnow() - self.startTime).total_seconds() % 60
            duration = f"{int(minutes)}m {int(floor(seconds))}s"
        
        # Get stop delays - comparing actual arrival times with scheduled times
        stop_delays = []
        if self.route and self.route.stops:
            for route_stop in self.route.stops:
                # Find board events at this stop
                stop_events = [e for e in board_events if e.stop_id == route_stop.id]
                if stop_events:
                    # Get the first arrival at this stop
                    arrival_time = min(e.time for e in stop_events)
                    
                    # Get scheduled time if available
                    location = route_stop.location if hasattr(route_stop, 'location') else None
                    if location:
                        schedule = location.getSchedule(self.route_id)
                        if schedule:
                            # Calculate delay in minutes
                            scheduled_time = schedule.arrivalTime
                            delay = (arrival_time - scheduled_time).total_seconds() / 60
                            stop_delays.append({
                                'stop_name': location.name,
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
            'endTime': self.endTime.isoformat() if self.endTime else None,
            'status': self.status
        }
        
    @classmethod
    def get_journeys_for_driver(cls, driver_id):
        """Get all journeys for a specific driver"""
        try:
            return cls.query.filter_by(driver_id=driver_id).order_by(cls.startTime.desc()).all()
        except Exception as e:
            print(f"Error getting journeys for driver {driver_id}: {str(e)}")
            return [] 