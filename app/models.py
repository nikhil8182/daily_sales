from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class PRVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pr_name = db.Column(db.String(100), nullable=False)
    visit_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    client_name = db.Column(db.String(100), nullable=False)
    manager_incharge = db.Column(db.String(100), nullable=False)
    visit_status = db.Column(db.String(50), default='Waiting to start')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TCActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telecaller_name = db.Column(db.String(100), nullable=False)
    manager_incharge = db.Column(db.String(100), nullable=False)
    calls_made = db.Column(db.Integer, default=0)
    visits_booked = db.Column(db.Integer, default=0)
    visits_confirmed = db.Column(db.Integer, default=0)
    leads_acquired = db.Column(db.Integer, default=0)
    bucket_leads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'PR', 'TC', or 'SM' (Sales Manager)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)