# StoreOps Application Context Skill

**Purpose:** Comprehensive understanding of StoreOps domain, architecture, and business context.

---

## STOREOPS DOMAIN

**Application:** Retail Store Operations Management REST API

**Capstone Nature:** Reference codebase (not for production)

**Core Domain Areas:**
1. **Operational Activities** - daily store tasks and activities
2. **Store Programmes** - multi-staff initiatives and programmes  
3. **Staff Coordination** - team member management
4. **Operational Alerts** - event notifications
5. **Performance Reporting** - store/region metrics

---

## FIVE REQUIRED MODULES

### Activities Module
- **Entity:** Task (Activity in routes, backwards compat)
- **States:** TaskStatus.TODO, IN_PROGRESS, DONE, BLOCKED
- **Priority:** TaskPriority.LOW, MEDIUM, HIGH, CRITICAL
- **Categories:** TaskCategory.RESTOCKING, PLANOGRAM, AUDIT, COMPLIANCE, GENERAL
- **Key Behavior:** Delete restricted to owner or STORE_MANAGER role
- **Endpoints:** 5 (GET list, POST create, GET by ID, PATCH update, DELETE)

### Programmes Module
- **Entity:** Project (Programme in routes, backwards compat)
- **Role:** ProjectRole.STORE_MANAGER, DEPARTMENT_LEAD, ASSOCIATE
- **Members:** ProjectMember with role assignment
- **Scope:** Store-scoped (authenticated store only)
- **Endpoints:** 3 (GET list, POST create, POST add member)

### Staff Module
- **Entity:** User (StaffMember in routes, backwards compat)
- **Role:** StaffRole.REGIONAL_MANAGER, STORE_MANAGER, DEPARTMENT_LEAD, ASSOCIATE
- **Access:** Read-only for other modules
- **No mutations:** Staff is reference data
- **Endpoints:** 2 read-only (GET list, GET by ID)

### Alerts Module
- **Entity:** Notification (Alert in routes, backwards compat)
- **Channel:** NotificationChannel.IN_APP, EMAIL
- **Type:** AlertType.INVENTORY, SLA_BREACH, SHIFT_HANDOVER, ESCALATION
- **Status:** NotificationStatus.PENDING, SENT, READ, FAILED
- **Scope:** User-scoped (user's alerts only)
- **Endpoints:** 1 (GET user's alerts)

### Reports Module
- **Entity:** Report
- **Type:** ReportType.STORE_SUMMARY, REGIONAL_ROLLUP, DEPARTMENT_PERFORMANCE
- **Status:** ReportStatus.PENDING, READY, FAILED
- **Access:** Read-only (never mutates other modules)
- **Endpoints:** Prepared for expansion (basic structure)

---

## ARCHITECTURE REQUIREMENTS

### Three-Layer Pattern (Per Module)
```
Routes Layer          (HTTP handling only)
    ↓
Service Layer         (Business logic, authorization)
    ↓
Repository Layer      (Storage/retrieval only)
```

### Module Boundaries (Hard Rules)
1. **No cross-module repository imports**
   - ✗ activities.service → staff.repository
   - ✓ activities.service → staff.service → staff.repository

2. **Routes must NOT import repositories**
   - ✓ Routes import and inject services
   - ✗ Routes import repositories directly

3. **Repositories are pure storage**
   - No HTTP logic
   - No business logic
   - No cross-module orchestration

4. **Services contain business rules**
   - Authorization logic lives here
   - Domain decisions
   - Read-only cross-module calls permitted
   - All mutations via own repository

5. **Event Bus for side effects**
   - Cross-module side effects go through EventBus
   - Never direct service-to-service mutations
   - Prevents circular dependencies

---

## ERROR HANDLING

### AppError Hierarchy
```python
AppError (base)
├── NotFoundError (404)
├── ValidationError (400)
├── UnauthorizedError (401)
├── ForbiddenError (403)
└── ConflictError (409)
```

### Rules
- No raw `Error` throws in services/routes
- All business/validation errors use AppError subclasses
- HTTP layer auto-maps statusCode
- Infrastructure errors handled centrally

---

## STORAGE

- **Type:** In-memory only (no database)
- **Repositories:** dict-based storage, clear abstractions
- **Persistence:** Session-scoped (resets on app restart)
- **Future:** Easy to replace with ORM/database

---

## TESTING REQUIREMENTS

### Validation Levels
1. **MUST test:** Business behavior, not HTTP status codes
2. **MUST test:** Activity deletion authorization (owner/manager)
3. **MUST test:** Module boundary enforcement (no cross-repo access)
4. **MUST test:** AppError contract (code, message, statusCode)
5. **MUST test:** EventBus event emission where applicable

### Coverage Targets
- Service layer: ≥80%
- Route/controller layer: ≥70%
- Overall: ≥70%

### Current State
- 22 tests passing
- 88% coverage
- Focus: service layer, authorization rules, error handling

---

## AUTHENTICATION CONTEXT

**AuthContext Structure:**
```python
{
    user_id: UUID,
    store_id: UUID,
    role: str (e.g., "store_manager", "staff")
}
```

**Scope Rules:**
- Activities/Programmes: scoped to user's store
- Alerts: scoped to user (no other user's alerts)
- Staff: read-only for all modules
- Reports: aggregates other module data (read-only)

**Capstone Note:** Placeholder auth (tests inject directly). Production harness sprint can add middleware.

---

## QUALITY GATES

**All Must Pass:**
- pytest: 22/22 tests pass
- ruff: 0 linting violations
- mypy: 0 type errors
- coverage: ≥70% overall, ≥80% service layer
- Architecture audit: 0 cross-module boundary violations
- Runtime: Application starts, endpoints accessible

---

## SPECIFICATION REFERENCE

### Nine Base REST Endpoints

**Activities (5)**
1. GET /api/activities - list (with programme, status filters)
2. POST /api/activities - create
3. GET /api/activities/:id - get by ID
4. PATCH /api/activities/:id - update (status, priority, category, assignee)
5. DELETE /api/activities/:id - delete (owner/STORE_MANAGER only)

**Programmes (3)**
6. GET /api/programmes - list (store-scoped)
7. POST /api/programmes - create
8. POST /api/programmes/:id/members - add staff member

**Alerts (1)**
9. GET /api/alerts - get user's alerts

**Additional**
- GET / - root endpoint
- GET /health - health check
- GET /docs - Swagger UI

---

## KEY CONTEXT FOR HARNESS

### Demonstration Feature (Upcoming)
**PATCH /api/activities/bulk-status**
- Purpose: Shift handover bulk status update
- Requirement: Outgoing shift staff update multiple tasks to DONE or BLOCKED
- Handling: Partial failure, audit entries, event emission
- Will be: Generated through completed harness

### Harness Philosophy
- Multi-agent orchestration: Planner → Generator → Evaluator → Monitor
- Deterministic evaluation: Hard gates for architecture/quality
- Autonomous retry loop: Max 3 iterations per sprint
- Escalation path: Clear failure mode for human intervention

---

## LINKS TO OTHER CONTEXT

- See: `architecture-principles.md` - module boundary enforcement
- See: `coding-conventions.md` - code style for StoreOps
- See: `how-to-test.md` - testing approach per layer
- See: `evaluation-criteria.md` - hard gates for harness verdicts
