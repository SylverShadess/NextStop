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
        else:
            return None

class BoardEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journey_id = db.Column(db.Integer, db.ForeignKey('journey.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=1)
    stop_id = db.Column(db.Integer, db.ForeignKey('route_stop.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    journey = db.relationship('Journey', back_populates='board_events')
    stop = db.relationship('RouteStop', back_populates='board_events')
    
    def __init__(self, journey, event_type, qty, stop, time=None):
        try:
            self.journey = journey
            self.type = event_type.value if isinstance(event_type, BoardType) else BoardType.set_type(event_type).value
            self.qty = qty
            self.stop = stop
            self.time = time if time else datetime.utcnow()
            
            # Update the bus passenger count
            if journey and journey.bus:
                bus = journey.bus
                if self.type == "Enter":
                    if not bus.board_passengers(qty):
                        raise ValueError(f"Cannot board {qty} passengers. Bus capacity exceeded.")
                elif self.type == "Exit":
                    if not bus.alight_passengers(qty):
                        raise ValueError(f"Cannot alight {qty} passengers. Not enough passengers on bus.")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error creating board event: {str(e)}")
    
    def get_json(self):
        return {
            'id': self.id,
            'journey_id': self.journey_id,
            'type': self.type,
            'qty': self.qty,
            'stop': self.stop.get_json() if self.stop else None,
            'time': self.time.isoformat()
        } 