"""Programmes repository layer."""

from uuid import UUID

from storeops.models import Programme, ProgrammeMember


class ProgrammesRepository:
    """In-memory repository for programmes."""

    def __init__(self) -> None:
        self._programmes: dict[UUID, Programme] = {}
        self._members: dict[UUID, ProgrammeMember] = {}

    def create_programme(self, programme: Programme) -> Programme:
        """Create a new programme."""
        self._programmes[programme.id] = programme
        return programme

    def get_programme_by_id(self, programme_id: UUID) -> Programme | None:
        """Get programme by ID."""
        return self._programmes.get(programme_id)

    def list_by_store(self, store_id: UUID) -> list[Programme]:
        """List programmes by store."""
        return [p for p in self._programmes.values() if p.store_id == store_id]

    def add_member(self, member: ProgrammeMember) -> ProgrammeMember:
        """Add a staff member to a programme."""
        self._members[member.id] = member
        return member

    def get_members(self, programme_id: UUID) -> list[ProgrammeMember]:
        """Get members of a programme."""
        return [m for m in self._members.values() if m.programme_id == programme_id]

    def member_exists(self, programme_id: UUID, staff_id: UUID) -> bool:
        """Check if staff member is already in programme."""
        return any(
            m.programme_id == programme_id and m.staff_id == staff_id
            for m in self._members.values()
        )
