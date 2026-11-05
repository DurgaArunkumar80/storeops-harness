"""Reports API routes."""

from fastapi import APIRouter, Depends

from storeops.models import AuthContext, Report
from storeops.reports.repository import ReportsRepository
from storeops.reports.service import ReportsService

router = APIRouter(prefix="/api/reports", tags=["reports"])

# In-memory repositories
_reports_repo = ReportsRepository()
_reports_service = ReportsService(_reports_repo)


def get_reports_service() -> ReportsService:
    """Dependency injection for reports service."""
    return _reports_service


@router.get("", response_model=list[Report])
async def get_reports(
    auth: AuthContext,
    service: ReportsService = Depends(get_reports_service),
) -> list[Report]:
    """Get reports for store or region."""
    store_reports = service.get_store_reports(auth.store_id)
    return store_reports
