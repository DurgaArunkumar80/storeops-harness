# StoreOps Testing Skill

**Purpose:** Testing approach for StoreOps modules per layer.

---

## SERVICE LAYER TESTING (≥80% coverage target)

### Behavior-Based Tests
```python
def test_create_task(service: TaskService):
    """Test task creation."""
    task = service.create_task(
        store_id=uuid4(),
        user_id=uuid4(),
        request=TaskCreate(title="Test", category=TaskCategory.AUDIT),
    )
    assert task.title == "Test"
    assert task.status == TaskStatus.TODO

def test_task_filtering(service: TaskService):
    """Test filtering by status."""
    service.create_task(..., status=TaskStatus.TODO)
    service.create_task(..., status=TaskStatus.IN_PROGRESS)
    
    results = service.list_tasks(store_id, status=TaskStatus.TODO)
    assert len(results) == 1
```

### Authorization Tests
```python
def test_delete_owner_allowed(service: TaskService):
    """Owner can delete task."""
    task = service.create_task(..., owner_id=user_id)
    service.delete_task(task.id, user_id, "staff")  # No exception

def test_delete_manager_allowed(service: TaskService):
    """Manager can delete any task."""
    task = service.create_task(..., owner_id=owner_id)
    service.delete_task(task.id, manager_id, "store_manager")  # No exception

def test_delete_unauthorized(service: TaskService):
    """Non-owner cannot delete."""
    task = service.create_task(..., owner_id=owner_id)
    with pytest.raises(ForbiddenError):
        service.delete_task(task.id, other_user_id, "staff")
```

### Error Tests
```python
def test_not_found_error(service: TaskService):
    """Proper NotFoundError on missing resource."""
    with pytest.raises(NotFoundError) as exc:
        service.get_task(uuid4())
    assert exc.value.status_code == 404
```

---

## ROUTE LAYER TESTING (≥70% coverage target)

### Endpoint Tests
```python
def test_get_tasks_endpoint(client: TestClient, auth: AuthContext):
    """Test GET /api/tasks endpoint."""
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth.token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Authentication Tests
```python
def test_endpoint_requires_auth(client: TestClient):
    """Endpoints require authentication."""
    response = client.get("/api/tasks")
    assert response.status_code == 401
```

---

## MODULE BOUNDARY TESTS

### Cross-Module Isolation
```python
def test_activities_independent(activities_repo: ActivitiesRepository):
    """Activities work without staff module."""
    repo = activities_repo
    service = ActivitiesService(repo)
    
    # Create without any staff setup
    task = service.create_task(uuid4(), uuid4(), TaskCreate(...))
    assert task.id is not None
```

### Read-Only Access
```python
def test_staff_read_only(activities_service, staff_service):
    """Activities can read staff but not mutate."""
    # Read OK
    staff = staff_service.get_staff_member(staff_id)
    assert staff is not None
    
    # Mutation forbidden (type checking prevents this)
    # staff_service.delete_staff(staff_id)  # Type error at compile time
```

---

## ENUM TESTS

### Valid Enum Values
```python
def test_task_status_enum_values():
    """TaskStatus has correct values."""
    assert TaskStatus.TODO.value == "todo"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.DONE.value == "done"
    assert TaskStatus.BLOCKED.value == "blocked"

def test_invalid_enum_rejected():
    """Invalid enum values rejected."""
    with pytest.raises(ValidationError):
        TaskCreate(title="Test", status="invalid_status")
```

---

## FIXTURE PATTERNS

### Service Fixture
```python
@pytest.fixture
def task_service() -> TaskService:
    """Create task service for testing."""
    repo = TaskRepository()
    return TaskService(repo)
```

### Sample Data Fixture
```python
@pytest.fixture
def sample_task() -> Task:
    """Create sample task."""
    return Task(
        id=uuid4(),
        store_id=uuid4(),
        title="Test Task",
        status=TaskStatus.TODO,
        category=TaskCategory.AUDIT,
        owner_id=uuid4(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
```

---

## COVERAGE TARGETS

| Layer | Target | Current | Status |
|-------|--------|---------|--------|
| Service | ≥80% | 87-100% | ✅ PASS |
| Routes | ≥70% | 77-83% | ✅ PASS |
| Models | ≥60% | 100% | ✅ PASS |
| Overall | ≥70% | 88% | ✅ PASS |

---

## TEST COMMAND REFERENCE

```bash
# Run all tests
pytest -q

# Run specific module tests
pytest tests/test_activities.py -v

# Run with coverage
pytest --cov=src/storeops -q

# Run and show missing lines
pytest --cov=src/storeops --cov-report=term-missing -q
```
