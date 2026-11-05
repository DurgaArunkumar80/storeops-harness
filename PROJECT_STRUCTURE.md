# StoreOps REST API - Project Structure

## Overview
Complete FastAPI REST API for retail store operations management with 5 modules, 9 endpoints, and production-ready architecture.

## Directory Structure

```
storeops-harness/
├── src/storeops/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   ├── errors.py                        # Typed error hierarchy (6 error classes)
│   ├── models.py                        # Pydantic models for all entities
│   ├── event_bus.py                     # Event bus for inter-module communication
│   │
│   ├── activities/                      # Activities Module (5 endpoints)
│   │   ├── __init__.py
│   │   ├── routes.py                    # 5 HTTP endpoints
│   │   ├── service.py                   # Business logic + access control
│   │   └── repository.py                # In-memory data access layer
│   │
│   ├── programmes/                      # Programmes Module (3 endpoints)
│   │   ├── __init__.py
│   │   ├── routes.py                    # 3 HTTP endpoints
│   │   ├── service.py                   # Business logic
│   │   └── repository.py                # Data access + member management
│   │
│   ├── staff/                           # Staff Module (2 read-only endpoints)
│   │   ├── __init__.py
│   │   ├── routes.py                    # 2 read-only HTTP endpoints
│   │   ├── service.py                   # Read-only access service
│   │   └── repository.py                # In-memory storage (read-only)
│   │
│   ├── alerts/                          # Alerts Module (1 endpoint)
│   │   ├── __init__.py
│   │   ├── routes.py                    # 1 HTTP endpoint
│   │   ├── service.py                   # Business logic
│   │   └── repository.py                # Alert storage
│   │
│   └── reports/                         # Reports Module
│       ├── __init__.py
│       ├── routes.py                    # Report endpoints
│       ├── service.py                   # Report generation logic
│       └── repository.py                # Report storage
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures and configuration
│   ├── test_activities.py               # 9 tests for activities module
│   ├── test_programmes.py               # 5 tests for programmes module
│   ├── test_staff.py                    # 3 tests for staff module
│   ├── test_alerts.py                   # 3 tests for alerts module
│   └── test_reports.py                  # 2 tests for reports module
│
├── pyproject.toml                       # Project configuration + dependencies
├── pytest.ini                           # Pytest configuration
├── mypy.ini                             # Type checking configuration
├── .gitignore                           # Git ignore rules
├── README.md                            # Project documentation
├── PROJECT_STRUCTURE.md                 # This file
└── PROMPTS.md                           # Prompt history and status

```

## Module Architecture

### Layer Pattern (Repeated for each module)
```
HTTP Request
    ↓
[Routes Layer]  - HTTP handlers, dependency injection
    ↓
[Service Layer] - Business logic, validation, access control
    ↓
[Repository]    - Data access, storage operations
    ↓
In-Memory Storage
```

## REST Endpoints (9 Total)

### Activities Module (5 endpoints)
- `GET /api/activities` - List activities (with filters)
- `POST /api/activities` - Create activity
- `GET /api/activities/{id}` - Get activity by ID
- `PATCH /api/activities/{id}` - Update activity
- `DELETE /api/activities/{id}` - Delete activity (owner/manager only)

### Programmes Module (3 endpoints)
- `GET /api/programmes` - List programmes
- `POST /api/programmes` - Create programme
- `POST /api/programmes/{id}/members` - Add staff member

### Alerts Module (1 endpoint)
- `GET /api/alerts` - Get user alerts

### Staff Module (2 read-only endpoints)
- `GET /api/staff` - List staff
- `GET /api/staff/{id}` - Get staff member

### Reports Module
- `GET /api/reports` - Get store/region reports

## Data Models

### Core Models
- `Activity` - Operational activity with status, priority, category
- `Programme` - Store programme with members
- `StaffMember` - Staff member (read-only reference)
- `Alert` - Operational alert for users
- `Report` - Store/region performance report

### Enums
- `ActivityStatus`: pending, in_progress, completed, cancelled
- `ActivityPriority`: low, medium, high, urgent

### Error Classes (Typed Hierarchy)
- `AppError` - Base class with code, message, statusCode
- `NotFoundError` (404)
- `ValidationError` (400)
- `UnauthorizedError` (401)
- `ForbiddenError` (403)
- `ConflictError` (409)

## Key Features

✅ **Typed Error Hierarchy** - No raw Error throws; all errors typed with status codes
✅ **Access Control** - Activity deletion restricted to owner or store manager
✅ **Module Isolation** - No circular imports; event bus for notifications
✅ **Type Safety** - 100% mypy passing; strict mode enabled
✅ **Linting** - All ruff checks passing
✅ **Testing** - 22 comprehensive unit tests covering all modules
✅ **In-Memory Storage** - Easy to replace with database layer
✅ **FastAPI** - Modern async framework with automatic API docs
✅ **Dependency Injection** - Clean service injection pattern
✅ **Pydantic Validation** - Automatic request/response validation

## Configuration

### Python Version
- Required: Python 3.11+
- Tested with: Python 3.14.3

### Dependencies
- FastAPI 0.104+
- Uvicorn 0.24+
- Pydantic 2.0+
- Pytest 7.4+ (dev)
- httpx 0.25+ (dev)
- Ruff 0.1+ (dev)
- Mypy 1.6+ (dev)

## Setup & Running

### Install
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest              # All tests
pytest -v          # Verbose
pytest tests/test_activities.py  # Specific module
```

### Run Linting
```bash
ruff check src/ tests/
```

### Run Type Checking
```bash
mypy src/
```

### Run Server
```bash
uvicorn storeops.main:app --reload
# API docs: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| Activities | 9 | ✅ Passing |
| Programmes | 5 | ✅ Passing |
| Alerts | 3 | ✅ Passing |
| Staff | 3 | ✅ Passing |
| Reports | 2 | ✅ Passing |
| **Total** | **22** | **✅ All Passing** |

## Design Patterns

### Dependency Injection
Services are injected into routes via FastAPI `Depends()`:
```python
async def endpoint(service: MyService = Depends(get_service)):
    ...
```

### Repository Pattern
Clean separation of data access:
```python
class MyRepository:
    def create(self, entity) -> Entity
    def get_by_id(self, id) -> Entity | None
    def list_all(self) -> list[Entity]
```

### Service Layer
Business logic separated from HTTP handling:
```python
class MyService:
    def __init__(self, repository: MyRepository):
        self.repository = repository
    
    def create(self, user_id, request) -> Entity:
        # validation, access control, etc.
```

### Error Handling
Typed exceptions with automatic HTTP status mapping:
```python
raise NotFoundError("Resource not found")  # → 404
raise ValidationError("Invalid data")      # → 400
raise ForbiddenError("No permission")      # → 403
```

## Next Steps for Production

1. **Database Integration** - Replace repositories with SQLAlchemy ORM
2. **Authentication** - Add JWT token validation to AuthContext
3. **Logging** - Add structured logging across all layers
4. **Monitoring** - Add metrics/tracing with OpenTelemetry
5. **API Documentation** - Enhance with additional OpenAPI metadata
6. **Rate Limiting** - Add rate limiter middleware
7. **CORS** - Restrict origins in production
8. **Caching** - Add Redis caching layer

## Quality Metrics

- **Type Coverage**: 100% (mypy passing)
- **Linting**: 100% (ruff passing)
- **Test Coverage**: Comprehensive unit tests
- **Documentation**: README + code comments
- **Architecture**: Clean 3-layer pattern per module
