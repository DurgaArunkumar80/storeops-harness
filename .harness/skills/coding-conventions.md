# StoreOps Coding Conventions Skill

**Purpose:** Consistent code style, patterns, and conventions for StoreOps implementation.

---

## PYTHON CODE STYLE

### Imports
```python
# Organize in three groups, separated by blank lines
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from storeops.models import Task
from storeops.errors import NotFoundError
```

### Type Hints (Required)
```python
# ALL functions must have complete type hints
def get_resource(resource_id: UUID) -> Resource | None:
    ...

# Union types with | (Python 3.10+)
def update_status(status: TaskStatus | None) -> Resource:
    ...

# Collections
def list_resources(filters: dict[str, Any]) -> list[Resource]:
    ...
```

### Docstrings (Short)
```python
# One-line docstrings for simple functions
def get_resource(resource_id: UUID) -> Resource:
    """Get resource by ID."""
    ...

# Multi-line only for complex logic
def delete_resource(id: UUID, user_id: UUID, role: str) -> None:
    """Delete resource if authorized.
    
    Raises ForbiddenError if user lacks permission.
    """
    ...
```

### Error Handling
```python
# ALWAYS use AppError subclasses, never raw Error
if not found:
    raise NotFoundError(f"Resource {id} not found")

if not authorized:
    raise ForbiddenError("Only owner can delete")

if invalid:
    raise ValidationError("Invalid input")

if conflict:
    raise ConflictError("Resource already exists")
```

### Naming Conventions
```python
# Classes: PascalCase
class TaskRepository: pass

# Functions/methods: snake_case
def get_resource_by_id(): pass

# Constants: UPPER_SNAKE_CASE
MAX_BATCH_SIZE = 100

# Private: _leading_underscore
self._internal_state = {}

# Enums: PascalCase with snake_case values
class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
```

---

## LAYER-SPECIFIC PATTERNS

### Routes Layer
```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/resources", tags=["resources"])

def get_service() -> MyService:
    """Dependency injection."""
    return MyService(MyRepository())

@router.get("/{id}")
async def get_resource(
    id: UUID,
    auth: AuthContext,
    service: MyService = Depends(get_service),
) -> ResourceModel:
    """Get resource by ID."""
    return service.get_resource(id)
```

### Service Layer
```python
class MyService:
    def __init__(self, repository: MyRepository) -> None:
        self.repository = repository
    
    def get_resource(self, resource_id: UUID) -> Resource:
        """Get resource by ID."""
        resource = self.repository.get_by_id(resource_id)
        if not resource:
            raise NotFoundError(f"Resource {resource_id} not found")
        return resource
```

### Repository Layer
```python
class MyRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, Resource] = {}
    
    def create(self, resource: Resource) -> Resource:
        """Create and store resource."""
        self._store[resource.id] = resource
        return resource
    
    def get_by_id(self, resource_id: UUID) -> Resource | None:
        """Get resource by ID."""
        return self._store.get(resource_id)
```

---

## TESTING PATTERNS

### Service Tests
```python
@pytest.fixture
def service() -> MyService:
    """Create service for testing."""
    repo = MyRepository()
    return MyService(repo)

def test_get_resource(service: MyService) -> None:
    """Test resource retrieval."""
    resource = service.create_resource(...)
    result = service.get_resource(resource.id)
    assert result.id == resource.id
```

### Authorization Tests
```python
def test_delete_authorized(service: MyService) -> None:
    """Test owner can delete."""
    resource = service.create_resource(owner_id=user_id)
    service.delete_resource(resource.id, user_id, "staff")
    # Should not raise

def test_delete_unauthorized(service: MyService) -> None:
    """Test non-owner cannot delete."""
    resource = service.create_resource(owner_id=owner_id)
    with pytest.raises(ForbiddenError):
        service.delete_resource(resource.id, other_user_id, "staff")
```

---

## ENUM PATTERNS

### Definition
```python
class TaskStatus(StrEnum):
    """Task status - exactly matches spec."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
```

### Usage
```python
# In models
status: TaskStatus = TaskStatus.TODO

# In requests
update_request = TaskUpdate(status=TaskStatus.DONE)

# In filtering
tasks = [t for t in tasks if t.status == TaskStatus.TODO]
```

---

## MODEL PATTERNS

### Pydantic Model
```python
from pydantic import BaseModel, Field

class Task(BaseModel):
    """Task entity."""
    id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    """Create task request."""
    title: str = Field(..., min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.TODO
```

---

## DEPENDENCIES ACROSS MODULES

### Read-Only Cross-Module Access
```python
# activities/service.py - OK to call other service
class ActivitiesService:
    def __init__(
        self,
        repo: ActivitiesRepository,
        staff_service: StaffService,  # Read-only injection
    ) -> None:
        self.repository = repo
        self.staff_service = staff_service
    
    def assign_task(self, task_id: UUID, staff_id: UUID) -> None:
        # Verify staff exists (read-only)
        staff = self.staff_service.get_staff_member(staff_id)
        # Update task (own repository)
        self.repository.update(task_id, {"assignee_id": staff_id})
```

### Event Bus for Side Effects
```python
# activities/service.py - publish event
from storeops.event_bus import event_bus

def complete_task(self, task_id: UUID) -> None:
    task = self.repository.get_by_id(task_id)
    self.repository.update(task_id, {"status": TaskStatus.DONE})
    
    # Notify other modules via event bus
    event_bus.publish("task_completed", {
        "task_id": str(task_id),
        "timestamp": datetime.utcnow().isoformat(),
    })

# alerts/service.py - subscribe to event
event_bus.subscribe("task_completed", handle_task_completed)
```

---

## LINTING & TYPE CHECKING

### Ruff Configuration
- Line length: 100 characters
- Target Python: 3.11+
- Ignore E501 (line too long)

### Mypy Configuration
- `disallow_untyped_defs = true` (all functions typed)
- `strict_equality = true`
- `check_untyped_defs = true`

### Pre-Commit
```bash
# Always run before committing
ruff check src/ tests/
mypy src/
pytest -q
```

---

## COMMIT MESSAGE FORMAT

```
<type>: <subject>

<body (optional)>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types
- `feat:` - new feature
- `fix:` - bug fix
- `refactor:` - code restructure
- `test:` - test additions/changes
- `docs:` - documentation
- `chore:` - maintenance

### Examples
```
feat: add bulk status update endpoint

Implements PATCH /api/activities/bulk-status for shift handover.
Supports partial failure with audit trail.

test: increase activities service coverage to 85%

docs: update API documentation with new enums
```
