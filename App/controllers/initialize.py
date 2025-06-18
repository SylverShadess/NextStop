from .user import create_user
from App.database import db
from App.models.User import User, Driver
from App.models.Journey import Journey
from App.models.Route import Route
from App.models.Location import Location, LocationType
from App.models.Bus import Bus
from App.models.Area import Area
from App.models.RouteStop import RouteStop

def initialize():
    db.drop_all()
    db.create_all()
    
    # Create demo data
    create_demo_data()
    
    return True

def create_demo_data():
    # Create areas
    san_fernando = Area("San Fernando")
    port_of_spain = Area("Port of Spain")
    st_augustine = Area("St. Augustine")
    db.session.add_all([san_fernando, port_of_spain, st_augustine])
    db.session.commit()
    
    # Create routes
    route1 = Route("San Fernando to Port of Spain", 25, san_fernando, port_of_spain)
    route2 = Route("San Fernando to St. Augustine", 20, san_fernando, st_augustine)
    db.session.add_all([route1, route2])
    db.session.commit()
    
    # Create locations (terminals and stops)
    san_fernando_terminal = Location("San Fernando Bus Terminal", 10.2799, -61.4702, LocationType.Terminal)
    couva_stop = Location("Couva Stop", 10.4213, -61.4111, LocationType.Stop)
    chaguanas_stop = Location("Chaguanas Stop", 10.5158, -61.4113, LocationType.Stop)
    port_of_spain_terminal = Location("Port of Spain Bus Terminal", 10.6572, -61.5180, LocationType.Terminal)
    uwi_stop = Location("U.W.I. Bus Stop", 10.6384, -61.4023, LocationType.Stop)
    
    db.session.add_all([
        san_fernando_terminal, couva_stop, chaguanas_stop, 
        port_of_spain_terminal, uwi_stop
    ])
    db.session.commit()
    
    # Create route stops
    # Route 1: San Fernando to Port of Spain
    route1_stop1 = RouteStop(route1, san_fernando_terminal, 0)
    route1_stop2 = RouteStop(route1, couva_stop, 1)
    route1_stop3 = RouteStop(route1, chaguanas_stop, 2)
    route1_stop4 = RouteStop(route1, port_of_spain_terminal, 3)
    
    # Route 2: San Fernando to St. Augustine
    route2_stop1 = RouteStop(route2, san_fernando_terminal, 0)
    route2_stop2 = RouteStop(route2, couva_stop, 1)
    route2_stop3 = RouteStop(route2, chaguanas_stop, 2)
    route2_stop4 = RouteStop(route2, uwi_stop, 3)
    
    db.session.add_all([
        route1_stop1, route1_stop2, route1_stop3, route1_stop4,
        route2_stop1, route2_stop2, route2_stop3, route2_stop4
    ])
    db.session.commit()
    
    # Create users (drivers)
    driver1 = Driver("driver1", "password123", is_admin=False, full_Name="John Driver", licenseNo="DL12345")
    driver2 = Driver("driver2", "password123", is_admin=False, full_Name="Jane Driver", licenseNo="DL67890")
    
    db.session.add_all([driver1, driver2])
    db.session.commit()

    # Create buses
    bus1 = Bus("Bus 001", driver1, route1, 50)
    bus2 = Bus("Bus 002", driver2, route1, 45)
    bus3 = Bus("Bus 003", driver1, route2, 50)
    
    db.session.add_all([bus1, bus2, bus3])
    db.session.commit()
    
    # Create admin user
    admin = User("admin", "admin123")
    admin.is_admin = True
    
    db.session.add(admin)
    db.session.commit()
    
    print("Demo data created successfully!")

def init_app(app):
    """Initialize the application with required settings and data"""
    with app.app_context():
        db.create_all()
        
        # Check if we need to initialize demo data
        if User.query.count() == 0:
            create_demo_data()
            
    return True
