from datetime import datetime
from app import db

class StripeEvent(db.Model):
    __tablename__ = "stripe_events"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(255), nullable=True)
    stripe_session_id = db.Column(db.String(255), nullable=True, index=True)
    commande_id = db.Column(db.Integer, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)