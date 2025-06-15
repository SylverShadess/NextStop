from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from App.models.Location import Location

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
 
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
        
    def getLocations(self):
        return db.session.query(Location).all()

class Driver(User):
    full_Name = db.Column(db.String(100), nullable=True)
    licenseNo = db.Column(db.String(50), nullable=True)
    
    buses = db.relationship('Bus', back_populates='driver')
    journeys = db.relationship('Journey', back_populates='driver')

    def __init__(self, username, password, full_Name=None, licenseNo=None):
        super().__init__(username, password)
        self.full_Name = full_Name
        self.licenseNo = licenseNo
    
    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'full_Name': self.full_Name,
            'licenseNo': self.licenseNo
        }  