# app/models/leave_request.py
import enum
from datetime import datetime
from app import db


class LeaveRequestStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    DENIED = 'denied'


class LeaveRequestType(enum.Enum):
    VACATION = 'vacation'
    SICK = 'sick'
    PERSONAL = 'personal'
    OTHER = 'other'


class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    leave_type = db.Column(db.Enum(LeaveRequestType), nullable=False,
                           default=LeaveRequestType.VACATION)
    status = db.Column(db.Enum(LeaveRequestStatus), nullable=False,
                       default=LeaveRequestStatus.PENDING, index=True)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=True)

    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                                nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id])
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])

    def __repr__(self):
        return f'<LeaveRequest user_id={self.user_id} {self.status.value}>'