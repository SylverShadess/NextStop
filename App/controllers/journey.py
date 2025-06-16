from App.models import Journey, Route, RouteStop
from App.database import db

def get_journey_stats(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return None
    
    return journey.getStats()

def create_journey_track_event(journey_id, lat, lng):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return None
    
    return journey.trackEvent(lat, lng)


def create_journey_board_event(journey_id, type, qty, stop_id):
    journey = Journey.query.get(journey_id)
    if not journey:
        return None

    stop = RouteStop.query.get(stop_id)
    if not stop:
        return None

    return journey.boardEvent(type, qty, stop)

def complete_journey(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return None
    
    journey.completeJourney()
    return journey