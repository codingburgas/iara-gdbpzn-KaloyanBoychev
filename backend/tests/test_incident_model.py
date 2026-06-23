# tests/test_incident_model.py
"""Unit tests for the Incident model's status lifecycle and helpers."""

from datetime import datetime
from app.models.incident import (
    Incident, IncidentType, IncidentStatus, IncidentPriority
)


def _make_incident(**overrides):
    """Helper to build a minimal valid Incident for testing."""
    defaults = dict(
        incident_type=IncidentType.STRUCTURE_FIRE,
        priority=IncidentPriority.MEDIUM,
        address='Test Address 1',
        city='Бургас',
    )
    defaults.update(overrides)
    return Incident(**defaults)


def test_new_incident_defaults_to_pending_status(db):
    """An incident with no explicit status should default to PENDING."""
    incident = _make_incident()
    db.session.add(incident)
    db.session.commit()
    assert incident.status == IncidentStatus.PENDING


def test_is_active_returns_true_for_pending(db):
    incident = _make_incident(status=IncidentStatus.PENDING)
    assert incident.is_active is True


def test_is_active_returns_false_for_resolved(db):
    incident = _make_incident(status=IncidentStatus.RESOLVED)
    assert incident.is_active is False


def test_is_active_returns_false_for_cancelled(db):
    incident = _make_incident(status=IncidentStatus.CANCELLED)
    assert incident.is_active is False


def test_is_active_returns_true_for_in_progress(db):
    incident = _make_incident(status=IncidentStatus.IN_PROGRESS)
    assert incident.is_active is True


def test_generate_reference_format(db):
    """Reference should follow INC-YYYY-NNNNN format with zero-padded ID."""
    incident = _make_incident(reported_at=datetime(2024, 6, 15))
    db.session.add(incident)
    db.session.commit()  # commit assigns incident.id

    reference = incident.generate_reference()
    assert reference.startswith('INC-2024-')
    assert reference == f'INC-2024-{incident.id:05d}'


def test_priority_critical_is_distinguishable_from_low(db):
    """Sanity check that the enum values used for UI badges are distinct."""
    critical = _make_incident(priority=IncidentPriority.CRITICAL)
    low = _make_incident(priority=IncidentPriority.LOW)
    assert critical.priority.value != low.priority.value
    assert critical.priority.value == 'critical'
    assert low.priority.value == 'low'