"""Alerts service layer."""

from uuid import UUID

from storeops.alerts.repository import AlertsRepository
from storeops.models import Alert


class AlertsService:
    """Business logic for alerts."""

    def __init__(self, repository: AlertsRepository) -> None:
        self.repository = repository

    def get_user_alerts(self, user_id: UUID) -> list[Alert]:
        """Get alerts for the authenticated user."""
        return self.repository.list_by_user(user_id)
