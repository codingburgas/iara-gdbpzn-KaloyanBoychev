# app/models/vehicle.py
import enum
from datetime import datetime
from app import db


class VehicleType(enum.Enum):
    FIRE_TRUCK = 'fire_truck'
    WATER_TANKER = 'water_tanker'
    LADDER_TRUCK = 'ladder_truck'
    RESCUE_VEHICLE = 'rescue_vehicle'
    COMMAND_VEHICLE = 'command_vehicle'
    AMBULANCE = 'ambulance'
    HAZMAT = 'hazmat'
    OTHER = 'other'


class VehicleStatus(enum.Enum):
    AVAILABLE = 'available'
    DEPLOYED = 'deployed'
    MAINTENANCE = 'maintenance'
    RETIRED = 'retired'


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)

    # Identification
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    call_sign = db.Column(db.String(20), unique=True, nullable=True)
    make = db.Column(db.String(64), nullable=True)
    model = db.Column(db.String(64), nullable=True)
    year = db.Column(db.Integer, nullable=True)

    # Classification
    vehicle_type = db.Column(db.Enum(VehicleType), nullable=False,
                             default=VehicleType.FIRE_TRUCK)
    status = db.Column(db.Enum(VehicleStatus), nullable=False,
                       default=VehicleStatus.AVAILABLE, index=True)

    # Capacity
    water_capacity_liters = db.Column(db.Integer, nullable=True)
    crew_capacity = db.Column(db.Integer, nullable=True)

    # Real-time GPS
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    gps_updated_at = db.Column(db.DateTime, nullable=True)

    home_station = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    shifts = db.relationship('Shift', backref='vehicle', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Vehicle {self.plate_number} | {self.vehicle_type.value}>'