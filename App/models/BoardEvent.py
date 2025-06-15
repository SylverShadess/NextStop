from App.database import db
from datetime import datetime
from enum import Enum

class BoardType(Enum):
    Enter = "Enter"
    Exit = "Exit"

    def set_type(type):
        if type == "Enter":
            return BoardType.Enter
        elif type == "Exit":
            return BoardType.Exit

class BoardEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=1)
    stop_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    bus = db.relationship('Bus', back_populates='board_events')
    stop = db.relationship('Location', back_populates='board_events')
    
    def __init__(self, bus, event_type, qty, stop, time=None):
        self.bus = bus
        self.type = event_type.value if isinstance(event_type, BoardType) else BoardType.set_type(event_type).value
        self.qty = qty
        self.stop = stop
        self.time = time if time else datetime.utcnow()
    
    def get_json(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'type': self.type.value,
            'qty': self.qty,
            'stop': self.stop.get_json() if self.stop else None,
            'time': self.time.isoformat()
        } 