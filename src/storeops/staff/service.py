"""Staff service layer."""

from uuid import UUID

from storeops.errors import NotFoundError
from storeops.models import StaffMember
from storeops.staff.repository import StaffRepository


class StaffService:
    """Business logic for staff members. Read-only access for other modules."""

    def __init__(self, repository: StaffRepository) -> None:
        self.repository = repository

    def get_staff_member(self, staff_id: UUID) -> StaffMember:
        """Get staff member by ID."""
        staff = self.repository.get_by_id(staff_id)
        if not staff:
            raise NotFoundError(f"Staff member {staff_id} not found")
        return staff

    def list_staff(self, store_id: UUID) -> list[StaffMember]:
        """List staff members by store."""
        return self.repository.list_by_store(store_id)
