"""Tests for activities module."""

from uuid import uuid4

import pytest

from storeops.activities.repository import ActivitiesRepository
from storeops.activities.service import ActivitiesService
from storeops.errors import ForbiddenError, NotFoundError
from storeops.models import ActivityCreate, ActivityStatus, ActivityUpdate


@pytest.fixture
def activities_service() -> ActivitiesService:
    """Create activities service for testing."""
    repo = ActivitiesRepository()
    return ActivitiesService(repo)


def test_create_activity(activities_service: ActivitiesService) -> None:
    """Test creating an activity."""
    store_id = uuid4()
    user_id = uuid4()
    request = ActivityCreate(
        title="Test Activity",
        description="Test description",
        category="maintenance",
    )

    activity = activities_service.create_activity(store_id, user_id, request)

    assert activity.title == "Test Activity"
    assert activity.store_id == store_id
    assert activity.owner_id == user_id
    assert activity.status == ActivityStatus.PENDING


def test_list_activities(activities_service: ActivitiesService) -> None:
    """Test listing activities."""
    store_id = uuid4()
    user_id = uuid4()

    request = ActivityCreate(
        title="Activity 1",
        category="maintenance",
    )
    activities_service.create_activity(store_id, user_id, request)

    activities = activities_service.list_activities(store_id)
    assert len(activities) == 1


def test_get_activity(activities_service: ActivitiesService) -> None:
    """Test getting an activity by ID."""
    store_id = uuid4()
    user_id = uuid4()
    request = ActivityCreate(
        title="Test Activity",
        category="maintenance",
    )

    created = activities_service.create_activity(store_id, user_id, request)
    activity = activities_service.get_activity(created.id)

    assert activity.id == created.id
    assert activity.title == "Test Activity"


def test_get_activity_not_found(activities_service: ActivitiesService) -> None:
    """Test getting non-existent activity."""
    with pytest.raises(NotFoundError):
        activities_service.get_activity(uuid4())


def test_update_activity(activities_service: ActivitiesService) -> None:
    """Test updating an activity."""
    store_id = uuid4()
    user_id = uuid4()
    request = ActivityCreate(
        title="Test Activity",
        category="maintenance",
    )

    created = activities_service.create_activity(store_id, user_id, request)
    update = ActivityUpdate(status=ActivityStatus.COMPLETED)
    updated = activities_service.update_activity(created.id, user_id, update, "staff")

    assert updated.status == ActivityStatus.COMPLETED


def test_delete_activity_owner(activities_service: ActivitiesService) -> None:
    """Test owner can delete activity."""
    store_id = uuid4()
    user_id = uuid4()
    request = ActivityCreate(
        title="Test Activity",
        category="maintenance",
    )

    created = activities_service.create_activity(store_id, user_id, request)
    activities_service.delete_activity(created.id, user_id, "staff")

    with pytest.raises(NotFoundError):
        activities_service.get_activity(created.id)


def test_delete_activity_manager(activities_service: ActivitiesService) -> None:
    """Test store manager can delete any activity."""
    store_id = uuid4()
    owner_id = uuid4()
    manager_id = uuid4()
    request = ActivityCreate(
        title="Test Activity",
        category="maintenance",
    )

    created = activities_service.create_activity(store_id, owner_id, request)
    activities_service.delete_activity(created.id, manager_id, "store_manager")

    with pytest.raises(NotFoundError):
        activities_service.get_activity(created.id)


def test_delete_activity_forbidden(activities_service: ActivitiesService) -> None:
    """Test non-owner cannot delete activity."""
    store_id = uuid4()
    owner_id = uuid4()
    other_user_id = uuid4()
    request = ActivityCreate(
        title="Test Activity",
        category="maintenance",
    )

    created = activities_service.create_activity(store_id, owner_id, request)

    with pytest.raises(ForbiddenError):
        activities_service.delete_activity(created.id, other_user_id, "staff")


def test_list_activities_by_status(activities_service: ActivitiesService) -> None:
    """Test listing activities by status."""
    store_id = uuid4()
    user_id = uuid4()

    request = ActivityCreate(title="Activity 1", category="maintenance")
    activities_service.create_activity(store_id, user_id, request)

    activities = activities_service.list_activities(store_id, status=ActivityStatus.PENDING)
    assert len(activities) == 1
