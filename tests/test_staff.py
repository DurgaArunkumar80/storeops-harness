"""Tests for staff module."""

from datetime import datetime
from uuid import uuid4

import pytest

from storeops.errors import NotFoundError
from storeops.models import StaffMember, StaffRole
from storeops.staff.repository import StaffRepository
from storeops.staff.service import StaffService


@pytest.fixture
def staff_service() -> StaffService:
    """Create staff service for testing."""
    repo = StaffRepository()
    return StaffService(repo)


def test_get_staff_member(staff_service: StaffService) -> None:
    """Test getting a staff member."""
    store_id = uuid4()
    staff_id = uuid4()
    staff = StaffMember(
        id=staff_id,
        store_id=store_id,
        name="John Doe",
        email="john@example.com",
        role=StaffRole.ASSOCIATE,
        created_at=datetime.utcnow(),
    )

    staff_service.repository._staff[staff_id] = staff

    result = staff_service.get_staff_member(staff_id)
    assert result.name == "John Doe"


def test_get_staff_member_not_found(staff_service: StaffService) -> None:
    """Test getting non-existent staff member."""
    with pytest.raises(NotFoundError):
        staff_service.get_staff_member(uuid4())


def test_list_staff(staff_service: StaffService) -> None:
    """Test listing staff members."""
    store_id = uuid4()
    staff_id = uuid4()
    staff = StaffMember(
        id=staff_id,
        store_id=store_id,
        name="John Doe",
        email="john@example.com",
        role=StaffRole.ASSOCIATE,
        created_at=datetime.utcnow(),
    )

    staff_service.repository._staff[staff_id] = staff

    result = staff_service.list_staff(store_id)
    assert len(result) == 1
    assert result[0].name == "John Doe"
