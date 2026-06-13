# app/models/__init__.py
# Imports all models so Flask-Migrate detects every table.

from app.models.user import User, UserRole
from app.models.crew import Crew, Shift, crew_members
from app.models.vehicle import Vehicle, VehicleType
from app.models.incident import Incident, IncidentStatus, IncidentType
from app.models.task import Task, TaskType, TaskStatus
from app.models.message import Message, SOSAlert

__all__ = [
    'User', 'UserRole',
    'Crew', 'Shift', 'crew_members',
    'Vehicle', 'VehicleType',
    'Incident', 'IncidentStatus', 'IncidentType',
    'Task', 'TaskType', 'TaskStatus',
    'Message', 'SOSAlert',
]