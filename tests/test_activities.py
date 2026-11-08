"""Tests for activities module."""

from uuid import uuid4

import pytest

from storeops.activities.repository import ActivitiesRepository
from storeops.activities.service import ActivitiesService
from storeops.errors import ForbiddenError, NotFoundError
from storeops.models import (
    ActivityCreate,
    ActivityUpdate,
    BulkStatusUpdateRequest,
    TaskCategory,
    TaskStatus,
)


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
        category=TaskCategory.GENERAL,
    )

    activity = activities_service.create_activity(store_id, user_id, request)

    assert activity.title == "Test Activity"
    assert activity.store_id == store_id
    assert activity.owner_id == user_id
    assert activity.status == TaskStatus.TODO


def test_list_activities(activities_service: ActivitiesService) -> None:
    """Test listing activities."""
    store_id = uuid4()
    user_id = uuid4()

    request = ActivityCreate(
        title="Activity 1",
        category=TaskCategory.AUDIT,
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
        category=TaskCategory.COMPLIANCE,
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
        category=TaskCategory.COMPLIANCE,
    )

    created = activities_service.create_activity(store_id, user_id, request)
    update = ActivityUpdate(status=TaskStatus.DONE)
    updated = activities_service.update_activity(created.id, user_id, update, "staff")

    assert updated.status == TaskStatus.DONE


def test_delete_activity_owner(activities_service: ActivitiesService) -> None:
    """Test owner can delete activity."""
    store_id = uuid4()
    user_id = uuid4()
    request = ActivityCreate(
        title="Test Activity",
        category=TaskCategory.COMPLIANCE,
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
        category=TaskCategory.COMPLIANCE,
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
        category=TaskCategory.COMPLIANCE,
    )

    created = activities_service.create_activity(store_id, owner_id, request)

    with pytest.raises(ForbiddenError):
        activities_service.delete_activity(created.id, other_user_id, "staff")


def test_list_activities_by_status(activities_service: ActivitiesService) -> None:
    """Test listing activities by status."""
    store_id = uuid4()
    user_id = uuid4()

    request = ActivityCreate(title="Activity 1", category=TaskCategory.GENERAL)
    activities_service.create_activity(store_id, user_id, request)

    activities = activities_service.list_activities(store_id, status=TaskStatus.TODO)
    assert len(activities) == 1


def test_bulk_update_all_succeed(activities_service: ActivitiesService) -> None:
    """Test bulk update when all activities authorized."""
    store_id = uuid4()
    user_id = uuid4()

    task1 = activities_service.create_activity(
        store_id, user_id, ActivityCreate(title="Task 1", category=TaskCategory.AUDIT)
    )
    task2 = activities_service.create_activity(
        store_id, user_id, ActivityCreate(title="Task 2", category=TaskCategory.GENERAL)
    )

    request = BulkStatusUpdateRequest(
        activity_ids=[task1.id, task2.id], status=TaskStatus.DONE, reason="Shift complete"
    )
    response = activities_service.bulk_update_status(request, user_id, "staff")

    assert response.summary["total"] == 2
    assert response.summary["succeeded"] == 2
    assert response.summary["failed"] == 0
    assert len(response.updated) == 2
    assert len(response.failed) == 0


def test_bulk_update_partial_failure(activities_service: ActivitiesService) -> None:
    """Test bulk update with mix of authorized and unauthorized activities."""
    store_id = uuid4()
    owner_id = uuid4()
    other_user_id = uuid4()

    task1 = activities_service.create_activity(
        store_id, owner_id, ActivityCreate(title="Task 1", category=TaskCategory.AUDIT)
    )
    task2 = activities_service.create_activity(
        store_id, owner_id, ActivityCreate(title="Task 2", category=TaskCategory.GENERAL)
    )

    request = BulkStatusUpdateRequest(
        activity_ids=[task1.id, task2.id], status=TaskStatus.BLOCKED
    )
    response = activities_service.bulk_update_status(request, other_user_id, "staff")

    assert response.summary["total"] == 2
    assert response.summary["succeeded"] == 0
    assert response.summary["failed"] == 2
    assert len(response.failed) == 2


