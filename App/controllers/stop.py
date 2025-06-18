from App.models import Location, RouteStop

def get_buses(stop_id, route_id):
    """Get buses approaching a specific stop on a route"""
    try:
        # Get the stop
        stop = RouteStop.query.get(stop_id)
        if not stop:
            return []
        
        # Get the location
        location = Location.query.get(stop.location_id)
        if not location:
            return []
        
        # Use the location's getBuses method to get approaching buses
        return location.getBuses(route_id)
    except Exception as e:
        print(f"Error in get_buses: {str(e)}")
        return []