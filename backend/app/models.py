from app.extensions import db
import datetime

class DataLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    data = db.Column(db.JSON, nullable=False)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.String(255), nullable=True)
    data_hash = db.Column(db.String(64), index=True, nullable=True)