def test_bulk_update_manager_authorization(activities_service: ActivitiesService) -> None:
    """Test that manager can update any activity via bulk endpoint."""
    store_id = uuid4()
    owner_id = uuid4()
    manager_id = uuid4()

    task = activities_service.create_activity(
        store_id, owner_id, ActivityCreate(title="Task", category=TaskCategory.COMPLIANCE)
    )

    request = BulkStatusUpdateRequest(activity_ids=[task.id], status=TaskStatus.DONE)
    response = activities_service.bulk_update_status(request, manager_id, "store_manager")

    assert response.summary["succeeded"] == 1
    assert response.summary["failed"] == 0


def test_bulk_update_empty_list(activities_service: ActivitiesService) -> None:
    """Test bulk update with empty activity list."""
    request = BulkStatusUpdateRequest(activity_ids=[], status=TaskStatus.DONE)
    response = activities_service.bulk_update_status(request, uuid4(), "staff")

    assert response.summary["total"] == 0
    assert response.summary["succeeded"] == 0
    assert response.summary["failed"] == 0
    assert len(response.updated) == 0
    assert len(response.failed) == 0


def test_bulk_update_invalid_status(activities_service: ActivitiesService) -> None:
    """Test bulk update rejects invalid status values."""
    from storeops.errors import ValidationError

    store_id = uuid4()
    user_id = uuid4()

    task = activities_service.create_activity(
        store_id, user_id, ActivityCreate(title="Task", category=TaskCategory.COMPLIANCE)
    )

    request = BulkStatusUpdateRequest(
        activity_ids=[task.id], status=TaskStatus.TODO  # Invalid for bulk update
    )

    with pytest.raises(ValidationError) as exc_info:
        activities_service.bulk_update_status(request, user_id, "staff")

    assert "Invalid status" in str(exc_info.value)


def test_bulk_update_response_format(activities_service: ActivitiesService) -> None:
    """Test bulk update response has correct structure and is JSON-serializable."""
    store_id = uuid4()
    user_id = uuid4()

    task1 = activities_service.create_activity(
        store_id, user_id, ActivityCreate(title="Task 1", category=TaskCategory.AUDIT)
    )
    task2 = activities_service.create_activity(
        store_id, user_id, ActivityCreate(title="Task 2", category=TaskCategory.GENERAL)
    )

    request = BulkStatusUpdateRequest(activity_ids=[task1.id, task2.id], status=TaskStatus.DONE)
    response = activities_service.bulk_update_status(request, user_id, "staff")

    assert hasattr(response, "updated")
    assert hasattr(response, "failed")
    assert hasattr(response, "summary")
    assert isinstance(response.updated, list)
    assert isinstance(response.failed, list)
    assert isinstance(response.summary, dict)
    assert "total" in response.summary
    assert "succeeded" in response.summary
    assert "failed" in response.summary

    # Verify JSON serialization works (UUIDs can be serialized)
    json_data = response.model_dump(mode="json")
    assert isinstance(json_data, dict)
    assert "updated" in json_data
    assert "failed" in json_data


def test_bulk_update_large_batch(activities_service: ActivitiesService) -> None:
    """Test bulk update with multiple activities."""
    store_id = uuid4()
    user_id = uuid4()

    # Create 10 activities
    activity_ids = []
    for i in range(10):
        task = activities_service.create_activity(
            store_id, user_id, ActivityCreate(title=f"Task {i}", category=TaskCategory.GENERAL)
        )
        activity_ids.append(task.id)

    request = BulkStatusUpdateRequest(activity_ids=activity_ids, status=TaskStatus.DONE)
    response = activities_service.bulk_update_status(request, user_id, "staff")

    assert response.summary["total"] == 10
    assert response.summary["succeeded"] == 10
    assert response.summary["failed"] == 0
    assert len(response.updated) == 10


def test_bulk_update_blocked_status(activities_service: ActivitiesService) -> None:
    """Test bulk update with BLOCKED status."""
    store_id = uuid4()
    user_id = uuid4()

    task = activities_service.create_activity(
        store_id, user_id, ActivityCreate(title="Task", category=TaskCategory.AUDIT)
    )

    request = BulkStatusUpdateRequest(activity_ids=[task.id], status=TaskStatus.BLOCKED)
    response = activities_service.bulk_update_status(request, user_id, "staff")

    assert response.summary["succeeded"] == 1
    assert len(response.updated) == 1
    assert response.updated[0].status == TaskStatus.BLOCKED
