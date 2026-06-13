# app/models/incident.py
import enum
from datetime import datetime
from app import db


class IncidentType(enum.Enum):
    STRUCTURE_FIRE = 'structure_fire'
    WILDFIRE = 'wildfire'
    VEHICLE_FIRE = 'vehicle_fire'
    TECHNICAL_RESCUE = 'technical_rescue'
    HAZMAT = 'hazmat'
    WATER_RESCUE = 'water_rescue'
    MEDICAL_ASSIST = 'medical_assist'
    FALSE_ALARM = 'false_alarm'
    PREVENTIVE = 'preventive'
    OTHER = 'other'


class IncidentStatus(enum.Enum):
    PENDING = 'pending'
    DISPATCHED = 'dispatched'
    ON_SCENE = 'on_scene'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CANCELLED = 'cancelled'


class IncidentPriority(enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True)

    # Reference number, e.g. INC-2024-00001
    reference_number = db.Column(db.String(30), unique=True, nullable=True, index=True)

    # Classification
    incident_type = db.Column(db.Enum(IncidentType), nullable=False,
                              default=IncidentType.OTHER)
    status = db.Column(db.Enum(IncidentStatus), nullable=False,
                       default=IncidentStatus.PENDING, index=True)
    priority = db.Column(db.Enum(IncidentPriority), nullable=False,
                         default=IncidentPriority.MEDIUM)

    # Location
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Бургас')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Details
    description = db.Column(db.Text, nullable=True)
    caller_phone = db.Column(db.String(20), nullable=True)
    caller_name = db.Column(db.String(100), nullable=True)
    hazard_notes = db.Column(db.Text, nullable=True)
    action_plan = db.Column(db.Text, nullable=True)

    # Timestamps
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    dispatched_at = db.Column(db.DateTime, nullable=True)
    on_scene_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Foreign keys
    registered_by_id = db.Column(db.Integer,
                                  db.ForeignKey('users.id', ondelete='SET NULL'),
                                  nullable=True)
    assigned_crew_id = db.Column(db.Integer,
                                  db.ForeignKey('crews.id', ondelete='SET NULL'),
                                  nullable=True, index=True)
    assigned_vehicle_id = db.Column(db.Integer,
                                     db.ForeignKey('vehicles.id', ondelete='SET NULL'),
                                     nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    registered_by = db.relationship('User', foreign_keys=[registered_by_id])
    assigned_vehicle = db.relationship('Vehicle', foreign_keys=[assigned_vehicle_id])
    tasks = db.relationship('Task', backref='incident', lazy='dynamic')
    messages = db.relationship('Message', backref='incident', lazy='dynamic')
    sos_alerts = db.relationship('SOSAlert', backref='incident', lazy='dynamic')

    def generate_reference(self) -> str:
        year = self.reported_at.year if self.reported_at else datetime.utcnow().year
        return f"INC-{year}-{self.id:05d}"

    @property
    def is_active(self) -> bool:
        return self.status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]

    def __repr__(self) -> str:
        ref = self.reference_number or f'id={self.id}'
        return f'<Incident {ref} | {self.status.value}>'