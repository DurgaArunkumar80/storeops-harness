"""Activities API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette.status import HTTP_204_NO_CONTENT

from storeops.activities.repository import ActivitiesRepository
from storeops.activities.service import ActivitiesService
from storeops.models import Activity, ActivityCreate, ActivityStatus, ActivityUpdate, AuthContext

router = APIRouter(prefix="/api/activities", tags=["activities"])

# In-memory repositories
_activities_repo = ActivitiesRepository()
_activities_service = ActivitiesService(_activities_repo)


def get_activities_service() -> ActivitiesService:
    """Dependency injection for activities service."""
    return _activities_service


@router.get("", response_model=list[Activity])
async def list_activities(
    auth: AuthContext,
    service: ActivitiesService = Depends(get_activities_service),
    programme_id: UUID | None = Query(None),
    status: ActivityStatus | None = Query(None),
) -> list[Activity]:
    """List activities with optional programme and status filters."""
    return service.list_activities(auth.store_id, programme_id=programme_id, status=status)


@router.post("", response_model=Activity, status_code=201)
async def create_activity(
    auth: AuthContext,
    request: ActivityCreate,
    service: ActivitiesService = Depends(get_activities_service),
) -> Activity:
    """Create a new activity."""
    return service.create_activity(auth.store_id, auth.user_id, request)


@router.get("/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: UUID,
    auth: AuthContext,
    service: ActivitiesService = Depends(get_activities_service),
) -> Activity:
    """Get an activity by ID."""
    return service.get_activity(activity_id)


@router.patch("/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: UUID,
    request: ActivityUpdate,
    auth: AuthContext,
    service: ActivitiesService = Depends(get_activities_service),
) -> Activity:
    """Update activity fields: status, priority, category, and assignee."""
    return service.update_activity(activity_id, auth.user_id, request, auth.role)


@router.delete("/{activity_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    auth: AuthContext,
    service: ActivitiesService = Depends(get_activities_service),
) -> None:
    """Delete an activity. Only the activity owner or store manager is permitted to delete."""
    service.delete_activity(activity_id, auth.user_id, auth.role)
