"""Programmes API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends

from storeops.models import (
    AuthContext,
    Programme,
    ProgrammeCreate,
    ProgrammeMember,
    ProgrammeMemberCreate,
)
from storeops.programmes.repository import ProgrammesRepository
from storeops.programmes.service import ProgrammesService

router = APIRouter(prefix="/api/programmes", tags=["programmes"])

# In-memory repositories
_programmes_repo = ProgrammesRepository()
_programmes_service = ProgrammesService(_programmes_repo)


def get_programmes_service() -> ProgrammesService:
    """Dependency injection for programmes service."""
    return _programmes_service


@router.get("", response_model=list[Programme])
async def list_programmes(
    auth: AuthContext,
    service: ProgrammesService = Depends(get_programmes_service),
) -> list[Programme]:
    """List programmes for the authenticated store."""
    return service.list_programmes(auth.store_id)


@router.post("", response_model=Programme, status_code=201)
async def create_programme(
    auth: AuthContext,
    request: ProgrammeCreate,
    service: ProgrammesService = Depends(get_programmes_service),
) -> Programme:
    """Create a new programme."""
    return service.create_programme(auth.store_id, request)


@router.post("/{programme_id}/members", response_model=ProgrammeMember, status_code=201)
async def add_programme_member(
    programme_id: UUID,
    request: ProgrammeMemberCreate,
    auth: AuthContext,
    service: ProgrammesService = Depends(get_programmes_service),
) -> ProgrammeMember:
    """Add a staff member to a programme."""
    return service.add_member(programme_id, request)
