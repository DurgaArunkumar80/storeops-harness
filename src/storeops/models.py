"""Shared data models for StoreOps API."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityStatus(StrEnum):
    """Activity status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityPriority(StrEnum):
    """Activity priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Activity(BaseModel):
    """Activity model."""

    id: UUID
    store_id: UUID
    programme_id: UUID | None = None
    title: str
    description: str | None = None
    status: ActivityStatus = ActivityStatus.PENDING
    priority: ActivityPriority = ActivityPriority.MEDIUM
    category: str
    assignee_id: UUID | None = None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class ActivityCreate(BaseModel):
    """Create activity request."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    programme_id: UUID | None = None
    category: str = Field(..., min_length=1, max_length=50)
    priority: ActivityPriority = ActivityPriority.MEDIUM
    assignee_id: UUID | None = None


class ActivityUpdate(BaseModel):
    """Update activity request."""

    status: ActivityStatus | None = None
    priority: ActivityPriority | None = None
    category: str | None = None
    assignee_id: UUID | None = None


class Programme(BaseModel):
    """Programme model."""

    id: UUID
    store_id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProgrammeCreate(BaseModel):
    """Create programme request."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


class ProgrammeMember(BaseModel):
    """Programme member model."""

    id: UUID
    programme_id: UUID
    staff_id: UUID
    joined_at: datetime


class ProgrammeMemberCreate(BaseModel):
    """Add member to programme request."""

    staff_id: UUID


class StaffMember(BaseModel):
    """Staff member model."""

    id: UUID
    store_id: UUID
    name: str
    email: str
    role: str
    created_at: datetime


class Alert(BaseModel):
    """Alert model."""

    id: UUID
    user_id: UUID
    title: str
    message: str
    severity: str
    read: bool
    created_at: datetime


class Report(BaseModel):
    """Store/Region performance report model."""

    id: UUID
    store_id: UUID | None = None
    region_id: UUID | None = None
    report_type: str
    data: dict[str, Any]
    created_at: datetime


# Context models for authenticated requests
class AuthContext(BaseModel):
    """Authentication context for requests."""

    user_id: UUID
    store_id: UUID
    role: str
