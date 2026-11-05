"""Tests for alerts module."""

from datetime import datetime
from uuid import uuid4

import pytest

from storeops.alerts.repository import AlertsRepository
from storeops.alerts.service import AlertsService
from storeops.models import Alert


@pytest.fixture
def alerts_service() -> AlertsService:
    """Create alerts service for testing."""
    repo = AlertsRepository()
    return AlertsService(repo)


def test_get_user_alerts(alerts_service: AlertsService) -> None:
    """Test getting alerts for a user."""
    user_id = uuid4()
    alert = Alert(
        id=uuid4(),
        user_id=user_id,
        title="Test Alert",
        message="Test message",
        severity="info",
        read=False,
        created_at=datetime.utcnow(),
    )

    repo = alerts_service.repository
    repo.create(alert)

    alerts = alerts_service.get_user_alerts(user_id)
    assert len(alerts) == 1
    assert alerts[0].title == "Test Alert"


def test_get_user_alerts_empty(alerts_service: AlertsService) -> None:
    """Test getting alerts for user with no alerts."""
    user_id = uuid4()
    alerts = alerts_service.get_user_alerts(user_id)
    assert len(alerts) == 0


def test_get_user_alerts_filtered(alerts_service: AlertsService) -> None:
    """Test alerts are filtered by user."""
    user_id1 = uuid4()
    user_id2 = uuid4()

    alert1 = Alert(
        id=uuid4(),
        user_id=user_id1,
        title="Alert 1",
        message="Message 1",
        severity="info",
        read=False,
        created_at=datetime.utcnow(),
    )
    alert2 = Alert(
        id=uuid4(),
        user_id=user_id2,
        title="Alert 2",
        message="Message 2",
        severity="warning",
        read=False,
        created_at=datetime.utcnow(),
    )

    repo = alerts_service.repository
    repo.create(alert1)
    repo.create(alert2)

    alerts = alerts_service.get_user_alerts(user_id1)
    assert len(alerts) == 1
    assert alerts[0].user_id == user_id1
