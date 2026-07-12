from datetime import datetime, UTC
from extensions import db


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    trek_id = db.Column(db.Integer,db.ForeignKey("trek.id"),nullable=False)
    
    booking_date = db.Column(db.DateTime,default=lambda: datetime.now(UTC),nullable=False)
    status = db.Column(db.String(20),default="Booked",nullable=False)
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(UTC),nullable=False)

    user = db.relationship("User",backref="bookings")
    trek = db.relationship("Trek",backref="bookings")

    def __repr__(self):
        return f"<Booking {self.id}>"