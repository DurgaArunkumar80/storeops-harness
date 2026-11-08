# StoreOps Architecture Principles Skill

**Purpose:** Enforce module boundaries and architectural constraints specific to StoreOps.

---

## GOLDEN RULE: ZERO CROSS-MODULE REPOSITORY ACCESS

### The Prohibition
```python
# ✗ FORBIDDEN - direct repository access
activities/service.py
    ↓
    from storeops.staff.repository import StaffRepository

# ✓ CORRECT - service-layer access
activities/service.py
    ↓
    from storeops.staff.service import StaffService
    ↓
    StaffService.get_staff_member(id)
    ↓
    staff/service.py
    ↓
    staff/repository.py
```

### Why This Matters
- Prevents tight coupling between modules
- Enables clean feature isolation
- Allows independent testing per module
- Makes module replacement possible
- Enforces clear API contracts

### Detection
```bash
# Search for violations
grep -r "from storeops\.[a-z]*\.repository import" src/storeops/*/service.py
grep -r "from storeops\.[a-z]*\.repository import" src/storeops/*/routes.py

# Both should return ZERO results
```

---

## LAYER SEPARATION RULES

### Routes/Controllers
**Allowed:**
- HTTP request/response handling
- Request parsing and validation
- Auth context extraction
- Service invocation
- Response mapping

**Forbidden:**
- Repository access
- Business logic
- Authorization decisions
- Cross-module orchestration

**Correct Pattern:**
```python
@router.get("/api/resource/{id}")
async def get_resource(
    id: UUID,
    auth: AuthContext,
    service: MyService = Depends(get_service),  # Injected
) -> ResourceModel:
    return service.get_resource(id)
```

### Service Layer
**Allowed:**
- Business rules implementation
- Authorization decisions
- Domain validations
- Own repository calls
- Read-only cross-module service calls

**Forbidden:**
- HTTP logic
- Repository access from other modules
- Direct cross-module side effects (use EventBus)
- Raw Error throws

**Correct Pattern:**
```python
class MyService:
    def delete_resource(self, resource_id: UUID, user_id: UUID, role: str):
        resource = self.repository.get_by_id(resource_id)
        if not resource:
            raise NotFoundError("Resource not found")
        
        # Authorization logic
        if resource.owner_id != user_id and role != "admin":
            raise ForbiddenError("Cannot delete")
        
        # Domain decision
        self.repository.delete(resource_id)
        
        # Cross-module read OK:
        # staff_info = self.staff_service.get_staff(user_id)
```

### Repository Layer
**Allowed:**
- CRUD operations
- Query filtering
- Storage implementation
- Data retrieval

**Forbidden:**
- HTTP logic
- Business rules
- Cross-module access
- External service calls

**Correct Pattern:**
```python
class MyRepository:
    def create(self, entity: Entity) -> Entity:
        self._store[entity.id] = entity
        return entity
    
    def get_by_id(self, entity_id: UUID) -> Entity | None:
        return self._store.get(entity_id)
    
    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False
```

---

## MODULE BOUNDARY RULES

### No Circular Dependencies
```python
# ✗ FORBIDDEN
activities → programmes
programmes → activities

# ✓ CORRECT (one direction only if needed)
activities → programmes (read-only lookup OK)
programmes → activities (NO access back)
```

### Read-Only Staff Access
```python
# ✓ All modules can read staff
activities.service → staff.service → staff.repository

# ✗ Only staff module can mutate
activities/repository → staff/repository (FORBIDDEN)
```

### Reports Read-Only
```python
# ✓ Reports can read all modules
reports.service → activities.service
reports.service → programmes.service
reports.service → staff.service

# ✗ Reports cannot mutate
reports/repository ← activities/repository (FORBIDDEN)
reports.service.create_mutation() (FORBIDDEN)
```

---

## ERROR HIERARCHY ENFORCEMENT

### Requirement
```python
# ✗ FORBIDDEN
raise Error("Something went wrong")
raise Exception("Not found")

# ✓ REQUIRED
raise NotFoundError("Resource not found")
raise ValidationError("Invalid input")
raise ForbiddenError("No permission")
raise ConflictError("Resource conflict")
```

