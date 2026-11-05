"""Reports repository layer."""

from uuid import UUID

from storeops.models import Report


class ReportsRepository:
    """In-memory repository for reports."""

    def __init__(self) -> None:
        self._reports: dict[UUID, Report] = {}

    def create(self, report: Report) -> Report:
        """Create a new report."""
        self._reports[report.id] = report
        return report

    def get_by_id(self, report_id: UUID) -> Report | None:
        """Get report by ID."""
        return self._reports.get(report_id)

    def list_by_store(self, store_id: UUID) -> list[Report]:
        """List reports by store."""
        return [r for r in self._reports.values() if r.store_id == store_id]

    def list_by_region(self, region_id: UUID) -> list[Report]:
        """List reports by region."""
        return [r for r in self._reports.values() if r.region_id == region_id]
