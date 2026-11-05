"""Activities repository layer."""

from datetime import datetime
from typing import Any
from uuid import UUID

from storeops.models import Activity, ActivityStatus


class ActivitiesRepository:
    """In-memory repository for activities."""

    def __init__(self) -> None:
        self._activities: dict[UUID, Activity] = {}

    def create(self, activity: Activity) -> Activity:
        """Create a new activity."""
        self._activities[activity.id] = activity
        return activity

    def get_by_id(self, activity_id: UUID) -> Activity | None:
        """Get activity by ID."""
        return self._activities.get(activity_id)

    def list_all(self) -> list[Activity]:
        """List all activities."""
        return list(self._activities.values())

    def list_by_store(self, store_id: UUID) -> list[Activity]:
        """List activities by store."""
        return [a for a in self._activities.values() if a.store_id == store_id]

    def list_by_programme(self, programme_id: UUID) -> list[Activity]:
        """List activities by programme."""
        return [a for a in self._activities.values() if a.programme_id == programme_id]

    def list_by_status(self, status: ActivityStatus) -> list[Activity]:
        """List activities by status."""
        return [a for a in self._activities.values() if a.status == status]

    def update(self, activity_id: UUID, updates: dict[str, Any]) -> Activity | None:
        """Update an activity."""
        activity = self._activities.get(activity_id)
        if not activity:
            return None

        for key, value in updates.items():
            if hasattr(activity, key):
                setattr(activity, key, value)

        activity.updated_at = datetime.utcnow()
        return activity

    def delete(self, activity_id: UUID) -> bool:
        """Delete an activity."""
        if activity_id in self._activities:
            del self._activities[activity_id]
            return True
        return False
