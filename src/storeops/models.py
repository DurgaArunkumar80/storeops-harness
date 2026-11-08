"""Shared data models for StoreOps API."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

# =====================================================================
# ACTIVITIES DOMAIN TYPES
# =====================================================================


class TaskStatus(StrEnum):
    """Task status - spec: TODO, IN_PROGRESS, DONE, BLOCKED."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(StrEnum):
    """Task priority - spec: LOW, MEDIUM, HIGH, CRITICAL."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCategory(StrEnum):
    """Task category - spec: RESTOCKING, PLANOGRAM, AUDIT, COMPLIANCE, GENERAL."""

    RESTOCKING = "restocking"
    PLANOGRAM = "planogram"
    AUDIT = "audit"
    COMPLIANCE = "compliance"
    GENERAL = "general"


# Backwards compatibility aliases
ActivityStatus = TaskStatus
ActivityPriority = TaskPriority


class Task(BaseModel):
    """Task (Activity) model - operational activity in store."""

    id: UUID
    store_id: UUID
    programme_id: UUID | None = None
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory
    assignee_id: UUID | None = None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    """Create task request."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    programme_id: UUID | None = None
    category: TaskCategory
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: UUID | None = None


class TaskUpdate(BaseModel):
    """Update task request."""

    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    category: TaskCategory | None = None
    assignee_id: UUID | None = None


# Backwards compatibility aliases
Activity = Task
ActivityCreate = TaskCreate
ActivityUpdate = TaskUpdate


# =====================================================================
# PROGRAMMES DOMAIN TYPES
# =====================================================================


class ProjectRole(StrEnum):
    """Project/Programme role - spec: STORE_MANAGER, DEPARTMENT_LEAD, ASSOCIATE."""

    STORE_MANAGER = "store_manager"
    DEPARTMENT_LEAD = "department_lead"
    ASSOCIATE = "associate"


class Project(BaseModel):
    """Project (Programme) model - store programme/initiative."""

    id: UUID
    store_id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    """Create project request."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


class ProjectMember(BaseModel):
    """Project member model."""

    id: UUID
    programme_id: UUID
    staff_id: UUID
    role: ProjectRole = ProjectRole.ASSOCIATE
    joined_at: datetime


class ProjectMemberCreate(BaseModel):
    """Add member to project request."""

    staff_id: UUID
    role: ProjectRole = ProjectRole.ASSOCIATE


# Backwards compatibility aliases
Programme = Project
ProgrammeCreate = ProjectCreate
ProgrammeMember = ProjectMember
ProgrammeMemberCreate = ProjectMemberCreate


# =====================================================================
# STAFF DOMAIN TYPES
# =====================================================================


class StaffRole(StrEnum):
    """Staff role - spec: REGIONAL_MANAGER, STORE_MANAGER, DEPARTMENT_LEAD, ASSOCIATE."""

    REGIONAL_MANAGER = "regional_manager"
    STORE_MANAGER = "store_manager"
    DEPARTMENT_LEAD = "department_lead"
    ASSOCIATE = "associate"


class User(BaseModel):
    """User model - staff member."""

    id: UUID
    store_id: UUID
    name: str
    email: str
    role: StaffRole
    created_at: datetime


class UserProfile(BaseModel):
    """User profile extended information."""

    user_id: UUID
    department: str | None = None
    phone: str | None = None
    active: bool = True


class AuthToken(BaseModel):
    """Authentication token model."""

    token: str
    user_id: UUID
    issued_at: datetime
    expires_at: datetime


# Backwards compatibility alias
StaffMember = User


# =====================================================================
# ALERTS DOMAIN TYPES
# =====================================================================


class NotificationChannel(StrEnum):
    """Notification delivery channel - spec: IN_APP, EMAIL."""

    IN_APP = "in_app"
    EMAIL = "email"


class NotificationStatus(StrEnum):
    """Notification status - lifecycle states."""

    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"


class AlertType(StrEnum):
    """Alert type - spec: INVENTORY, SLA_BREACH, SHIFT_HANDOVER, ESCALATION."""

    INVENTORY = "inventory"
    SLA_BREACH = "sla_breach"
    SHIFT_HANDOVER = "shift_handover"
    ESCALATION = "escalation"


class Notification(BaseModel):
    """Notification (Alert) model - operational alert."""

    id: UUID
    user_id: UUID
    title: str
    message: str
    alert_type: AlertType
    channel: NotificationChannel = NotificationChannel.IN_APP
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime
    read_at: datetime | None = None


# Backwards compatibility alias
Alert = Notification


# =====================================================================
# REPORTS DOMAIN TYPES
# =====================================================================


class ReportType(StrEnum):
    """Report type - spec: STORE_SUMMARY, REGIONAL_ROLLUP, DEPARTMENT_PERFORMANCE."""

    STORE_SUMMARY = "store_summary"
    REGIONAL_ROLLUP = "regional_rollup"
    DEPARTMENT_PERFORMANCE = "department_performance"


class ReportStatus(StrEnum):
    """Report generation status - spec: PENDING, READY, FAILED."""

    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class Report(BaseModel):
    """Report model - store/region performance report."""

    id: UUID
    store_id: UUID | None = None
    region_id: UUID | None = None
    report_type: ReportType
    status: ReportStatus = ReportStatus.PENDING
    data: dict[str, Any]
    created_at: datetime
    completed_at: datetime | None = None


# =====================================================================
# BULK OPERATIONS
# =====================================================================


class BulkUpdateDetail(BaseModel):
    """Individual activity result in bulk update."""

    activity_id: UUID
    success: bool
    status: TaskStatus | None = None
    error: str | None = None
    status_code: int | None = None


class BulkStatusUpdateRequest(BaseModel):
    """Bulk status update request."""

    activity_ids: list[UUID]
    status: TaskStatus
    reason: str | None = Field(None, max_length=500)


class BulkStatusUpdateResponse(BaseModel):
    """Bulk status update response."""

    updated: list[BulkUpdateDetail]
    failed: list[BulkUpdateDetail]
    summary: dict[str, int]


# Context models for authenticated requests
class AuthContext(BaseModel):
    """Authentication context for requests."""

    user_id: UUID
    store_id: UUID
    role: str
