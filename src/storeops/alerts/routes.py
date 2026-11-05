"""Alerts API routes."""

from fastapi import APIRouter, Depends

from storeops.alerts.repository import AlertsRepository
from storeops.alerts.service import AlertsService
from storeops.models import Alert, AuthContext

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# In-memory repositories
_alerts_repo = AlertsRepository()
_alerts_service = AlertsService(_alerts_repo)


def get_alerts_service() -> AlertsService:
    """Dependency injection for alerts service."""
    return _alerts_service


@router.get("", response_model=list[Alert])
async def get_alerts(
    auth: AuthContext,
    service: AlertsService = Depends(get_alerts_service),
) -> list[Alert]:
    """Get alerts for the authenticated user."""
    return service.get_user_alerts(auth.user_id)
