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
    driver3 = Driver(username="SandoDriver", password="pass123", full_Name="Marcus Thompson", licenseNo="MT54321")
    driver4 = Driver(username="SpeedyDriv", password="pass123", full_Name="Rachel Gomez", licenseNo="RG98765")
    driver5 = Driver(username="BajanDriver", password="pass123", full_Name="Dexter Hollingsworth", licenseNo="DH11223")
    driver6 = Driver(username="ChagDriver", password="pass123", full_Name="Anita Rodriguez", licenseNo="AR44556")
    driver7 = Driver(username="EastDriver", password="pass123", full_Name="Samuel Williams", licenseNo="SW78901")
    driver8 = Driver(username="WestDriver", password="pass123", full_Name="Maria Garcia", licenseNo="MG23456")
    driver9 = Driver(username="NorthDriver", password="pass123", full_Name="David Johnson", licenseNo="DJ34567")
    driver10 = Driver(username="SouthDriver", password="pass123", full_Name="Lisa Brown", licenseNo="LB45678")
    
    db.session.add_all([driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10])
    db.session.commit()
    
    print("Creating areas...")
    pos = Area(name="Port of Spain")
    sando = Area(name="San Fernando")
    chag = Area(name="Chaguanas")
    point = Area(name="Point Fortin")
    staug = Area(name="St. Augustine")
    arima = Area(name="Arima")
    sangre = Area(name="Sangre Grande")
    mayaro = Area(name="Mayaro")
    siparia = Area(name="Siparia")
    penal = Area(name="Penal")
    diego = Area(name="Diego Martin")
    tunapuna = Area(name="Tunapuna")
    curepe = Area(name="Curepe")
    laventille = Area(name="Laventille")

    bridge = Area(name="BridgeTown")
    hole = Area(name="Hole Town")
    spice = Area(name="Spice Town")
    oist = Area(name="Oistins")

    
    db.session.add_all([pos, sando, chag, point, staug, arima, sangre, mayaro, siparia, penal, diego, tunapuna, curepe, laventille, bridge, hole, spice, oist])
    db.session.commit()
    
    print("Creating locations...")
    # Trinidad Terminals
    loc1 = Location(name="San Fernando Bus Terminal", lat=10.2836855, lng=-61.4682742, type=LocationType.Terminal)
    loc4 = Location(name="Port of Spain Bus Terminal", lat=10.6481372, lng=-61.5086253, type=LocationType.Terminal)
    loc6 = Location(name="Arima Bus Terminal", lat=10.6372, lng=-61.2829, type=LocationType.Terminal)
    loc7 = Location(name="Sangre Grande Terminal", lat=10.5884, lng=-61.1291, type=LocationType.Terminal)
    loc9 = Location(name="Point Fortin Terminal", lat=10.1733, lng=-61.6846, type=LocationType.Terminal)
    loc13 = Location(name="Mayaro Terminal", lat=10.2906, lng=-61.0019, type=LocationType.Terminal)
    loc14 = Location(name="Siparia Terminal", lat=10.1453, lng=-61.5078, type=LocationType.Terminal)
    loc15 = Location(name="Penal Terminal", lat=10.1694, lng=-61.4500, type=LocationType.Terminal)
    loc16 = Location(name="Diego Martin Terminal", lat=10.7239, lng=-61.5606, type=LocationType.Terminal)
    
    # Trinidad Stops
    loc2 = Location(name="Couva Stop", lat=10.4173997, lng=-61.4177743, type=LocationType.Stop)
    loc3 = Location(name="Chaguanas Stop", lat=10.5152464, lng=-61.4079954, type=LocationType.Stop)
    loc5 = Location(name="U.W.I. Bus Stop", lat=10.644798439497738, lng=-61.399914886823, type=LocationType.Stop)
    loc8 = Location(name="Fyzabad Stop", lat=10.1730, lng=-61.5484, type=LocationType.Stop)
    loc17 = Location(name="Tunapuna Stop", lat=10.6525, lng=-61.3880, type=LocationType.Stop)
    loc18 = Location(name="Curepe Junction", lat=10.6399, lng=-61.4105, type=LocationType.Stop)
    loc19 = Location(name="Laventille Road Stop", lat=10.6511, lng=-61.4994, type=LocationType.Stop)
    loc20 = Location(name="Marabella Stop", lat=10.3119, lng=-61.4564, type=LocationType.Stop)
    loc21 = Location(name="Gasparillo Junction", lat=10.3456, lng=-61.4412, type=LocationType.Stop)
    loc22 = Location(name="Princes Town Stop", lat=10.2711, lng=-61.3778, type=LocationType.Stop)
    loc23 = Location(name="Rio Claro Stop", lat=10.3061, lng=-61.1758, type=LocationType.Stop)
    loc24 = Location(name="Barrackpore Stop", lat=10.2111, lng=-61.4331, type=LocationType.Stop)
    loc25 = Location(name="La Brea Stop", lat=10.2500, lng=-61.6167, type=LocationType.Stop)
    loc26 = Location(name="St. Joseph Stop", lat=10.6633, lng=-61.4233, type=LocationType.Stop)
    
    # Barbados Locations
    loc10 = Location(name="Oistins Terminal", lat=13.0678, lng=-59.5327, type=LocationType.Terminal)
    loc11 = Location(name="Bridgetown Terminal", lat=13.1132, lng=-59.5988, type=LocationType.Terminal)
    loc12 = Location(name="Speightstown Stop", lat=13.2506, lng=-59.6437, type=LocationType.Stop)
    loc27 = Location(name="Holetown Stop", lat=13.1867, lng=-59.6381, type=LocationType.Stop)
    loc28 = Location(name="Bathsheba Stop", lat=13.2139, lng=-59.5261, type=LocationType.Stop)
    
    db.session.add_all([
        loc1, loc2, loc3, loc4, loc5, loc6, loc7, loc8, loc9, loc10, 
        loc11, loc12, loc13, loc14, loc15, loc16, loc17, loc18, loc19, loc20, 
        loc21, loc22, loc23, loc24, loc25, loc26, loc27, loc28
    ])
    db.session.commit()
    
    print("Creating routes...")
    # Trinidad Routes
    route1 = Route(name="POS Express", cost=10, start_area=sando, end_area=pos)
    route2 = Route(name="UWI Shuttle", cost=8, start_area=sando, end_area=staug)
    route3 = Route(name="Eastern Main Road", cost=12, start_area=pos, end_area=arima)
    route4 = Route(name="South Coast Line", cost=15, start_area=point, end_area=sando)
    route6 = Route(name="Central Line", cost=18, start_area=pos, end_area=chag)
    route7 = Route(name="North Coast Express", cost=20, start_area=pos, end_area=diego)
    route8 = Route(name="East-West Corridor", cost=15, start_area=arima, end_area=diego)
    route9 = Route(name="Deep South Express", cost=25, start_area=sando, end_area=siparia)
    route10 = Route(name="Sangre Grande Link", cost=22, start_area=arima, end_area=sangre)
    route11 = Route(name="Mayaro Coastal", cost=30, start_area=sangre, end_area=mayaro)
    route12 = Route(name="South Eastern Line", cost=28, start_area=sando, end_area=mayaro)
    route13 = Route(name="Penal Connector", cost=12, start_area=siparia, end_area=penal)
    
    # Barbados Routes
    route5 = Route(name="Barbados Coastal Line", cost=25, start_area=bridge, end_area=hole)
    route14 = Route(name="Bridgetown-Oistins Express", cost=15, start_area=bridge, end_area=oist)
    route15 = Route(name="Island Circle Route", cost=30, start_area=bridge, end_area=bridge)
    
    db.session.add_all([
        route1, route2, route3, route4, route5, route6, route7, route8, 
        route9, route10, route11, route12, route13, route14, route15
    ])
    db.session.commit()
    
    print("Creating route stops...")
    # Route 1: San Fernando to Port of Spain Express
    rs1 = RouteStop(route=route1, location=loc1, stop_index=0)   # San Fernando Terminal
    rs2 = RouteStop(route=route1, location=loc20, stop_index=1)  # Marabella Stop
    rs3 = RouteStop(route=route1, location=loc2, stop_index=2)   # Couva Stop
    rs4 = RouteStop(route=route1, location=loc3, stop_index=3)   # Chaguanas Stop
    rs5 = RouteStop(route=route1, location=loc4, stop_index=4)   # Port of Spain Terminal
    
    # Route 2: San Fernando to UWI/St. Augustine
    rs6 = RouteStop(route=route2, location=loc1, stop_index=0)   # San Fernando Terminal
    rs7 = RouteStop(route=route2, location=loc2, stop_index=1)   # Couva Stop
    rs8 = RouteStop(route=route2, location=loc3, stop_index=2)   # Chaguanas Stop
    rs9 = RouteStop(route=route2, location=loc18, stop_index=3)  # Curepe Junction
    rs10 = RouteStop(route=route2, location=loc5, stop_index=4)  # UWI Bus Stop
    
    # Route 3: Port of Spain to Arima (Eastern Main Road)
    rs11 = RouteStop(route=route3, location=loc4, stop_index=0)  # Port of Spain Terminal
    rs12 = RouteStop(route=route3, location=loc19, stop_index=1) # Laventille Road Stop
    rs13 = RouteStop(route=route3, location=loc26, stop_index=2) # St. Joseph Stop
    rs14 = RouteStop(route=route3, location=loc17, stop_index=3) # Tunapuna Stop
    rs15 = RouteStop(route=route3, location=loc6, stop_index=4)  # Arima Bus Terminal
    
    # Route 4: Point Fortin to San Fernando (South Coast)
    rs16 = RouteStop(route=route4, location=loc9, stop_index=0)  # Point Fortin Terminal
    rs17 = RouteStop(route=route4, location=loc25, stop_index=1) # La Brea Stop
    rs18 = RouteStop(route=route4, location=loc8, stop_index=2)  # Fyzabad Stop
    rs19 = RouteStop(route=route4, location=loc1, stop_index=3)  # San Fernando Terminal
    
    # Route 5: Bridgetown to Hole Town (Barbados Coastal)
    rs20 = RouteStop(route=route5, location=loc11, stop_index=0) # Bridgetown Terminal
    rs21 = RouteStop(route=route5, location=loc27, stop_index=1) # Holetown Stop
    rs22 = RouteStop(route=route5, location=loc12, stop_index=2) # Speightstown Stop
    
    # Route 6: Port of Spain to Chaguanas (Central Line)
    rs23 = RouteStop(route=route6, location=loc4, stop_index=0)  # Port of Spain Terminal
    rs24 = RouteStop(route=route6, location=loc18, stop_index=1) # Curepe Junction
    rs25 = RouteStop(route=route6, location=loc3, stop_index=2)  # Chaguanas Stop
    
    # Route 7: Port of Spain to Diego Martin (North Coast)
    rs26 = RouteStop(route=route7, location=loc4, stop_index=0)  # Port of Spain Terminal
    rs27 = RouteStop(route=route7, location=loc16, stop_index=1) # Diego Martin Terminal
    
    # Route 8: Arima to Diego Martin (East-West Corridor)
    rs28 = RouteStop(route=route8, location=loc6, stop_index=0)  # Arima Bus Terminal
    rs29 = RouteStop(route=route8, location=loc17, stop_index=1) # Tunapuna Stop
    rs30 = RouteStop(route=route8, location=loc18, stop_index=2) # Curepe Junction
    rs31 = RouteStop(route=route8, location=loc4, stop_index=3)  # Port of Spain Terminal
    rs32 = RouteStop(route=route8, location=loc16, stop_index=4) # Diego Martin Terminal
    
    # Route 9: San Fernando to Siparia (Deep South)
    rs33 = RouteStop(route=route9, location=loc1, stop_index=0)  # San Fernando Terminal
    rs34 = RouteStop(route=route9, location=loc24, stop_index=1) # Barrackpore Stop
    rs35 = RouteStop(route=route9, location=loc15, stop_index=2) # Penal Terminal
    rs36 = RouteStop(route=route9, location=loc14, stop_index=3) # Siparia Terminal
    
    # Route 10: Arima to Sangre Grande
    rs37 = RouteStop(route=route10, location=loc6, stop_index=0) # Arima Bus Terminal
    rs38 = RouteStop(route=route10, location=loc7, stop_index=1) # Sangre Grande Terminal
    
    # Route 11: Sangre Grande to Mayaro (Coastal)
    rs39 = RouteStop(route=route11, location=loc7, stop_index=0) # Sangre Grande Terminal
    rs40 = RouteStop(route=route11, location=loc23, stop_index=1) # Rio Claro Stop
    rs41 = RouteStop(route=route11, location=loc13, stop_index=2) # Mayaro Terminal
    
    # Route 12: San Fernando to Mayaro (South Eastern)
    rs42 = RouteStop(route=route12, location=loc1, stop_index=0) # San Fernando Terminal
    rs43 = RouteStop(route=route12, location=loc22, stop_index=1) # Princes Town Stop
    rs44 = RouteStop(route=route12, location=loc23, stop_index=2) # Rio Claro Stop
    rs45 = RouteStop(route=route12, location=loc13, stop_index=3) # Mayaro Terminal
    
    # Route 13: Siparia to Penal Connector
    rs46 = RouteStop(route=route13, location=loc14, stop_index=0) # Siparia Terminal
    rs47 = RouteStop(route=route13, location=loc15, stop_index=1) # Penal Terminal
    
    # Route 14: Bridgetown to Oistins (Barbados Express)
    rs48 = RouteStop(route=route14, location=loc11, stop_index=0) # Bridgetown Terminal
    rs49 = RouteStop(route=route14, location=loc10, stop_index=1) # Oistins Terminal
    
    # Route 15: Barbados Island Circle
    rs50 = RouteStop(route=route15, location=loc11, stop_index=0) # Bridgetown Terminal
    rs51 = RouteStop(route=route15, location=loc27, stop_index=1) # Holetown Stop
    rs52 = RouteStop(route=route15, location=loc12, stop_index=2) # Speightstown Stop
    rs53 = RouteStop(route=route15, location=loc28, stop_index=3) # Bathsheba Stop
    rs54 = RouteStop(route=route15, location=loc10, stop_index=4) # Oistins Terminal
    rs55 = RouteStop(route=route15, location=loc11, stop_index=5) # Back to Bridgetown
    
    db.session.add_all([
        rs1, rs2, rs3, rs4, rs5, rs6, rs7, rs8, rs9, rs10,
        rs11, rs12, rs13, rs14, rs15, rs16, rs17, rs18, rs19, rs20,
        rs21, rs22, rs23, rs24, rs25, rs26, rs27, rs28, rs29, rs30,
        rs31, rs32, rs33, rs34, rs35, rs36, rs37, rs38, rs39, rs40,
        rs41, rs42, rs43, rs44, rs45, rs46, rs47, rs48, rs49, rs50,
        rs51, rs52, rs53, rs54, rs55
    ])
    db.session.commit()
    
    print("Creating buses...")
    bus1 = Bus(plate_num="BUS001", driver=driver1, route=route1)
    bus2 = Bus(plate_num="BUS002", driver=driver2, route=route2)
    bus3 = Bus(plate_num="BUS003", driver=driver3, route=route3)
    bus4 = Bus(plate_num="BUS004", driver=driver4, route=route4)
    bus5 = Bus(plate_num="BBD001", driver=driver5, route=route5)
    bus6 = Bus(plate_num="BUS006", driver=driver6, route=route6)
    bus7 = Bus(plate_num="BUS007", driver=driver1, route=route1) 
    bus8 = Bus(plate_num="BUS008", driver=driver2, route=route2)  
    bus9 = Bus(plate_num="BUS009", driver=driver7, route=route7)
    bus10 = Bus(plate_num="BUS010", driver=driver8, route=route8)
    bus11 = Bus(plate_num="BUS011", driver=driver9, route=route9)
    bus12 = Bus(plate_num="BUS012", driver=driver10, route=route10)
    bus13 = Bus(plate_num="BUS013", driver=driver3, route=route11)
    bus14 = Bus(plate_num="BUS014", driver=driver4, route=route12)
    bus15 = Bus(plate_num="BUS015", driver=driver5, route=route13)
    bus16 = Bus(plate_num="BBD002", driver=driver6, route=route14)
    bus17 = Bus(plate_num="BBD003", driver=driver7, route=route15)
    
    db.session.add_all([
        bus1, bus2, bus3, bus4, bus5, bus6, bus7, bus8, bus9, bus10,
        bus11, bus12, bus13, bus14, bus15, bus16, bus17
    ])
    db.session.commit()
    
    print("Creating schedules...")
    now = datetime.utcnow()
    
    # Route 1 schedules - San Fernando to Port of Spain
    sched1 = Schedule(stop=loc1, route=route1, 
                     arrivalTime=now, 
                     departureTime=now + timedelta(minutes=5))
    
    sched2 = Schedule(stop=loc20, route=route1, 
                     arrivalTime=now + timedelta(minutes=15), 
                     departureTime=now + timedelta(minutes=17))
    
    sched3 = Schedule(stop=loc2, route=route1, 
                     arrivalTime=now + timedelta(minutes=35), 
                     departureTime=now + timedelta(minutes=37))
    
    sched4 = Schedule(stop=loc3, route=route1, 
                     arrivalTime=now + timedelta(minutes=55), 
                     departureTime=now + timedelta(minutes=57))
    
    sched5 = Schedule(stop=loc4, route=route1, 
                     arrivalTime=now + timedelta(minutes=85), 
                     departureTime=now + timedelta(minutes=95))
    
    # Route 2 schedules - San Fernando to UWI/St. Augustine
    sched6 = Schedule(stop=loc1, route=route2, 
                     arrivalTime=now + timedelta(minutes=10), 
                     departureTime=now + timedelta(minutes=15))
    
    sched7 = Schedule(stop=loc2, route=route2, 
                     arrivalTime=now + timedelta(minutes=35), 
                     departureTime=now + timedelta(minutes=37))
    
    sched8 = Schedule(stop=loc3, route=route2, 
                     arrivalTime=now + timedelta(minutes=55), 
                     departureTime=now + timedelta(minutes=57))
    
    sched9 = Schedule(stop=loc18, route=route2, 
                     arrivalTime=now + timedelta(minutes=75), 
                     departureTime=now + timedelta(minutes=77))
    
    sched10 = Schedule(stop=loc5, route=route2, 
                     arrivalTime=now + timedelta(minutes=85), 
                     departureTime=now + timedelta(minutes=90))
    
    # Route 3 schedules - Port of Spain to Arima
    sched11 = Schedule(stop=loc4, route=route3, 
                     arrivalTime=now + timedelta(minutes=5), 
                     departureTime=now + timedelta(minutes=10))
    
    sched12 = Schedule(stop=loc19, route=route3, 
                     arrivalTime=now + timedelta(minutes=20), 
                     departureTime=now + timedelta(minutes=22))
    
    sched13 = Schedule(stop=loc26, route=route3, 
                     arrivalTime=now + timedelta(minutes=35), 
                     departureTime=now + timedelta(minutes=37))
    
    sched14 = Schedule(stop=loc17, route=route3, 
                     arrivalTime=now + timedelta(minutes=50), 
                     departureTime=now + timedelta(minutes=52))
    
    sched15 = Schedule(stop=loc6, route=route3, 
                     arrivalTime=now + timedelta(minutes=70), 
                     departureTime=now + timedelta(minutes=75))
    
    db.session.add_all([
        sched1, sched2, sched3, sched4, sched5, sched6, sched7, sched8, sched9, sched10,
        sched11, sched12, sched13, sched14, sched15
    ])
    db.session.commit()
    
    print("Creating journeys...")
    journey1_start = now - timedelta(minutes=40)  # Journey in progress on route 1
    journey1 = Journey(driver=driver1, route=route1, bus=bus1, startTime=journey1_start)
    
    journey2_start = now - timedelta(minutes=50)  # Journey in progress on route 2
    journey2 = Journey(driver=driver2, route=route2, bus=bus2, startTime=journey2_start)
    
    journey3_start = now - timedelta(minutes=30)  # Journey in progress on route 3
    journey3 = Journey(driver=driver3, route=route3, bus=bus3, startTime=journey3_start)
    
    journey4_start = now - timedelta(minutes=45)  # Journey in progress on route 4
    journey4 = Journey(driver=driver4, route=route4, bus=bus4, startTime=journey4_start)
    
    journey5_start = now - timedelta(minutes=55)  # Journey in progress on route 5
    journey5 = Journey(driver=driver5, route=route5, bus=bus5, startTime=journey5_start)
    
    journey6_start = now - timedelta(minutes=25)  # Journey in progress on route 6
    journey6 = Journey(driver=driver6, route=route6, bus=bus6, startTime=journey6_start)
    
    journey7_start = now - timedelta(minutes=20)  # Another journey on route 1 (second bus)
    journey7 = Journey(driver=driver1, route=route1, bus=bus7, startTime=journey7_start)
    
    journey8_start = now - timedelta(minutes=35)  # Another journey on route 2 (second bus)
    journey8 = Journey(driver=driver2, route=route2, bus=bus8, startTime=journey8_start)
    
    journey9_start = now - timedelta(minutes=15)  # Journey on route 7
    journey9 = Journey(driver=driver7, route=route7, bus=bus9, startTime=journey9_start)
    
    journey10_start = now - timedelta(minutes=25)  # Journey on route 8
    journey10 = Journey(driver=driver8, route=route8, bus=bus10, startTime=journey10_start)
    
    journey11_start = now - timedelta(minutes=30)  # Journey on route 9
    journey11 = Journey(driver=driver9, route=route9, bus=bus11, startTime=journey11_start)
    
    journey12_start = now - timedelta(minutes=40)  # Journey on route 10
    journey12 = Journey(driver=driver10, route=route10, bus=bus12, startTime=journey12_start)
    
    # Completed journeys (for history)
    past_journey1_start = now - timedelta(hours=5)
    past_journey1 = Journey(driver=driver1, route=route1, bus=bus1, 
                        startTime=past_journey1_start, 
                        endTime=past_journey1_start + timedelta(hours=2),
                        status="Completed")
    
    past_journey2_start = now - timedelta(hours=8)
    past_journey2 = Journey(driver=driver2, route=route2, bus=bus2, 
                        startTime=past_journey2_start, 
                        endTime=past_journey2_start + timedelta(hours=2, minutes=30),
                        status="Completed")
    
    past_journey3_start = now - timedelta(hours=6)
    past_journey3 = Journey(driver=driver3, route=route3, bus=bus3, 
                        startTime=past_journey3_start, 
                        endTime=past_journey3_start + timedelta(hours=1, minutes=45),
                        status="Completed")
    
    past_journey4_start = now - timedelta(hours=10)
    past_journey4 = Journey(driver=driver4, route=route4, bus=bus4, 
                        startTime=past_journey4_start, 
                        endTime=past_journey4_start + timedelta(hours=1, minutes=30),
                        status="Completed")
    
    db.session.add_all([
        journey1, journey2, journey3, journey4, journey5, journey6, journey7, journey8, 
        journey9, journey10, journey11, journey12,
        past_journey1, past_journey2, past_journey3, past_journey4
    ])
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
    je22 = JourneyEvent(journey=journey2, lat=10.644798439497738, lng=-61.399914886823)  # At UWI Bus Stop
    
    # Journey 3 events - Port of Spain to Arima and St. Augustine
    je23 = JourneyEvent(journey=journey3, lat=10.6481372, lng=-61.5086253)  # Port of Spain Terminal
    je24 = JourneyEvent(journey=journey3, lat=10.6423, lng=-61.4789)  # Moving east from POS
    je25 = JourneyEvent(journey=journey3, lat=10.6398, lng=-61.4421)  # Approaching Arima
    je26 = JourneyEvent(journey=journey3, lat=10.6372, lng=-61.2829)  # Arima Bus Terminal
    je27 = JourneyEvent(journey=journey3, lat=10.6401, lng=-61.3512)  # Between Arima and UWI
    # Current position is between Arima and UWI - good for getBuses test
    
    # Journey 4 events - Point Fortin to San Fernando
    je28 = JourneyEvent(journey=journey4, lat=10.1733, lng=-61.6846)  # Point Fortin Terminal
    je29 = JourneyEvent(journey=journey4, lat=10.1731, lng=-61.6532)  # Leaving Point Fortin
    je30 = JourneyEvent(journey=journey4, lat=10.1730, lng=-61.5484)  # Fyzabad Stop
    je31 = JourneyEvent(journey=journey4, lat=10.2156, lng=-61.5231)  # Between Fyzabad and San Fernando
    # Current position is between Fyzabad and San Fernando - good for getBuses test
    
    # Journey 5 events - Bridgetown to Hole Town (Barbados)
    je32 = JourneyEvent(journey=journey5, lat=13.1132, lng=-59.5988)  # Bridgetown Terminal
    je33 = JourneyEvent(journey=journey5, lat=13.1489, lng=-59.6211)  # Moving north from Bridgetown
    je34 = JourneyEvent(journey=journey5, lat=13.1837, lng=-59.6358)  # Halfway to Speightstown
    je35 = JourneyEvent(journey=journey5, lat=13.2154, lng=-59.6402)  # Approaching Speightstown
    # Current position is approaching Speightstown - good for getBuses test
    
    # Journey 6 events - Port of Spain to Chaguanas
    je36 = JourneyEvent(journey=journey6, lat=10.6481372, lng=-61.5086253)  # Port of Spain Terminal
    je37 = JourneyEvent(journey=journey6, lat=10.6123, lng=-61.4892)  # Leaving Port of Spain
    je38 = JourneyEvent(journey=journey6, lat=10.5864, lng=-61.4678)  # On the highway
    je39 = JourneyEvent(journey=journey6, lat=10.5512, lng=-61.4321)  # Approaching Chaguanas
    # Current position is approaching Chaguanas - good for getBuses test
    
    # Journey 7 events - San Fernando to Port of Spain (second bus)
    je40 = JourneyEvent(journey=journey7, lat=10.2836855, lng=-61.4682742)  # San Fernando Terminal
    je41 = JourneyEvent(journey=journey7, lat=10.3119, lng=-61.4564)  # Passing Marabella
    je42 = JourneyEvent(journey=journey7, lat=10.3456, lng=-61.4412)  # Approaching Couva
    # Current position is approaching Couva - good for getBuses test
    
    # Journey 8 events - San Fernando to UWI/St. Augustine (second bus)
    je43 = JourneyEvent(journey=journey8, lat=10.2836855, lng=-61.4682742)  # San Fernando Terminal
    je44 = JourneyEvent(journey=journey8, lat=10.3119, lng=-61.4564)  # Passing Marabella
    je45 = JourneyEvent(journey=journey8, lat=10.3456, lng=-61.4412)  # Approaching Couva
    je46 = JourneyEvent(journey=journey8, lat=10.3921, lng=-61.4231)  # Near Preysal
    # Current position is near Preysal - good for getBuses test
    
    # Journey 9 events - Port of Spain to Diego Martin
    je47 = JourneyEvent(journey=journey9, lat=10.6481372, lng=-61.5086253)  # Port of Spain Terminal
    je48 = JourneyEvent(journey=journey9, lat=10.6723, lng=-61.5312)  # Moving west from POS
    je49 = JourneyEvent(journey=journey9, lat=10.6891, lng=-61.5489)  # Approaching Diego Martin
    # Current position is approaching Diego Martin
    
    # Journey 10 events - Arima to Diego Martin
    je50 = JourneyEvent(journey=journey10, lat=10.6372, lng=-61.2829)  # Arima Bus Terminal
    je51 = JourneyEvent(journey=journey10, lat=10.6525, lng=-61.3880)  # Tunapuna Stop
    je52 = JourneyEvent(journey=journey10, lat=10.6399, lng=-61.4105)  # Curepe Junction
    # Current position is at Curepe Junction
    
    # Journey 11 events - San Fernando to Siparia
    je53 = JourneyEvent(journey=journey11, lat=10.2836855, lng=-61.4682742)  # San Fernando Terminal
    je54 = JourneyEvent(journey=journey11, lat=10.2111, lng=-61.4331)  # Barrackpore Stop
    # Current position is at Barrackpore Stop
    
    # Journey 12 events - Arima to Sangre Grande
    je55 = JourneyEvent(journey=journey12, lat=10.6372, lng=-61.2829)  # Arima Bus Terminal
    je56 = JourneyEvent(journey=journey12, lat=10.6128, lng=-61.2060)  # Moving east from Arima
    # Current position is moving east from Arima
    
    db.session.add_all([
        je1, je2, je3, je4, je5, je6, je7, je8, je9, je10, 
        je11, je12, je13, je14, je15, je16, je17, je18, je19, je20, 
        je21, je22, je23, je24, je25, je26, je27, je28, je29, je30, 
        je31, je32, je33, je34, je35, je36, je37, je38, je39, je40,
        je41, je42, je43, je44, je45, je46, je47, je48, je49, je50,
        je51, je52, je53, je54, je55, je56
    ])
    db.session.commit()
    
    print("Creating board events...")
    # Create board events
    # Journey 1 board events - San Fernando to Port of Spain
    be1 = BoardEvent(journey=journey1, event_type=BoardType.Enter, qty=12, stop=rs1, 
                    time=journey1_start + timedelta(minutes=5))  # 12 passengers at San Fernando
    
    be2 = BoardEvent(journey=journey1, event_type=BoardType.Exit, qty=3, stop=rs2, 
                    time=journey1_start + timedelta(minutes=25))  # 3 exit at Marabella
    
    be3 = BoardEvent(journey=journey1, event_type=BoardType.Enter, qty=5, stop=rs2, 
                    time=journey1_start + timedelta(minutes=27))  # 5 enter at Marabella
    
    be4 = BoardEvent(journey=journey1, event_type=BoardType.Exit, qty=4, stop=rs3, 
                    time=journey1_start + timedelta(minutes=45))  # 4 exit at Couva
    
    be5 = BoardEvent(journey=journey1, event_type=BoardType.Enter, qty=7, stop=rs3, 
                    time=journey1_start + timedelta(minutes=47))  # 7 enter at Couva
    
    be6 = BoardEvent(journey=journey1, event_type=BoardType.Exit, qty=5, stop=rs4, 
                    time=journey1_start + timedelta(minutes=65))  # 5 exit at Chaguanas
    
    be7 = BoardEvent(journey=journey1, event_type=BoardType.Enter, qty=8, stop=rs4, 
                    time=journey1_start + timedelta(minutes=67))  # 8 enter at Chaguanas
    
    # Journey 2 board events - San Fernando to UWI/St. Augustine
    be8 = BoardEvent(journey=journey2, event_type=BoardType.Enter, qty=15, stop=rs6, 
                    time=journey2_start + timedelta(minutes=5))  # 15 passengers at San Fernando
    
    be9 = BoardEvent(journey=journey2, event_type=BoardType.Exit, qty=2, stop=rs7, 
                    time=journey2_start + timedelta(minutes=35))  # 2 exit at Couva
    
    be10 = BoardEvent(journey=journey2, event_type=BoardType.Enter, qty=4, stop=rs7, 
                    time=journey2_start + timedelta(minutes=37))  # 4 enter at Couva
    
    be11 = BoardEvent(journey=journey2, event_type=BoardType.Exit, qty=5, stop=rs8, 
                    time=journey2_start + timedelta(minutes=55))  # 5 exit at Chaguanas
    
    be12 = BoardEvent(journey=journey2, event_type=BoardType.Enter, qty=8, stop=rs8, 
                    time=journey2_start + timedelta(minutes=57))  # 8 enter at Chaguanas
    
    # Journey 3 board events - Port of Spain to Arima/St. Augustine
    be13 = BoardEvent(journey=journey3, event_type=BoardType.Enter, qty=18, stop=rs11, 
                    time=journey3_start + timedelta(minutes=5))  # 18 passengers at Port of Spain
    
    be14 = BoardEvent(journey=journey3, event_type=BoardType.Exit, qty=7, stop=rs15, 
                    time=journey3_start + timedelta(minutes=25))  # 7 exit at Arima
    
    be15 = BoardEvent(journey=journey3, event_type=BoardType.Enter, qty=5, stop=rs15, 
                    time=journey3_start + timedelta(minutes=27))  # 5 enter at Arima
                    
    # Journey 4 board events - Point Fortin to San Fernando
    be16 = BoardEvent(journey=journey4, event_type=BoardType.Enter, qty=14, stop=rs16, 
                    time=journey4_start + timedelta(minutes=5))  # 14 passengers at Point Fortin
    
    be17 = BoardEvent(journey=journey4, event_type=BoardType.Exit, qty=6, stop=rs18, 
                    time=journey4_start + timedelta(minutes=20))  # 6 exit at Fyzabad
    
    be18 = BoardEvent(journey=journey4, event_type=BoardType.Enter, qty=9, stop=rs18, 
                    time=journey4_start + timedelta(minutes=22))  # 9 enter at Fyzabad
                    
    # Journey 5 board events - Bridgetown to Hole Town
    be19 = BoardEvent(journey=journey5, event_type=BoardType.Enter, qty=20, stop=rs20, 
                    time=journey5_start + timedelta(minutes=5))  # 20 passengers at Bridgetown
    
    # Journey 6 board events - Port of Spain to Chaguanas
    be20 = BoardEvent(journey=journey6, event_type=BoardType.Enter, qty=16, stop=rs23, 
                    time=journey6_start + timedelta(minutes=5))  # 16 passengers at Port of Spain
    
    # Journey 7 board events - San Fernando to Port of Spain (second bus)
    be21 = BoardEvent(journey=journey7, event_type=BoardType.Enter, qty=18, stop=rs1, 
                    time=journey7_start + timedelta(minutes=5))  # 18 passengers at San Fernando
    
    # Journey 8 board events - San Fernando to UWI (second bus)
    be22 = BoardEvent(journey=journey8, event_type=BoardType.Enter, qty=14, stop=rs6, 
                    time=journey8_start + timedelta(minutes=5))  # 14 passengers at San Fernando
    
    # Journey 9 board events - Port of Spain to Diego Martin
    be23 = BoardEvent(journey=journey9, event_type=BoardType.Enter, qty=12, stop=rs26, 
                    time=journey9_start + timedelta(minutes=5))  # 12 passengers at Port of Spain
    
    # Journey 10 board events - Arima to Diego Martin
    be24 = BoardEvent(journey=journey10, event_type=BoardType.Enter, qty=15, stop=rs28, 
                    time=journey10_start + timedelta(minutes=5))  # 15 passengers at Arima
    
    # Journey 11 board events - San Fernando to Siparia
    be25 = BoardEvent(journey=journey11, event_type=BoardType.Enter, qty=10, stop=rs33, 
                    time=journey11_start + timedelta(minutes=5))  # 10 passengers at San Fernando
    
    # Journey 12 board events - Arima to Sangre Grande
    be26 = BoardEvent(journey=journey12, event_type=BoardType.Enter, qty=8, stop=rs37, 
                    time=journey12_start + timedelta(minutes=5))  # 8 passengers at Arima
    
    db.session.add_all([
        be1, be2, be3, be4, be5, be6, be7, be8, be9, be10, 
        be11, be12, be13, be14, be15, be16, be17, be18, be19, be20, 
        be21, be22, be23, be24, be25, be26
    ])
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
    
    # Test getBuses functionality
    # buses1 = loc3.getBuses(route1.id)  # Get buses approaching Chaguanas on Route 1
    # buses2 = loc5.getBuses(route2.id)  # Get buses approaching UWI on Route 2
    # buses3 = loc11.getBuses(route5.id)  # Get buses approaching Bridgetown on Route 5
    
    # if buses1:
    #     print("\nBuses approaching Chaguanas on Route 1:")
    #     for bus in buses1:
    #         print(f"Bus: {bus['bus'].plate_num}, Distance: {bus['distance']}m, ETA: {bus['estimated_arrival']}")
    
    # if buses2:
    #     print("\nBuses approaching UWI on Route 2:")
    #     for bus in buses2:
    #         print(f"Bus: {bus['bus'].plate_num}, Distance: {bus['distance']}m, ETA: {bus['estimated_arrival']}")
            
    # if buses3:
    #     print("\nBuses approaching Bridgetown on Route 5:")
    #     for bus in buses3:
    #         print(f"Bus: {bus['bus'].plate_num}, Distance: {bus['distance']}m, ETA: {bus['estimated_arrival']}")

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
    
@test.command("journey", help="Run Journey tests")
@click.argument("type", default="all")
def journey_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "JourneyUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "JourneyIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))

app.cli.add_command(test)
app.cli.add_command(seed_cli)