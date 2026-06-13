# app/models/crew.py
from datetime import datetime
from app import db

# Many-to-many join table: Crew <-> User
crew_members = db.Table(
    'crew_members',
    db.Column('crew_id', db.Integer, db.ForeignKey('crews.id', ondelete='CASCADE'),
              primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
              primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class Crew(db.Model):
    __tablename__ = 'crews'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    station = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    members = db.relationship(
        'User',
        secondary=crew_members,
        backref=db.backref('crews', lazy='dynamic'),
        lazy='dynamic'
    )
    shifts = db.relationship('Shift', backref='crew', lazy='dynamic')
    incidents = db.relationship('Incident', backref='assigned_crew', lazy='dynamic')

    def get_available_members(self):
        """Return only ON_DUTY members — used when dispatching."""
        from app.models.user import LeaveStatus
        return self.members.filter_by(leave_status=LeaveStatus.ON_DUTY).all()

    def __repr__(self) -> str:
        return f'<Crew {self.name}>'


class Shift(db.Model):
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)

    crew_id = db.Column(db.Integer, db.ForeignKey('crews.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='SET NULL'),
                           nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def end_shift(self):
        self.end_time = datetime.utcnow()
        self.is_active = False

    def __repr__(self) -> str:
        status = 'ACTIVE' if self.is_active else 'ENDED'
        return f'<Shift crew_id={self.crew_id} [{status}]>'