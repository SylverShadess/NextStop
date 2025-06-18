from App.models.Journey import Journey
from App.models.JourneyEvent import JourneyEvent
from App.models.BoardEvent import BoardEvent, BoardType
from App.models.RouteStop import RouteStop
from App.database import db
from datetime import datetime

def get_journey_stats(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return None
    
    return journey.getStats()

def create_journey_board_event(journey_id, event_type, qty, stop_id):
    try:
        journey = Journey.query.get(journey_id)
        stop = RouteStop.query.get(stop_id)
        
        if not journey or not stop:
            return None
        
        board_type = BoardType.set_type(event_type)
        event = BoardEvent(journey, board_type, qty, stop)
        db.session.add(event)
        db.session.commit()
        return event
    except Exception as e:
        print(f"Error creating board event: {str(e)}")
        db.session.rollback()
        raise ValueError(str(e))

def create_journey_track_event(journey_id, lat, lng):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return None
    
    try:
        event = JourneyEvent(journey, lat, lng)
        db.session.add(event)
        db.session.commit()
        return event
    except Exception as e:
        print(f"Error creating track event: {str(e)}")
        db.session.rollback()
        return None

def complete_journey(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return False
    
    try:
        journey.completeJourney()
        return journey
    except Exception as e:
        print(f"Error completing journey: {str(e)}")
        db.session.rollback()
        return False
        
def cancel_journey(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return False
    
    try:
        journey.cancelJourney()
        return journey
    except Exception as e:
        print(f"Error cancelling journey: {str(e)}")
        db.session.rollback()
        return False
        
def move_to_next_stop(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return None
    
    try:
        if journey.moveToNextStop():
            return journey.getCurrentStop()
        return None
    except Exception as e:
        print(f"Error moving to next stop: {str(e)}")
        db.session.rollback()
        return None
        
def move_to_previous_stop(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return None
    
    try:
        if journey.moveToPreviousStop():
            return journey.getCurrentStop()
        return None
    except Exception as e:
        print(f"Error moving to previous stop: {str(e)}")
        db.session.rollback()
        return None
        
def get_journey_progress(journey_id):
    journey = Journey.query.get(journey_id)
    
    if not journey:
        return 0
    
    return journey.calculateProgress()