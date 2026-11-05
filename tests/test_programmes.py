"""Tests for programmes module."""

from uuid import uuid4

import pytest

from storeops.errors import ConflictError, NotFoundError
from storeops.models import ProgrammeCreate, ProgrammeMemberCreate
from storeops.programmes.repository import ProgrammesRepository
from storeops.programmes.service import ProgrammesService


@pytest.fixture
def programmes_service() -> ProgrammesService:
    """Create programmes service for testing."""
    repo = ProgrammesRepository()
    return ProgrammesService(repo)


def test_create_programme(programmes_service: ProgrammesService) -> None:
    """Test creating a programme."""
    store_id = uuid4()
    request = ProgrammeCreate(
        name="Test Programme",
        description="Test description",
    )

    programme = programmes_service.create_programme(store_id, request)

    assert programme.name == "Test Programme"
    assert programme.store_id == store_id


def test_list_programmes(programmes_service: ProgrammesService) -> None:
    """Test listing programmes."""
    store_id = uuid4()
    request = ProgrammeCreate(name="Test Programme")

    programmes_service.create_programme(store_id, request)

    programmes = programmes_service.list_programmes(store_id)
    assert len(programmes) == 1


def test_add_member(programmes_service: ProgrammesService) -> None:
    """Test adding a member to a programme."""
    store_id = uuid4()
    staff_id = uuid4()
    programme_request = ProgrammeCreate(name="Test Programme")
    programme = programmes_service.create_programme(store_id, programme_request)

    member_request = ProgrammeMemberCreate(staff_id=staff_id)
    member = programmes_service.add_member(programme.id, member_request)

    assert member.staff_id == staff_id
    assert member.programme_id == programme.id


def test_add_member_duplicate(programmes_service: ProgrammesService) -> None:
    """Test adding duplicate member raises error."""
    store_id = uuid4()
    staff_id = uuid4()
    programme_request = ProgrammeCreate(name="Test Programme")
    programme = programmes_service.create_programme(store_id, programme_request)

    member_request = ProgrammeMemberCreate(staff_id=staff_id)
    programmes_service.add_member(programme.id, member_request)

    with pytest.raises(ConflictError):
        programmes_service.add_member(programme.id, member_request)


def test_add_member_programme_not_found(programmes_service: ProgrammesService) -> None:
    """Test adding member to non-existent programme."""
    staff_id = uuid4()
    member_request = ProgrammeMemberCreate(staff_id=staff_id)

    with pytest.raises(NotFoundError):
        programmes_service.add_member(uuid4(), member_request)
