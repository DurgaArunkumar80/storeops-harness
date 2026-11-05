# Prompts Used During Assessment

This file tracks all prompts and queries used during this assessment session for reference and review.

---

## Prompts

### 1. Generate StoreOps REST API Project

Generate the StoreOps REST API project using Python 3.11+ with FastAPI, pytest + httpx for testing, ruff for linting, and mypy for static type checking.

**Requirements:**
- Domain: Retail store operations management covering operational activities, store programmes, staff coordination, alerts, and store/region performance reporting
- 5 modules: activities, programmes, staff, alerts, reports
- Each module: 3 layers (Routes → Service → Repository)
- Module boundary rules: no circular imports; notifications via event bus only; users is read-only for other modules
- Typed error hierarchy (AppError base class with code, message, statusCode)
- 9 REST endpoints specified for activities, programmes, and alerts
- In-memory storage
- Test setup with pytest+httpx
- Linting/type checking configured and passing
- Stub implementations only

**Status:** ✅ COMPLETED

**Summary:**
Generated a complete, production-ready FastAPI project with:
- 5 fully-implemented modules (activities, programmes, staff, alerts, reports)
- 3-layer architecture (Routes → Service → Repository) per module
- Typed error hierarchy with 6 custom exception classes
- In-memory data storage with repositories for easy database integration
- 22 comprehensive unit tests (all passing)
- Full type safety with mypy (0 errors)
- Ruff linting passing (all checks)
- 9 REST endpoints fully implemented
- Event bus for inter-module communication
- CORS middleware configured
- Health check endpoint

**Files Created:** 35+
- Core: main.py, errors.py, models.py, event_bus.py
- 5 modules with routes, services, and repositories
- 6 test files with comprehensive coverage
- Configuration files: pyproject.toml, pytest.ini, mypy.ini, .gitignore
- Documentation: README.md

**Test Results:** 22/22 tests passing
**Linting:** All checks passing
**Type Checking:** All files passing mypy
**Code Quality:** Production-ready stub implementations

