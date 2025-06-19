from App.models.Journey import Journey
from App.models.JourneyEvent import JourneyEvent
from App.models.BoardEvent import BoardEvent, BoardType
from App.models.RouteStop import RouteStop
from App.database import db
from datetime import datetime, time
import traceback
import sys

def get_journey_stats(journey_id):
    try:
        # Debug output
        print(f"Fetching journey stats for journey_id: {journey_id}")
        
        journey = Journey.query.get(journey_id)
        
        if not journey:
            print(f"Journey with ID {journey_id} not found")
            return None
        
        print(f"Journey found: {journey.id}, route: {journey.route_id if journey.route else 'None'}")
        
        try:
            # Try to access relationships to see if they're loaded correctly
            if journey.route:
                print(f"Route name: {journey.route.name}")
            else:
                print("Route is None")
                
            if journey.driver:
                print(f"Driver username: {journey.driver.username}")
            else:
                print("Driver is None")
                
            if journey.bus:
                print(f"Bus plate: {journey.bus.plate_num}")
            else:
                print("Bus is None")
                
            # Get board events for debugging
            board_events = BoardEvent.query.filter(
                BoardEvent.journey_id == journey.id
            ).all()
            print(f"Found {len(board_events)} board events")
            
            # Get journey stats
            stats = journey.getStats()
            
            # Check if there was an error in getStats
            if 'error' in stats:
                print(f"Error in getStats for journey {journey_id}: {stats['error']}")
                # Remove the error message from the stats before returning
                error_msg = stats.pop('error', None)
            
            # Ensure stop_delays has the correct format
            if 'stop_delays' in stats and stats['stop_delays']:
                for delay in stats['stop_delays']:
                    # Make sure time fields are properly formatted as strings
                    if 'scheduled_time' in delay and not isinstance(delay['scheduled_time'], str):
                        delay['scheduled_time'] = delay['scheduled_time'].strftime('%H:%M:%S') if hasattr(delay['scheduled_time'], 'strftime') else str(delay['scheduled_time'])
                    
                    if 'actual_time' in delay and not isinstance(delay['actual_time'], str):
                        delay['actual_time'] = delay['actual_time'].strftime('%H:%M:%S') if hasattr(delay['actual_time'], 'strftime') else str(delay['actual_time'])
            
            return stats
        except Exception as inner_e:
            print(f"Error accessing journey relationships: {str(inner_e)}")
            # Print full traceback for debugging
            traceback.print_exc(file=sys.stdout)
            
            # Return a minimal stats object
            return {
                'journey_id': journey_id,
                'route_name': journey.route.name if journey.route else "Unknown",
                'start_time': journey.startTime.isoformat() if hasattr(journey, 'startTime') else "Unknown",
                'end_time': journey.endTime.isoformat() if hasattr(journey, 'endTime') and journey.endTime else None,
                'duration': "Unknown",
                'total_passengers': 0,
                'revenue': 0,
                'stop_delays': [],
                'error_details': str(inner_e)
            }
    except Exception as e:
        print(f"Error getting journey stats for journey {journey_id}: {str(e)}")
        # Print full traceback for debugging
        traceback.print_exc(file=sys.stdout)
        
        # Return a minimal stats object that won't cause template rendering errors
        return {
            'journey_id': journey_id,
            'route_name': "Unknown",
            'start_time': "Unknown",
            'end_time': None,
            'duration': "Unknown",
            'total_passengers': 0,
            'revenue': 0,
            'stop_delays': [],
            'error_details': str(e)
        }

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