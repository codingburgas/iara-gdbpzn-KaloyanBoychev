# app/models/message.py
import enum
from datetime import datetime
from app import db


class MessageType(enum.Enum):
    TEXT = 'text'
    IMAGE = 'image'
    TEMPLATE = 'template'
    SYSTEM = 'system'


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    message_type = db.Column(db.Enum(MessageType), nullable=False,
                             default=MessageType.TEXT)
    image_path = db.Column(db.String(300), nullable=True)
    read_by_user_ids = db.Column(db.Text, nullable=True, default='')

    # Foreign keys
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                          nullable=True, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id', ondelete='CASCADE'),
                            nullable=False, index=True)

    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def mark_read_by(self, user_id: int) -> None:
        ids = set(self.read_by_user_ids.split(',')) if self.read_by_user_ids else set()
        ids.discard('')
        ids.add(str(user_id))
        self.read_by_user_ids = ','.join(ids)

    def __repr__(self) -> str:
        return f'<Message id={self.id} incident_id={self.incident_id}>'


class SOSAlertStatus(enum.Enum):
    ACTIVE = 'active'
    ACKNOWLEDGED = 'acknowledged'
    RESOLVED = 'resolved'


class SOSAlert(db.Model):
    __tablename__ = 'sos_alerts'

    id = db.Column(db.Integer, primary_key=True)

    firefighter_id = db.Column(db.Integer,
                                db.ForeignKey('users.id', ondelete='CASCADE'),
                                nullable=False, index=True)
    incident_id = db.Column(db.Integer,
                             db.ForeignKey('incidents.id', ondelete='CASCADE'),
                             nullable=True, index=True)

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    status = db.Column(db.Enum(SOSAlertStatus), nullable=False,
                       default=SOSAlertStatus.ACTIVE, index=True)
    notes = db.Column(db.Text, nullable=True)

    acknowledged_by_id = db.Column(db.Integer,
                                    db.ForeignKey('users.id', ondelete='SET NULL'),
                                    nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)

    triggered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    acknowledged_by = db.relationship(
        'User',
        foreign_keys='SOSAlert.acknowledged_by_id'
    )

    def acknowledge(self, ops_user_id: int) -> None:
        self.status = SOSAlertStatus.ACKNOWLEDGED
        self.acknowledged_by_id = ops_user_id
        self.acknowledged_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f'<SOSAlert firefighter_id={self.firefighter_id} status={self.status.value}>'