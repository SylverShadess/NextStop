from App.database import db
from App.models import User
from App.models.User import Driver
from App.models.Area import Area
from App.models.Route import Route
from App.models.Location import Location, LocationType
from App.models.RouteStop import RouteStop
from App.models.Bus import Bus
from App.models.Journey import Journey
from App.models.JourneyEvent import JourneyEvent
from App.models.BoardEvent import BoardEvent
from App.models.Schedule import Schedule
from datetime import datetime, timedelta
from .user import create_user

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
    bridgetown = Area("BridgeTown")
    hole_town = Area("Hole Town")
    speights_town = Area("Speights Town")
    oistins = Area("Oistins")
    db.session.add_all([san_fernando, port_of_spain, st_augustine, bridgetown, hole_town, speights_town, oistins])
    db.session.commit()
    
    # Create routes
    route1 = Route(name="POS Express", cost=10, start_area=san_fernando, end_area=port_of_spain)
    route2 = Route(name="UWI Shuttle", cost=8, start_area=san_fernando, end_area=st_augustine)
    route3 = Route(name="Barbados Coastal Line", cost=25, start_area=bridgetown, end_area=hole_town)
    route4 = Route(name="Bridgetown-Oistins Express", cost=15, start_area=bridgetown, end_area=oistins)
    db.session.add_all([route1, route2, route3, route4])
    db.session.commit()
    
    # Create locations (terminals and stops)
    san_fernando_terminal = Location("San Fernando Bus Terminal", 10.2799, -61.4702, LocationType.Terminal)
    couva_stop = Location("Couva Stop", 10.4213, -61.4111, LocationType.Stop)
    chaguanas_stop = Location("Chaguanas Stop", 10.5158, -61.4113, LocationType.Stop)
    port_of_spain_terminal = Location("Port of Spain Bus Terminal", 10.6572, -61.5180, LocationType.Terminal)
    uwi_stop = Location("U.W.I. Bus Stop", 10.6384, -61.4023, LocationType.Stop)
    oistins_terminal = Location(name="Oistins Terminal", lat=13.0678, lng=-59.5327, type=LocationType.Terminal)
    bridgetown_terminal = Location(name="Bridgetown Terminal", lat=13.1132, lng=-59.5988, type=LocationType.Terminal)
    speights_town_stop = Location(name="Speightstown Stop", lat=13.2506, lng=-59.6437, type=LocationType.Stop)
    holetown_stop = Location(name="Holetown Stop", lat=13.1867, lng=-59.6381, type=LocationType.Stop)
    bathsheba_stop = Location(name="Bathsheba Stop", lat=13.2139, lng=-59.5261, type=LocationType.Stop)
    db.session.add_all([
        san_fernando_terminal, couva_stop, chaguanas_stop, 
        port_of_spain_terminal, uwi_stop, oistins_terminal, bridgetown_terminal, speights_town_stop, holetown_stop, bathsheba_stop
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
    
    # Route 3: Bridgetown to Hole Town
    route3_stop1 = RouteStop(route3, bridgetown_terminal, 0)
    route3_stop2 = RouteStop(route3, speights_town_stop, 1)
    route3_stop3 = RouteStop(route3, holetown_stop, 2)
    
    # Route 4: Bridgetown to Oistins
    route4_stop1 = RouteStop(route4, bridgetown_terminal, 0)
    route4_stop2 = RouteStop(route4, speights_town_stop, 1)
    route4_stop3 = RouteStop(route4, oistins_terminal, 2)
    
    db.session.add_all([
        route1_stop1, route1_stop2, route1_stop3, route1_stop4,
        route2_stop1, route2_stop2, route2_stop3, route2_stop4,
        route3_stop1, route3_stop2, route3_stop3,
        route4_stop1, route4_stop2, route4_stop3
    ])
    db.session.commit()
    
    # Create users (drivers)
    driver1 = Driver("driver1", "pass123", is_admin=False, full_Name="John Driver", licenseNo="DL12345")
    driver2 = Driver("driver2", "pass123", is_admin=False, full_Name="Jane Driver", licenseNo="DL67890")
    
    db.session.add_all([driver1, driver2])
    db.session.commit()

    # Create buses
    bus1 = Bus("Bus 001", driver1, route1, 50)
    bus2 = Bus("Bus 002", driver2, route1, 45)
    bus3 = Bus("Bus 003", driver1, route2, 50)
    
    db.session.add_all([bus1, bus2, bus3])
    db.session.commit()

    now = datetime.utcnow()
    
    # Route 1 schedules - San Fernando to Port of Spain
    sched1 = Schedule(stop=san_fernando_terminal, route=route1, 
                     arrivalTime=now, 
                     departureTime=now + timedelta(minutes=5))
    
    sched2 = Schedule(stop=couva_stop, route=route1, 
                     arrivalTime=now + timedelta(minutes=15), 
                     departureTime=now + timedelta(minutes=17))
    
    sched3 = Schedule(stop=chaguanas_stop, route=route1, 
                     arrivalTime=now + timedelta(minutes=35), 
                     departureTime=now + timedelta(minutes=37))
    
    sched4 = Schedule(stop=port_of_spain_terminal, route=route1, 
                     arrivalTime=now + timedelta(minutes=55), 
                     departureTime=now + timedelta(minutes=57))
    
    # Route 2 schedules - San Fernando to UWI/St. Augustine
    sched5 = Schedule(stop=san_fernando_terminal, route=route2, 
                     arrivalTime=now + timedelta(minutes=10), 
                     departureTime=now + timedelta(minutes=15))
    
    sched6 = Schedule(stop=couva_stop, route=route2, 
                     arrivalTime=now + timedelta(minutes=35), 
                     departureTime=now + timedelta(minutes=37))
    
    sched7 = Schedule(stop=chaguanas_stop, route=route2, 
                     arrivalTime=now + timedelta(minutes=55), 
                     departureTime=now + timedelta(minutes=57))
    
    sched8 = Schedule(stop=uwi_stop, route=route2, 
                     arrivalTime=now + timedelta(minutes=75), 
                     departureTime=now + timedelta(minutes=77))
    
    db.session.add_all([sched1, sched2, sched3, sched4, sched5, sched6, sched7, sched8])
    db.session.commit()

    journey2_start = now - timedelta(minutes=50)  # Journey in progress on route 2
    journey2 = Journey(driver=driver2, route=route2, bus=bus2, startTime=journey2_start)

    db.session.add(journey2)
    db.session.commit()

    # Journey 2 events - San Fernando to UWI/St. Augustine (Eastern route)
    # Starting at San Fernando Terminal
    je1 = JourneyEvent(journey=journey2, lat=10.2836855, lng=-61.4682742)  # San Fernando Terminal
    
    # Moving north through Marabella, onto the highway
    je2 = JourneyEvent(journey=journey2, lat=10.3119, lng=-61.4564)  # Passing Marabella
    je3 = JourneyEvent(journey=journey2, lat=10.3456, lng=-61.4412)  # Approaching Gasparillo
    
    # Approaching Couva
    je4 = JourneyEvent(journey=journey2, lat=10.3921, lng=-61.4231)  # Near Preysal
    je5 = JourneyEvent(journey=journey2, lat=10.4173997, lng=-61.4177743)  # At Couva Stop
    
    # Moving toward Chaguanas
    je6 = JourneyEvent(journey=journey2, lat=10.4512, lng=-61.4138)  # Between Couva and Chaguanas
    je7 = JourneyEvent(journey=journey2, lat=10.4863, lng=-61.4102)  # Approaching Chaguanas
    je8 = JourneyEvent(journey=journey2, lat=10.5152464, lng=-61.4079954)  # At Chaguanas Stop
    
    # Moving toward UWI/St. Augustine
    je9 = JourneyEvent(journey=journey2, lat=10.5487, lng=-61.3987)  # East of Chaguanas
    je10 = JourneyEvent(journey=journey2, lat=10.5912, lng=-61.3921)  # Approaching Curepe
    je11 = JourneyEvent(journey=journey2, lat=10.6231, lng=-61.3954)  # Near St. Augustine
    
    db.session.add_all([je1, je2, je3, je4, je5, je6, je7, je8, je9, je10, je11])
    db.session.commit()

    be1 = BoardEvent(journey=journey2, event_type="Enter", qty=15, stop=route2_stop1, 
                    time=journey2_start + timedelta(minutes=5))  # 15 passengers at San Fernando
    
    be2 = BoardEvent(journey=journey2, event_type="Exit", qty=2, stop=route2_stop2, 
                    time=journey2_start + timedelta(minutes=35))  # 2 exit at Couva
    
    be3 = BoardEvent(journey=journey2, event_type="Enter", qty=4, stop=route2_stop2, 
                    time=journey2_start + timedelta(minutes=37))  # 4 enter at Couva
    
    be4 = BoardEvent(journey=journey2, event_type="Exit", qty=5, stop=route2_stop3, 
                    time=journey2_start + timedelta(minutes=55))  # 5 exit at Chaguanas
    
    be5 = BoardEvent(journey=journey2, event_type="Enter", qty=8, stop=route2_stop3, 
                    time=journey2_start + timedelta(minutes=57))  # 8 enter at Chaguanas
    
    db.session.add_all([be1, be2, be3, be4, be5])
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
