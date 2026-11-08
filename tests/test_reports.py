"""Tests for reports module."""

from datetime import datetime
from uuid import uuid4

import pytest

from storeops.models import Report, ReportStatus, ReportType
from storeops.reports.repository import ReportsRepository
from storeops.reports.service import ReportsService


@pytest.fixture
def reports_service() -> ReportsService:
    """Create reports service for testing."""
    repo = ReportsRepository()
    return ReportsService(repo)


def test_get_store_reports(reports_service: ReportsService) -> None:
    """Test getting reports for a store."""
    store_id = uuid4()
    report = Report(
        id=uuid4(),
        store_id=store_id,
        region_id=None,
        report_type=ReportType.STORE_SUMMARY,
        status=ReportStatus.READY,
        data={"metric": "value"},
        created_at=datetime.utcnow(),
    )

    reports_service.repository.create(report)

    result = reports_service.get_store_reports(store_id)
    assert len(result) == 1
    assert result[0].report_type == ReportType.STORE_SUMMARY


def test_get_region_reports(reports_service: ReportsService) -> None:
    """Test getting reports for a region."""
    region_id = uuid4()
    report = Report(
        id=uuid4(),
        store_id=None,
        region_id=region_id,
        report_type=ReportType.REGIONAL_ROLLUP,
        status=ReportStatus.READY,
        data={"metric": "value"},
        created_at=datetime.utcnow(),
    )

    reports_service.repository.create(report)

    result = reports_service.get_region_reports(region_id)
    assert len(result) == 1
    assert result[0].report_type == ReportType.REGIONAL_ROLLUP
