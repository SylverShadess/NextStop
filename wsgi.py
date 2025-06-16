import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from datetime import datetime, timedelta
from App.database import db, get_migrate
from App.models import User, Driver, Area, Location, LocationType, Route, RouteStop, Bus, Journey, JourneyEvent, BoardEvent, BoardType, Schedule
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
Seed Commands
'''
seed_cli = AppGroup('seed', help='Seed database commands')

@seed_cli.command("data", help="Seeds the database with sample data")
def seed_data_command():
    db.drop_all()
    db.create_all()
    
    print("Creating drivers...")
    driver1 = Driver(username="driver1", password="pass123", full_Name="Kyle Persard", licenseNo="HL12345")
    driver2 = Driver(username="BigMann528", password="pass123", full_Name="Joshua Brathwaite", licenseNo="ZR67890")
    
    db.session.add_all([driver1, driver2])
    db.session.commit()
    
    print("Creating areas...")
    pos = Area(name="Port of Spain")
    sando = Area(name="San Fernando")
    chag = Area(name="Chaguanas")
    point = Area(name="Point Fortin")
    staug = Area(name="St. Augustine")

    bridge = Area(name="BridgeTown")
    hole = Area(name="Hole Town")
    spice = Area(name="Spice Town")
    oist = Area(name="Oistins")

    
    db.session.add_all([pos, sando, chag, point, staug, bridge, hole, spice, oist])
    db.session.commit()
    
    print("Creating locations...")
    loc1 = Location(name="San Fernando Bus Terminal", lat=10.2836855, lng=-61.4682742, type=LocationType.Terminal)
    loc2 = Location(name="Couva Stop", lat=10.4173997, lng=--61.4177743, type=LocationType.Stop)
    loc3 = Location(name="Chaguanas Stop", lat=10.5152464, lng=-61.4079954, type=LocationType.Stop)
    loc4 = Location(name="Port of Spain Bus Terminal", lat=10.6481372, lng=-61.5086253, type=LocationType.Terminal)
    loc5 = Location(name="U.W.I. Bus Stop", lat=10.644798439497738, lng=-61.399914886823, type=LocationType.Stop)
    
    db.session.add_all([loc1, loc2, loc3, loc4, loc5])
    db.session.commit()
    
    print("Creating routes...")
    route1 = Route(name="POS Coach", cost=10, start_area=sando, end_area=pos)
    route2 = Route(name="UWI Shuttle", cost=8, start_area=sando, end_area=staug)
    
    db.session.add_all([route1, route2])
    db.session.commit()
    
    print("Creating route stops...")
    rs1 = RouteStop(route=route1, location=loc1, stop_index=0)
    rs2 = RouteStop(route=route1, location=loc2, stop_index=1)
    rs3 = RouteStop(route=route1, location=loc3, stop_index=2)
    rs4 = RouteStop(route=route1, location=loc4, stop_index=3)
    
    rs4 = RouteStop(route=route2, location=loc1, stop_index=0)
    rs5 = RouteStop(route=route2, location=loc2, stop_index=1)
    rs6 = RouteStop(route=route2, location=loc3, stop_index=2)
    rs7 = RouteStop(route=route2, location=loc5, stop_index=3)
    
    db.session.add_all([rs1, rs2, rs3, rs4, rs5, rs6, rs7])
    db.session.commit()
    
    print("Creating buses...")
    bus1 = Bus(plate_num="BUS001", driver=driver1, route=route1)
    bus2 = Bus(plate_num="BUS002", driver=driver2, route=route2)
    
    db.session.add_all([bus1, bus2])
    db.session.commit()
    
    print("Creating schedules...")
    now = datetime.utcnow()
    
    # Route 1 schedules - San Fernando to Port of Spain
    sched1 = Schedule(stop=loc1, route=route1, 
                     arrivalTime=now, 
                     departureTime=now + timedelta(minutes=5))
    
    sched2 = Schedule(stop=loc2, route=route1, 
                     arrivalTime=now + timedelta(minutes=25), 
                     departureTime=now + timedelta(minutes=27))
    
    sched3 = Schedule(stop=loc3, route=route1, 
                     arrivalTime=now + timedelta(minutes=45), 
                     departureTime=now + timedelta(minutes=47))
    
    sched4 = Schedule(stop=loc4, route=route1, 
                     arrivalTime=now + timedelta(minutes=75), 
                     departureTime=now + timedelta(minutes=85))
    
    # Route 2 schedules - San Fernando to UWI/St. Augustine
    sched5 = Schedule(stop=loc1, route=route2, 
                     arrivalTime=now + timedelta(minutes=10), 
                     departureTime=now + timedelta(minutes=15))
    
    sched6 = Schedule(stop=loc2, route=route2, 
                     arrivalTime=now + timedelta(minutes=35), 
                     departureTime=now + timedelta(minutes=37))
    
    sched7 = Schedule(stop=loc3, route=route2, 
                     arrivalTime=now + timedelta(minutes=55), 
                     departureTime=now + timedelta(minutes=57))
    
    sched8 = Schedule(stop=loc5, route=route2, 
                     arrivalTime=now + timedelta(minutes=85), 
                     departureTime=now + timedelta(minutes=90))
    
    db.session.add_all([sched1, sched2, sched3, sched4, sched5, sched6, sched7, sched8])
    db.session.commit()
    
    print("Creating journeys...")
    journey1_start = now - timedelta(minutes=40)  # Journey in progress on route 1
    journey1 = Journey(driver=driver1, route=route1, bus=bus1, startTime=journey1_start)
    
    journey2_start = now - timedelta(minutes=50)  # Journey in progress on route 2
    journey2 = Journey(driver=driver2, route=route2, bus=bus2, startTime=journey2_start)
    
    db.session.add_all([journey1, journey2])
    db.session.commit()
    
    print("Creating journey events...")
    
    # Journey 1 events - San Fernando to Port of Spain (Southern Main Road/Uriah Butler Highway)
    # Starting at San Fernando Terminal
    je1 = JourneyEvent(journey=journey1, lat=10.2836855, lng=-61.4682742)  # San Fernando Terminal
    
    # Moving north through Marabella, onto the highway
    je2 = JourneyEvent(journey=journey1, lat=10.3119, lng=-61.4564)  # Passing Marabella
    je3 = JourneyEvent(journey=journey1, lat=10.3456, lng=-61.4412)  # Approaching Gasparillo
    
    # Approaching Couva
    je4 = JourneyEvent(journey=journey1, lat=10.3921, lng=-61.4231)  # Near Preysal
    je5 = JourneyEvent(journey=journey1, lat=10.4173997, lng=-61.4177743)  # At Couva Stop
    
    # Moving toward Chaguanas
    je6 = JourneyEvent(journey=journey1, lat=10.4512, lng=-61.4138)  # Between Couva and Chaguanas
    je7 = JourneyEvent(journey=journey1, lat=10.4863, lng=-61.4102)  # Approaching Chaguanas
    je8 = JourneyEvent(journey=journey1, lat=10.5152464, lng=-61.4079954)  # At Chaguanas Stop
    
    # Currently between Chaguanas and Port of Spain
    je9 = JourneyEvent(journey=journey1, lat=10.5487, lng=-61.4231)  # North of Chaguanas
    je10 = JourneyEvent(journey=journey1, lat=10.5812, lng=-61.4453)  # Approaching Curepe
    
    # Journey 2 events - San Fernando to UWI/St. Augustine (Eastern route)
    # Starting at San Fernando Terminal
    je11 = JourneyEvent(journey=journey2, lat=10.2836855, lng=-61.4682742)  # San Fernando Terminal
    
    # Moving north through Marabella, onto the highway
    je12 = JourneyEvent(journey=journey2, lat=10.3119, lng=-61.4564)  # Passing Marabella
    je13 = JourneyEvent(journey=journey2, lat=10.3456, lng=-61.4412)  # Approaching Gasparillo
    
    # Approaching Couva
    je14 = JourneyEvent(journey=journey2, lat=10.3921, lng=-61.4231)  # Near Preysal
    je15 = JourneyEvent(journey=journey2, lat=10.4173997, lng=-61.4177743)  # At Couva Stop
    
    # Moving toward Chaguanas
    je16 = JourneyEvent(journey=journey2, lat=10.4512, lng=-61.4138)  # Between Couva and Chaguanas
    je17 = JourneyEvent(journey=journey2, lat=10.4863, lng=-61.4102)  # Approaching Chaguanas
    je18 = JourneyEvent(journey=journey2, lat=10.5152464, lng=-61.4079954)  # At Chaguanas Stop
    
    # Moving toward UWI/St. Augustine
    je19 = JourneyEvent(journey=journey2, lat=10.5487, lng=-61.3987)  # East of Chaguanas
    je20 = JourneyEvent(journey=journey2, lat=10.5912, lng=-61.3921)  # Approaching Curepe
    je21 = JourneyEvent(journey=journey2, lat=10.6231, lng=-61.3954)  # Near St. Augustine
    # je22 = JourneyEvent(journey=journey2, lat=10.644798439497738, lng=-61.399914886823)  # At UWI Bus Stop
    
    db.session.add_all([je1, je2, je3, je4, je5, je6, je7, je8, je9, je10, je11, je12, je13, je14, je15, je16, je17, je18, je19, je20, je21])
    db.session.commit()
    
    print("Creating board events...")
    # Create board events
    # Journey 1 board events - San Fernando to Port of Spain
    be1 = BoardEvent(journey=journey1, event_type=BoardType.Enter, qty=12, stop=rs1, 
                    time=journey1_start + timedelta(minutes=5))  # 12 passengers at San Fernando
    
    be2 = BoardEvent(journey=journey1, event_type=BoardType.Exit, qty=3, stop=rs2, 
                    time=journey1_start + timedelta(minutes=25))  # 3 exit at Couva
    
    be3 = BoardEvent(journey=journey1, event_type=BoardType.Enter, qty=5, stop=rs2, 
                    time=journey1_start + timedelta(minutes=27))  # 5 enter at Couva
    
    be4 = BoardEvent(journey=journey1, event_type=BoardType.Exit, qty=4, stop=rs3, 
                    time=journey1_start + timedelta(minutes=45))  # 4 exit at Chaguanas
    
    be5 = BoardEvent(journey=journey1, event_type=BoardType.Enter, qty=7, stop=rs3, 
                    time=journey1_start + timedelta(minutes=47))  # 7 enter at Chaguanas
    
    # Journey 2 board events - San Fernando to UWI/St. Augustine
    be6 = BoardEvent(journey=journey2, event_type=BoardType.Enter, qty=15, stop=rs4, 
                    time=journey2_start + timedelta(minutes=5))  # 15 passengers at San Fernando
    
    be7 = BoardEvent(journey=journey2, event_type=BoardType.Exit, qty=2, stop=rs5, 
                    time=journey2_start + timedelta(minutes=35))  # 2 exit at Couva
    
    be8 = BoardEvent(journey=journey2, event_type=BoardType.Enter, qty=4, stop=rs5, 
                    time=journey2_start + timedelta(minutes=37))  # 4 enter at Couva
    
    be9 = BoardEvent(journey=journey2, event_type=BoardType.Exit, qty=5, stop=rs6, 
                    time=journey2_start + timedelta(minutes=55))  # 5 exit at Chaguanas
    
    be10 = BoardEvent(journey=journey2, event_type=BoardType.Enter, qty=8, stop=rs6, 
                    time=journey2_start + timedelta(minutes=57))  # 8 enter at Chaguanas
    
    db.session.add_all([be1, be2, be3, be4, be5, be6, be7, be8, be9, be10])
    db.session.commit()
    
    print("Database seeded successfully!")
    
    stats = journey1.getStats()
    print("\nJourney 1 Stats (San Fernando to Port of Spain):")
    print(f"Total passengers: {stats['total_passengers']}")
    print(f"Revenue: ${stats['revenue']}")
    print(f"Duration: {stats['duration']}")
    
    stats2 = journey2.getStats()
    print("\nJourney 2 Stats (San Fernando to UWI/St. Augustine):")
    print(f"Total passengers: {stats2['total_passengers']}")
    print(f"Revenue: ${stats2['revenue']}")
    print(f"Duration: {stats2['duration']}")
    
    # buses = loc5.getBuses(route2.id)
    # print(buses)

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)

# Add the seed command group to the app
app.cli.add_command(seed_cli)