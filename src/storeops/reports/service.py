"""Reports service layer."""

from uuid import UUID

from storeops.models import Report
from storeops.reports.repository import ReportsRepository


class ReportsService:
    """Business logic for reports."""

    def __init__(self, repository: ReportsRepository) -> None:
        self.repository = repository

    def get_store_reports(self, store_id: UUID) -> list[Report]:
        """Get reports for a store."""
        return self.repository.list_by_store(store_id)

    def get_region_reports(self, region_id: UUID) -> list[Report]:
        """Get reports for a region."""
        return self.repository.list_by_region(region_id)
