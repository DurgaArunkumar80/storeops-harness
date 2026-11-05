"""Staff repository layer."""

from uuid import UUID

from storeops.models import StaffMember


class StaffRepository:
    """Read-only in-memory repository for staff members."""

    def __init__(self) -> None:
        self._staff: dict[UUID, StaffMember] = {}

    def get_by_id(self, staff_id: UUID) -> StaffMember | None:
        """Get staff member by ID."""
        return self._staff.get(staff_id)

    def list_by_store(self, store_id: UUID) -> list[StaffMember]:
        """List staff members by store."""
        return [s for s in self._staff.values() if s.store_id == store_id]
