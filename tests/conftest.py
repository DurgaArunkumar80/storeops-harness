"""Pytest configuration and fixtures."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from storeops.activities.repository import ActivitiesRepository
from storeops.alerts.repository import AlertsRepository
from storeops.main import app
from storeops.models import (
    Activity,
    ActivityStatus,
    Alert,
    AuthContext,
    Programme,
    StaffMember,
)
from storeops.programmes.repository import ProgrammesRepository
from storeops.staff.repository import StaffRepository


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def store_id() -> UUID:
    """Create a test store ID."""
    return uuid4()


@pytest.fixture
def user_id() -> UUID:
    """Create a test user ID."""
    return uuid4()


@pytest.fixture
def auth_context(store_id: UUID, user_id: UUID) -> AuthContext:
    """Create authentication context."""
    return AuthContext(user_id=user_id, store_id=store_id, role="store_manager")


@pytest.fixture
def sample_activity(store_id: UUID, user_id: UUID) -> Activity:
    """Create a sample activity."""
    return Activity(
        id=uuid4(),
        store_id=store_id,
        programme_id=None,
        title="Test Activity",
        description="Test activity description",
        status=ActivityStatus.PENDING,
        priority="medium",
        category="maintenance",
        assignee_id=None,
        owner_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_programme(store_id: UUID) -> Programme:
    """Create a sample programme."""
    return Programme(
        id=uuid4(),
        store_id=store_id,
        name="Test Programme",
        description="Test programme description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_staff(store_id: UUID) -> StaffMember:
    """Create a sample staff member."""
    return StaffMember(
        id=uuid4(),
        store_id=store_id,
        name="John Doe",
        email="john@example.com",
        role="staff",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_alert(user_id: UUID) -> Alert:
    """Create a sample alert."""
    return Alert(
        id=uuid4(),
        user_id=user_id,
        title="Test Alert",
        message="Test alert message",
        severity="info",
        read=False,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def activities_repository() -> ActivitiesRepository:
    """Create activities repository."""
    return ActivitiesRepository()


@pytest.fixture
def programmes_repository() -> ProgrammesRepository:
    """Create programmes repository."""
    return ProgrammesRepository()


@pytest.fixture
def staff_repository() -> StaffRepository:
    """Create staff repository."""
    return StaffRepository()


@pytest.fixture
def alerts_repository() -> AlertsRepository:
    """Create alerts repository."""
    return AlertsRepository()
