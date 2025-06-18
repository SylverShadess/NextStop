from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from .Location import Location


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }
 
    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.set_password(password)
        self.is_admin = is_admin

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin
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
    __mapper_args__ = {
        'polymorphic_identity': 'driver'
    }
    
    full_Name = db.Column(db.String(100), nullable=True)
    licenseNo = db.Column(db.String(50), nullable=True)
    buses = db.relationship('Bus', back_populates='driver', foreign_keys='Bus.driver_id')
    journeys = db.relationship('Journey', back_populates='driver', foreign_keys='Journey.driver_id')

    def __init__(self, username, password, is_admin=False, full_Name=None, licenseNo=None):
        super().__init__(username, password, is_admin)
        self.full_Name = full_Name
        self.licenseNo = licenseNo
    
    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin,
            'full_Name': self.full_Name,
            'licenseNo': self.licenseNo
        }  