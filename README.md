# StoreOps REST API

A FastAPI-based REST API for retail store operations management. Covers operational activities, store programmes, staff coordination, alerts, and performance reporting.

## Project Structure

```
src/storeops/
├── main.py                 # FastAPI application entry point
├── errors.py               # Typed error hierarchy
├── models.py               # Shared data models
├── event_bus.py            # Event bus for inter-module communication
├── activities/             # Activities module (5 endpoints)
│   ├── routes.py          # API endpoints
│   ├── service.py         # Business logic
│   └── repository.py      # Data access layer
├── programmes/            # Programmes module (3 endpoints)
│   ├── routes.py
│   ├── service.py
│   └── repository.py
├── staff/                 # Staff module (read-only)
│   ├── routes.py
│   ├── service.py
│   └── repository.py
├── alerts/                # Alerts module (1 endpoint)
│   ├── routes.py
│   ├── service.py
│   └── repository.py
└── reports/               # Reports module
    ├── routes.py
    ├── service.py
    └── repository.py
```

## Features

### 5 Modules with 3-Layer Architecture

Each module follows a strict 3-layer pattern:
- **Routes**: FastAPI endpoints for HTTP handling
- **Service**: Business logic and validation
- **Repository**: Data access and storage

### Module Isolation

- No circular imports between modules
- Inter-module notifications via event bus only
- Staff module is read-only for other modules
- Typed error hierarchy prevents raw Error throws

### 9 REST Endpoints

**Activities** (5 endpoints):
- `GET /api/activities` - List activities with filters
- `POST /api/activities` - Create activity
- `GET /api/activities/{id}` - Get activity
- `PATCH /api/activities/{id}` - Update activity
- `DELETE /api/activities/{id}` - Delete activity (owner/manager only)

**Programmes** (3 endpoints):
- `GET /api/programmes` - List programmes
- `POST /api/programmes` - Create programme
- `POST /api/programmes/{id}/members` - Add staff member

**Alerts** (1 endpoint):
- `GET /api/alerts` - Get user alerts

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Python**: 3.11+
- **Testing**: pytest + httpx
- **Linting**: ruff
- **Type Checking**: mypy
- **Storage**: In-memory (no database required)

## Setup

### Install Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run Linting

```bash
ruff check src/ tests/
```

### Run Type Checking

```bash
mypy src/
```

### Run Application

```bash
uvicorn storeops.main:app --reload
```

## Error Handling

All errors use a typed error hierarchy:

```python
class AppError(Exception):
    code: str
    message: str
    status_code: int
    details: dict
```

Common error types:
- `NotFoundError` (404)
- `ValidationError` (400)
- `UnauthorizedError` (401)
- `ForbiddenError` (403)
- `ConflictError` (409)

## Authentication

Endpoints expect an `AuthContext` with:
- `user_id`: UUID of authenticated user
- `store_id`: UUID of user's store
- `role`: User role (e.g., "store_manager", "staff")

## In-Memory Storage

All data is stored in-memory using Python dictionaries. Repositories provide the data access layer for potential database integration later.

## Testing

- Unit tests for services
- Fixtures for test data
- Test client for endpoint testing
- Async test support
