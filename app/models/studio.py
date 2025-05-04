from datetime import datetime
from app import db

class Studio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    hourly_rate = db.Column(db.Float)
    half_day_rate = db.Column(db.Float)
    full_day_rate = db.Column(db.Float)
    description = db.Column(db.Text)
    equipment = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)