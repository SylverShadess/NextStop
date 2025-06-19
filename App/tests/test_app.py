import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)

# Import the necessary controllers and models for journey tests
from App.models import Journey, Route, Bus, User, Location, Area, RouteStop
from App.models.User import Driver
from App.models.BoardEvent import BoardType
from App.models.Location import LocationType
from App.controllers import (
    create_journey_board_event,
    create_journey_track_event,
    complete_journey,
    cancel_journey,
    move_to_next_stop,
    move_to_previous_stop,
    get_journey_progress,
    get_journey_stats
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob", "bobpass")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob", "is_admin":False})
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


def test_authenticate():
    user = create_user("bob", "bobpass")
    assert login("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "bobpass")
        assert user.username == "rick"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bob", "is_admin":False}, {"id":2, "username":"rick", "is_admin":False}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
        
'''
    Journey Integration Tests
'''

class JourneyIntegrationTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test data for journey tests"""
        # Create areas
        cls.start_area = Area("Start Area")
        cls.end_area = Area("End Area")
        db.session.add(cls.start_area)
        db.session.add(cls.end_area)
        db.session.commit()
        
        # Create route
        cls.route = Route("Test Route", 5, cls.start_area, cls.end_area)
        db.session.add(cls.route)
        db.session.commit()
        
        # Create locations for stops
        cls.location1 = Location("Stop 1", 1.0, 1.0, LocationType.Stop)
        cls.location2 = Location("Stop 2", 2.0, 2.0, LocationType.Stop)
        cls.location3 = Location("Stop 3", 3.0, 3.0, LocationType.Terminal)
        db.session.add_all([cls.location1, cls.location2, cls.location3])
        db.session.commit()
        
        # Create route stops
        cls.stop1 = RouteStop(cls.route, cls.location1, 0)
        cls.stop2 = RouteStop(cls.route, cls.location2, 1)
        cls.stop3 = RouteStop(cls.route, cls.location3, 2)
        db.session.add_all([cls.stop1, cls.stop2, cls.stop3])
        db.session.commit()
        
        # Create driver user - use Driver subclass instead of User
        cls.driver = Driver("driver1", "driverpass", False, "Test Driver", "DL12345")
        db.session.add(cls.driver)
        db.session.commit()
        
        # Create bus
        cls.bus = Bus("TEST123", cls.driver, cls.route, 50)
        db.session.add(cls.bus)
        db.session.commit()
        
        # Create journey
        cls.journey = Journey(cls.driver, cls.route, cls.bus)
        cls.journey.startJourney()
    
    def test_journey_creation(self):
        """Test that journey was created properly"""
        journey = Journey.query.get(self.journey.id)
        self.assertIsNotNone(journey)
        self.assertEqual(journey.bus.plate_num, "TEST123")
        self.assertEqual(journey.route.name, "Test Route")
        self.assertEqual(journey.driver.username, "driver1")
        self.assertEqual(journey.status, "In Progress")
        self.assertEqual(journey.current_stop_index, 0)
    
    def test_create_journey_board_event(self):
        """Test creating board events for journey"""
        # Create a boarding event
        board_event = create_journey_board_event(
            self.journey.id, 
            "Enter", 
            5, 
            self.stop1.id
        )
        
        self.assertIsNotNone(board_event)
        self.assertEqual(board_event.qty, 5)
        self.assertEqual(board_event.type, "Enter")
        
        # Verify bus passenger count
        self.assertEqual(self.bus.passenger_count, 5)
        
        # Create an alighting event
        board_event = create_journey_board_event(
            self.journey.id, 
            "Exit", 
            2, 
            self.stop2.id
        )
        
        self.assertIsNotNone(board_event)
        self.assertEqual(board_event.qty, 2)
        self.assertEqual(board_event.type, "Exit")
        
        # Verify bus passenger count decreased
        self.assertEqual(self.bus.passenger_count, 3)
    
    def test_create_journey_track_event(self):
        """Test creating location tracking events"""
        track_event = create_journey_track_event(self.journey.id, 1.5, 1.5)
        self.assertIsNotNone(track_event)
        self.assertEqual(track_event.lat, 1.5)
        self.assertEqual(track_event.lng, 1.5)
    
    def test_journey_stop_navigation(self):
        """Test journey stop navigation functions"""
        # Test initial stop
        current_stop = self.journey.getCurrentStop()
        self.assertEqual(current_stop.id, self.stop1.id)
        
        # Test moving to next stop
        next_stop = move_to_next_stop(self.journey.id)
        self.assertEqual(next_stop.id, self.stop2.id)
        self.assertEqual(self.journey.current_stop_index, 1)
        
        # Test moving to previous stop
        prev_stop = move_to_previous_stop(self.journey.id)
        self.assertEqual(prev_stop.id, self.stop1.id)
        self.assertEqual(self.journey.current_stop_index, 0)
        
        # Test journey progress calculation
        progress = get_journey_progress(self.journey.id)
        self.assertEqual(progress, 0)  # At first stop (0 of 2)
        
        # Move to last stop
        move_to_next_stop(self.journey.id)  # To stop2
        move_to_next_stop(self.journey.id)  # To stop3
        progress = get_journey_progress(self.journey.id)
        self.assertEqual(progress, 100)  # At last stop (2 of 2)
    
    def test_journey_completion(self):
        """Test journey completion and cancellation"""
        # First, create a new journey for testing completion
        new_journey = Journey(self.driver, self.route, self.bus)
        new_journey.startJourney()
        
        # Complete the journey
        result = complete_journey(new_journey.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "Completed")
        self.assertIsNotNone(result.endTime)
        
        # Create another journey for testing cancellation
        another_journey = Journey(self.driver, self.route, self.bus)
        another_journey.startJourney()
        
        # Cancel the journey
        result = cancel_journey(another_journey.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "Cancelled")
        self.assertIsNotNone(result.endTime)
        
    def test_journey_stats(self):
        """Test getting journey statistics"""
        # Create a new journey for this test
        stats_journey = Journey(self.driver, self.route, self.bus)
        stats_journey.startJourney()
        
        # Add some board events (10 passengers enter at first stop)
        create_journey_board_event(
            stats_journey.id,
            "Enter",
            10,
            self.stop1.id
        )
        
        # Move to the next stop
        move_to_next_stop(stats_journey.id)
        
        # 3 passengers exit, 2 enter at second stop
        create_journey_board_event(
            stats_journey.id,
            "Exit",
            3,
            self.stop2.id
        )
        
        create_journey_board_event(
            stats_journey.id,
            "Enter",
            2,
            self.stop2.id
        )
        
        # Move to the final stop
        move_to_next_stop(stats_journey.id)
        
        # All remaining passengers exit
        create_journey_board_event(
            stats_journey.id,
            "Exit",
            9,
            self.stop3.id
        )
        
        # Complete the journey
        complete_journey(stats_journey.id)
        
        # Get journey stats
        stats = get_journey_stats(stats_journey.id)
        
        # Verify stats
        self.assertIsNotNone(stats)
        self.assertEqual(stats['journey_id'], stats_journey.id)
        self.assertEqual(stats['route_name'], "Test Route")
        self.assertEqual(stats['total_passengers'], 12)  # 10 + 2 = 12 total entries
        self.assertEqual(stats['revenue'], 60)  # 12 passengers * 5 cost = 60

