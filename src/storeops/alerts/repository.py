"""Alerts repository layer."""

from uuid import UUID

from storeops.models import Alert


class AlertsRepository:
    """In-memory repository for alerts."""

    def __init__(self) -> None:
        self._alerts: dict[UUID, Alert] = {}

    def create(self, alert: Alert) -> Alert:
        """Create a new alert."""
        self._alerts[alert.id] = alert
        return alert

    def get_by_id(self, alert_id: UUID) -> Alert | None:
        """Get alert by ID."""
        return self._alerts.get(alert_id)

    def list_by_user(self, user_id: UUID) -> list[Alert]:
        """List alerts for a user."""
        return [a for a in self._alerts.values() if a.user_id == user_id]
