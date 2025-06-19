from App.database import db
from enum import Enum

from .Schedule import Schedule
from .Journey import Journey
from .JourneyEvent import JourneyEvent
from .Route import Route
from .RouteStop import RouteStop
from .BoardEvent import BoardEvent

from sqlalchemy import func, desc
import os
from datetime import datetime, timedelta
import openrouteservice
from App.config import config

class LocationType(Enum):
    Stop = "Stop"
    Terminal = "Terminal"

    def set_type(type):
        if type == "Stop":
            return LocationType.Stop
        elif type == "Terminal":
            return LocationType.Terminal


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    
    routes = db.relationship('Route', secondary='route_stop', viewonly=True)
    schedules = db.relationship('Schedule', back_populates='stop')
    
    def __init__(self, name, lat, lng, type):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.type = type.value if isinstance(type, LocationType) else LocationType.set_type(type).value
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'lat': self.lat,
            'lng': self.lng,
            'type': self.type.value
        }
        
    def getSchedule(self, route_id):
        return Schedule.query.filter(Schedule.route_id == route_id, Schedule.stop_id == self.id).first()
        
    def getBuses(self, route_id):
        # Get API key from environment variable
        ors_api_key = config.get('OPENROUTE_SERVICE_KEY', '')
        
        # Check if API key is valid
        if not ors_api_key:
            print("Warning: OpenRouteService API key not configured")
            return []
        
        # Find this stop's position in the route
        current_stop_position = RouteStop.query.filter_by(
            route_id=route_id, 
            location_id=self.id
        ).first()
        
        if not current_stop_position:
            return []  # This stop is not on the route
        
        # Find the previous stop in the route
        previous_stop_position = RouteStop.query.filter_by(
            route_id=route_id, 
            stop_index=current_stop_position.stop_index - 1
        ).first()
        
        if not previous_stop_position:
            return []  # There is no previous stop (this is the first stop)
        
        # Find active journeys on this route
        active_journeys = Journey.query.filter_by(route_id=route_id, endTime=None).all()
        
        if not active_journeys:
            return []
        
        # Find buses that have board events at the previous stop but not at the current stop
        buses_between_stops = []
        
        for journey in active_journeys:
            # Get the bus for this journey
            bus = journey.bus
            
            # Check if there are board events for this bus at the previous stop
            previous_stop_event = BoardEvent.query.filter_by(
                journey_id=journey.id,
                stop_id=previous_stop_position.id
            ).order_by(BoardEvent.time.desc()).first()
            
            # Check if there are board events for this bus at the current stop
            current_stop_event = BoardEvent.query.filter_by(
                journey_id=journey.id,
                stop_id=current_stop_position.id
            ).order_by(BoardEvent.time.desc()).first()
            
            # If there are events at the previous stop but none at the current stop,
            # or if the most recent event at the previous stop is more recent than
            # the most recent event at the current stop, the bus is between stops
            if previous_stop_event and (not current_stop_event or 
                                        previous_stop_event.time > current_stop_event.time):
                buses_between_stops.append(journey)
        
        if not buses_between_stops:
            return []
        
        # Get latest position for each journey
        bus_info = []
        
        for journey in buses_between_stops:
            # Get the latest event for this journey
            latest_event = JourneyEvent.query.filter_by(
                journey_id=journey.id
            ).order_by(JourneyEvent.time.desc()).first()
            
            if latest_event:
                bus_info.append({
                    'journey': journey,
                    'bus': journey.bus,
                    'lat': latest_event.lat,
                    'lng': latest_event.lng,
                    'last_updated': latest_event.time
                })
        
        if not bus_info:
            return []
        
        try:
            # Initialize the OpenRouteService client
            client = openrouteservice.Client(key=ors_api_key)
            
            # Create coordinates list with current location as first entry
            coordinates = [[self.lng, self.lat]]
            
            # Add bus coordinates
            for info in bus_info:
                coordinates.append([info['lng'], info['lat']])
            
            # Make API request with both distance and duration metrics using the Python client
            try:
                matrix = client.distance_matrix(
                    locations=coordinates,
                    profile='driving-car',
                    metrics=['distance', 'duration'],
                    units='m'  # meters
                )
                
                # Process results
                distances = matrix['distances'][0]  # First row contains distances from our location
                durations = matrix['durations'][0]  # First row contains durations from our location
                
                # Skip the first entries (which are 0, distance/duration to self)
                for i in range(len(distances) - 1):
                    distance = distances[i + 1]
                    duration_seconds = durations[i + 1]
                    
                    # Calculate estimated arrival time
                    now = datetime.utcnow()
                    arrival_time = now + timedelta(seconds=duration_seconds)
                    
                    # Format arrival time for display
                    arrival_time_str = arrival_time.strftime('%H:%M:%S')
                    
                    # Update bus info with distance and duration
                    bus_info[i]['distance'] = distance
                    bus_info[i]['duration_seconds'] = duration_seconds
                    bus_info[i]['estimated_arrival'] = arrival_time_str
                
                # Sort by distance and take the closest 3
                bus_info.sort(key=lambda x: x['distance'])
                return bus_info[:3]
                
            except openrouteservice.exceptions.ApiError as e:
                print(f"OpenRouteService API error: {str(e)}")
                # Fallback: Estimate using straight-line distance
                return self._fallback_distance_calculation(bus_info)
                
        except Exception as e:
            # Handle any errors from the OpenRouteService client
            print(f"Error calculating distances: {str(e)}")
            # Fallback: Estimate using straight-line distance
            return self._fallback_distance_calculation(bus_info)
            
    def _fallback_distance_calculation(self, bus_info):
        """Fallback method to calculate straight-line distance and estimated arrival"""
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine(lat1, lon1, lat2, lon2):
            # Calculate the great circle distance between two points
            # on the earth (specified in decimal degrees)
            R = 6371000  # Earth radius in meters
            
            # Convert decimal degrees to radians
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            return distance
        
        # Average bus speed in meters per second (30 km/h)
        avg_speed = 8.33  # m/s
        
        for info in bus_info:
            # Calculate straight-line distance
            distance = haversine(self.lat, self.lng, info['lat'], info['lng'])
            
            # Estimate duration (add 30% to account for roads not being straight)
            duration_seconds = (distance * 1.3) / avg_speed
            
            # Calculate estimated arrival time
            now = datetime.utcnow()
            arrival_time = now + timedelta(seconds=duration_seconds)
            
            # Format arrival time for display
            arrival_time_str = arrival_time.strftime('%H:%M:%S')
            
            # Update bus info
            info['distance'] = distance
            info['duration_seconds'] = duration_seconds
            info['estimated_arrival'] = arrival_time_str
        
        # Sort by distance and take the closest 3
        bus_info.sort(key=lambda x: x['distance'])
        return bus_info[:3]