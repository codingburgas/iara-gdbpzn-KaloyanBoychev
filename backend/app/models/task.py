# app/models/task.py
import enum
from datetime import datetime
from app import db


class TaskType(enum.Enum):
    # Operational
    FIREFIGHTING = 'firefighting'
    EVACUATION = 'evacuation'
    SEARCH_RESCUE = 'search_rescue'
    PERIMETER_CONTROL = 'perimeter'
    VENTILATION = 'ventilation'
    # Logistics
    WATER_DELIVERY = 'water_delivery'
    FUEL_DELIVERY = 'fuel_delivery'
    EQUIPMENT_DELIVERY = 'equip_delivery'
    PERSONNEL_TRANSPORT = 'personnel_transport'
    # Administrative
    DOCUMENTATION = 'documentation'
    DEBRIEF = 'debrief'
    OTHER = 'other'


class TaskStatus(enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    task_type = db.Column(db.Enum(TaskType), nullable=False, default=TaskType.OTHER)
    status = db.Column(db.Enum(TaskStatus), nullable=False,
                       default=TaskStatus.PENDING, index=True)

    # Optional separate location for this task
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_notes = db.Column(db.String(255), nullable=True)

    # Timing
    due_by = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Foreign keys
    incident_id = db.Column(db.Integer,
                             db.ForeignKey('incidents.id', ondelete='CASCADE'),
                             nullable=False, index=True)
    assigned_crew_id = db.Column(db.Integer,
                                  db.ForeignKey('crews.id', ondelete='SET NULL'),
                                  nullable=True, index=True)
    created_by_id = db.Column(db.Integer,
                               db.ForeignKey('users.id', ondelete='SET NULL'),
                               nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assigned_crew = db.relationship('Crew', foreign_keys=[assigned_crew_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    def mark_completed(self) -> None:
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f'<Task "{self.title}" | {self.status.value}>'