from datetime import datetime
from app import db

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    studio_id = db.Column(db.Integer, db.ForeignKey('studio.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    booking_type = db.Column(db.String(20))  # hourly/half-day/full-day
    status = db.Column(db.String(20), default='pending')  # pending/confirmed/cancelled
    total_amount = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bookings')
    studio = db.relationship('Studio', backref='bookings')