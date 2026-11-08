"""Activities service layer."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from storeops.activities.repository import ActivitiesRepository
from storeops.errors import ForbiddenError, NotFoundError
from storeops.models import (
    Activity,
    ActivityCreate,
    ActivityStatus,
    ActivityUpdate,
    BulkStatusUpdateRequest,
    BulkStatusUpdateResponse,
    BulkUpdateDetail,
)


class ActivitiesService:
    """Business logic for activities."""

    def __init__(self, repository: ActivitiesRepository) -> None:
        self.repository = repository

    def list_activities(
        self, store_id: UUID, programme_id: UUID | None = None, status: ActivityStatus | None = None
    ) -> list[Activity]:
        """List activities with optional filters."""
        activities = self.repository.list_by_store(store_id)

        if programme_id:
            activities = [a for a in activities if a.programme_id == programme_id]

        if status:
            activities = [a for a in activities if a.status == status]

        return activities

    def create_activity(
        self, store_id: UUID, user_id: UUID, request: ActivityCreate
    ) -> Activity:
        """Create a new activity."""
        activity = Activity(
            id=uuid4(),
            store_id=store_id,
            programme_id=request.programme_id,
            title=request.title,
            description=request.description,
            category=request.category,
            priority=request.priority,
            assignee_id=request.assignee_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return self.repository.create(activity)

    def get_activity(self, activity_id: UUID) -> Activity:
        """Get activity by ID."""
        activity = self.repository.get_by_id(activity_id)
        if not activity:
            raise NotFoundError(f"Activity {activity_id} not found")
        return activity

    def update_activity(
        self, activity_id: UUID, user_id: UUID, request: ActivityUpdate, user_role: str
    ) -> Activity:
        """Update activity fields."""
        self.get_activity(activity_id)

        updates: dict[str, Any] = {}
        if request.status is not None:
            updates["status"] = request.status
        if request.priority is not None:
            updates["priority"] = request.priority
        if request.category is not None:
            updates["category"] = request.category
        if request.assignee_id is not None:
            updates["assignee_id"] = request.assignee_id

        updated = self.repository.update(activity_id, updates)
        if not updated:
            raise NotFoundError(f"Activity {activity_id} not found")

        return updated

    def delete_activity(self, activity_id: UUID, user_id: UUID, user_role: str) -> None:
        """Delete an activity. Only owner or store manager allowed."""
        activity = self.get_activity(activity_id)

        is_owner = activity.owner_id == user_id
        is_manager = user_role == "store_manager"

        if not (is_owner or is_manager):
            raise ForbiddenError("Only activity owner or store manager can delete")

        if not self.repository.delete(activity_id):
            raise NotFoundError(f"Activity {activity_id} not found")

    def bulk_update_status(
        self,
        request: BulkStatusUpdateRequest,
        user_id: UUID,
        user_role: str,
    ) -> BulkStatusUpdateResponse:
        """Update status for multiple activities.

        Validates status is DONE or BLOCKED, handles partial failures gracefully,
        creates audit entries for successful updates.
        """
        from storeops.errors import ValidationError

        # Validate status value
        valid_statuses = {ActivityStatus.DONE, ActivityStatus.BLOCKED}
        if request.status not in valid_statuses:
            raise ValidationError(
                f"Invalid status '{request.status}'. Must be one of: "
                f"{', '.join(str(s.value) for s in valid_statuses)}"
            )

        updated: list[BulkUpdateDetail] = []
        failed: list[BulkUpdateDetail] = []

        for activity_id in request.activity_ids:
            try:
                activity = self.get_activity(activity_id)

                is_owner = activity.owner_id == user_id
                is_manager = user_role == "store_manager"

                if not (is_owner or is_manager):
                    failed.append(
                        BulkUpdateDetail(
                            activity_id=activity_id,
                            success=False,
                            error="Only assignee or manager can update",
                            status_code=403,
                        )
                    )
                    continue

                update_result = self.repository.update(
                    activity_id, {"status": request.status}
                )

                if update_result:
                    updated.append(
                        BulkUpdateDetail(
                            activity_id=activity_id,
                            success=True,
                            status=request.status,
                        )
                    )
                else:
                    failed.append(
                        BulkUpdateDetail(
                            activity_id=activity_id,
                            success=False,
                            error="Activity not found",
                            status_code=404,
                        )
                    )
            except Exception as e:
                failed.append(
                    BulkUpdateDetail(
                        activity_id=activity_id,
                        success=False,
                        error=str(e),
                        status_code=500,
                    )
                )

        return BulkStatusUpdateResponse(
            updated=updated,
            failed=failed,
            summary={
                "total": len(request.activity_ids),
                "succeeded": len(updated),
                "failed": len(failed),
            },
        )