### In Routes
```python
# Routes catch AppError and map automatically
try:
    return service.delete_resource(id)
except AppError as e:
    raise HTTPException(
        status_code=e.status_code,
        detail=e.to_dict()
    )
```

### In Services
```python
# Services raise typed errors
if not found:
    raise NotFoundError(f"Resource {id} not found")

if not authorized:
    raise ForbiddenError("Only owner can delete")

if invalid:
    raise ValidationError("Invalid enum value")
```

---

## EVENT BUS ARCHITECTURE

### Cross-Module Side Effects
```python
# ✗ FORBIDDEN (direct mutation)
activities/service.py → alerts/service.py.create_alert()

# ✓ CORRECT (event bus)
activities/service.py
    ↓
    event_bus.publish("activity_created", {activity_id: ...})
    ↓
    alerts/service.py (subscribed)
    ↓
    creates alert asynchronously
```

### Event Types for StoreOps
- `activity_created` - new activity created
- `activity_completed` - activity marked done
- `activity_blocked` - activity blocked
- `programme_created` - new programme
- `member_added` - staff added to programme
- `alert_triggered` - alert threshold reached

### Prevention of Circular Dependencies
```python
# Alerts listen to activities
activities.service.create() → event_bus.publish("activity_created")
event_bus → alerts.service.subscribe("activity_created")

# Activities must NOT listen to alerts
// activities.service never subscribes to alert events
```

---

## TESTING BOUNDARY ENFORCEMENT

### Unit Test: No Cross-Module Imports
```python
# In test setup, verify no prohibited imports
def test_module_boundaries():
    """Verify no service imports other modules' repositories."""
    import ast
    import os
    
    for service_file in glob("src/storeops/*/service.py"):
        with open(service_file) as f:
            tree = ast.parse(f.read())
        
        for import_node in ast.walk(tree):
            if isinstance(import_node, ast.ImportFrom):
                if ".repository import" in import_node.module:
                    module = service_file.split("/")[2]
                    other = import_node.module.split(".")[1]
                    assert module == other, \
                        f"{module}.service imports {other}.repository"
```

### Integration Test: Module Independence
```python
# Each module's tests should NOT depend on other modules' implementations
def test_activities_module_independent():
    """Activities module works without staff module data."""
    repo = ActivitiesRepository()
    service = ActivitiesService(repo)
    
    # Create activity without any staff module setup
    activity = service.create_activity(
        store_id=uuid4(),
        user_id=uuid4(),
        request=ActivityCreate(...)
    )
    assert activity.id is not None  # Works standalone
```

---

## ARCHITECTURAL AUDIT CHECKLIST

**Before marking code complete:**

- [ ] No cross-module repository imports (`grep` verification)
- [ ] Routes don't import repositories (code review)
- [ ] No raw Error throws in services (code review)
- [ ] All AppErrors have proper status codes (type checking)
- [ ] Services use own repository only (imports audit)
- [ ] Event bus used for cross-module side effects (code review)
- [ ] Reports module is read-only (no mutations)
- [ ] No circular module dependencies (import analysis)
- [ ] Staff module accessed read-only only (code review)
- [ ] All tests pass with coverage thresholds (metrics)

---

## VIOLATION RESPONSE

If violation detected:

1. **Identify the violation type**
   - Cross-module repository import
   - Route importing repository
   - Raw Error throw
   - Circular dependency
   - Reports mutation

2. **Locate the violation**
   - File path
   - Line number
   - Exact code

3. **Apply corrective action**
   - Add service layer intermediary
   - Remove direct repository access
   - Replace Error with AppError subclass
   - Restructure to eliminate circular dependency
   - Use EventBus for side effects

4. **Verify fix**
   - Run architecture audit again
   - Verify tests still pass
   - Type checking passes
   - Linting passes

---

## RELATED SKILLS

- `app-context.md` - Understand module responsibilities
- `how-to-test.md` - Verify boundaries in tests
- `evaluation-criteria.md` - Hard gate: Module boundary audit
