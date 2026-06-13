# app/models/user.py
import enum
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class UserRole(enum.Enum):
    ADMIN = 'admin'
    OPERATIONS_CENTER = 'ops'
    FIREFIGHTER = 'firefighter'
    DISPATCHER = 'dispatcher'


class LeaveStatus(enum.Enum):
    ON_DUTY = 'on_duty'
    ON_LEAVE = 'on_leave'
    SICK = 'sick'
    ON_MISSION = 'on_mission'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Identity
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Personal info
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    badge_number = db.Column(db.String(20), unique=True, nullable=True)

    # Role & availability
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.FIREFIGHTER)
    leave_status = db.Column(db.Enum(LeaveStatus), nullable=False, default=LeaveStatus.ON_DUTY)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Real-time GPS (updated by mobile app)
    last_known_latitude = db.Column(db.Float, nullable=True)
    last_known_longitude = db.Column(db.Float, nullable=True)
    location_updated_at = db.Column(db.DateTime, nullable=True)

    # Mobile push notification token
    device_push_token = db.Column(db.String(256), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # Relationships
    messages = db.relationship('Message', backref='sender', lazy='dynamic')
    sos_alerts = db.relationship(
        'SOSAlert',
        foreign_keys='SOSAlert.firefighter_id',
        backref='firefighter',
        lazy='dynamic'
    )

    # Password helpers
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # Role helpers
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_firefighter(self) -> bool:
        return self.role == UserRole.FIREFIGHTER

    @property
    def is_ops(self) -> bool:
        return self.role == UserRole.OPERATIONS_CENTER

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f'<User {self.username} | {self.role.value}>'


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))