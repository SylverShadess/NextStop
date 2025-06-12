from App.database import db

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def __init__(self, name):
        self.name = name
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name
        } 