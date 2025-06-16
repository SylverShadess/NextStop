from App.models import Route
from App.database import db

def get_all_routes():
    
    try:
        routes = Route.query.all()
    except Exception as e:
        print(f"Error fetching routes: {e}")
        return []
    
    if not routes:
        return []
    
    return routes
