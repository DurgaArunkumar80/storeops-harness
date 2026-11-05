"""Programmes service layer."""

from datetime import datetime
from uuid import UUID, uuid4

from storeops.errors import ConflictError, NotFoundError
from storeops.models import Programme, ProgrammeCreate, ProgrammeMember, ProgrammeMemberCreate
from storeops.programmes.repository import ProgrammesRepository


class ProgrammesService:
    """Business logic for programmes."""

    def __init__(self, repository: ProgrammesRepository) -> None:
        self.repository = repository

    def list_programmes(self, store_id: UUID) -> list[Programme]:
        """List programmes for a store."""
        return self.repository.list_by_store(store_id)

    def create_programme(self, store_id: UUID, request: ProgrammeCreate) -> Programme:
        """Create a new programme."""
        programme = Programme(
            id=uuid4(),
            store_id=store_id,
            name=request.name,
            description=request.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return self.repository.create_programme(programme)

    def add_member(self, programme_id: UUID, request: ProgrammeMemberCreate) -> ProgrammeMember:
        """Add a staff member to a programme."""
        programme = self.repository.get_programme_by_id(programme_id)
        if not programme:
            raise NotFoundError(f"Programme {programme_id} not found")

        if self.repository.member_exists(programme_id, request.staff_id):
            raise ConflictError("Staff member already in programme")

        member = ProgrammeMember(
            id=uuid4(),
            programme_id=programme_id,
            staff_id=request.staff_id,
            joined_at=datetime.utcnow(),
        )
        return self.repository.add_member(member)
