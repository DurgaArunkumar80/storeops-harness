"""Staff API routes (read-only)."""

from uuid import UUID

from fastapi import APIRouter, Depends

from storeops.models import AuthContext, StaffMember
from storeops.staff.repository import StaffRepository
from storeops.staff.service import StaffService

router = APIRouter(prefix="/api/staff", tags=["staff"])

# In-memory repositories
_staff_repo = StaffRepository()
_staff_service = StaffService(_staff_repo)


def get_staff_service() -> StaffService:
    """Dependency injection for staff service."""
    return _staff_service


@router.get("/{staff_id}", response_model=StaffMember)
async def get_staff_member(
    staff_id: UUID,
    auth: AuthContext,
    service: StaffService = Depends(get_staff_service),
) -> StaffMember:
    """Get a staff member by ID."""
    return service.get_staff_member(staff_id)


@router.get("", response_model=list[StaffMember])
async def list_staff(
    auth: AuthContext,
    service: StaffService = Depends(get_staff_service),
) -> list[StaffMember]:
    """List staff members for the store."""
    return service.list_staff(auth.store_id)
