# Sprint 2 Contract: Shift Handover Bulk Status Update

**Sprint ID:** 2  
**Feature ID:** STOREOPS-BULK-001  
**Feature Name:** PATCH /api/activities/bulk-status endpoint  

**STATUS: AWAITING APPROVAL**

---

## SPRINT COMMITMENT

### Story Points: 8

**Estimate Rationale:**
- Models: 1 point (2 simple Pydantic models)
- Route handler: 2 points (HTTP layer, status code routing)
- Service method: 3 points (validation, iteration, partial failure logic)
- Tests (unit + integration): 2 points (10 tests total)

**Complexity Factors:**
- Partial failure handling (moderate)
- Multi-status HTTP response routing (moderate)
- Audit trail verification (low - existing mechanism)
- No cross-module dependencies (low complexity)

---

## ACCEPTANCE CRITERIA CHECKLIST

```
Sprint 2 must deliver ALL of these:

IMPLEMENTATION:
[ ] BulkStatusUpdateRequest model (activity_ids: list[int], status: str)
[ ] BulkStatusUpdateResponse model (updated, failed, total lists)
[ ] Route handler: @router.patch("/bulk-status")
[ ] Service method: bulk_update_status(activity_ids, status)
[ ] HTTP status code routing: 200, 207, 400, 404
[ ] Validation: status must be "DONE" or "BLOCKED"
[ ] Partial failure handling: separate updated vs failed lists
[ ] Audit trail: one entry per successfully updated activity

ACCEPTANCE CRITERIA VERIFICATION:
[ ] AC1 Pass: All activities updated → 200 with all IDs in updated list
[ ] AC2 Pass: Partial failure → 207 with both updated and failed lists
[ ] AC3 Pass: Invalid status → 400 with error message
[ ] AC4 Pass: All invalid IDs → 404 with failed list
[ ] AC5 Pass: Audit entries created for each updated activity
[ ] AC6 Pass: Empty list → 200 with empty lists

TESTING:
[ ] test_bulk_update_all_valid_ids passes
[ ] test_bulk_update_partial_failure passes
[ ] test_bulk_update_invalid_status passes
[ ] test_bulk_update_all_invalid_ids passes
[ ] test_bulk_update_empty_list passes
[ ] test_bulk_update_audit_entries passes
[ ] test_endpoint_bulk_status_success passes
[ ] test_endpoint_bulk_status_partial passes
[ ] test_endpoint_bulk_status_validation passes
[ ] test_endpoint_bulk_status_not_found passes

QUALITY GATES:
[ ] Ruff linting: 0 violations
[ ] Mypy type checking: 0 errors
[ ] Service coverage: ≥80%
[ ] Route coverage: ≥75%
[ ] Overall test pass: 22+ tests (all baseline + new)
[ ] Architecture audit: 0 module boundary violations
[ ] No cross-module repository imports
[ ] Error handling uses AppError subclasses
```

---

## SUCCESS MEASURES

### Functional Success
1. **Endpoint Correctness:** All 6 acceptance criteria pass with real data
2. **Status Codes:** 200 (all success), 207 (partial), 400 (invalid), 404 (none found) - verified
3. **Audit Trail:** Each successful update has corresponding audit entry with timestamp, IDs, status change
4. **Partial Failure:** Failed IDs do not block successful updates; both lists populated correctly

### Quality Success
1. **Test Coverage:** Service ≥80%, Route ≥75%
2. **Code Quality:** Ruff 0 violations, Mypy 0 errors
3. **All Tests Pass:** 22+ baseline tests + 10 new tests = 32+ passing
4. **Architecture:** 0 boundary violations, 0 cross-module repo imports

### Performance Success
1. **Latency:** Bulk update of 10 activities completes in <100ms
2. **Data Integrity:** No partial updates left dangling; either persisted or rolled back

### Reliability Success
1. **Error Handling:** All error paths use AppError subclasses
2. **Empty List:** Endpoint gracefully handles empty array
3. **Invalid Status:** Rejected before any updates attempted

---

## HARD GATES (Must All Pass)

### Gate 1: Pytest
**Requirement:** All tests pass, including new bulk endpoint tests  
**Command:** `pytest -q`  
**Expected:** `32+ passed` (22 baseline + 10 new)  
**Failure Consequence:** FAIL verdict

### Gate 2: Ruff Linting
**Requirement:** No linting violations in modified files  
**Command:** `ruff check src/storeops/activities/ tests/test_activities.py`  
**Expected:** `All checks passed`  
**Failure Consequence:** FAIL verdict

### Gate 3: Mypy Type Checking
**Requirement:** All type hints correct, no type errors  
**Command:** `mypy src/storeops/activities/`  
**Expected:** `Success: no issues found`  
**Failure Consequence:** FAIL verdict

### Gate 4: Coverage
**Requirement:** Service layer ≥80%, Route layer ≥75%  
**Command:** `pytest --cov=storeops.activities --cov-report=term-missing`  
**Expected:** 
- `storeops/activities/service.py` ≥80%
- `storeops/activities/routes.py` ≥75%  
**Failure Consequence:** FAIL verdict

### Gate 5: Architecture Audit
**Requirement:** No cross-module repository imports, no boundary violations  
**Check:** grep for prohibited imports in service/route files  
**Expected:** 0 violations  
**Failure Consequence:** FAIL verdict

---

## SCOPE BOUNDARIES

### IN SCOPE
- PATCH /api/activities/bulk-status endpoint only
- Bulk update service method (Activity module)
- Request/Response models for bulk operation
- Unit tests for service logic
- Integration tests for HTTP endpoint
- Audit trail verification (existing mechanism)

### OUT OF SCOPE (Future Sprints)
- Other HTTP methods (GET, POST, DELETE on bulk endpoint)
- Authorization beyond existing store-scope checks
- Event bus integration (no cross-module side effects needed)
- Performance optimization for >100 items
- Async/parallel bulk processing
- Database transaction support (production only)

### DEPENDENCIES SATISFIED
- Activity model: Already exists ✓
- Activities service: Already exists ✓
- Activities repository: Already exists ✓
- Audit mechanism: Already exists ✓
- AppError hierarchy: Already exists ✓
- Testing framework: Already exists ✓

---

## DELIVERABLES

### Code Files (Modified/Created)

**Modified:**
- `src/storeops/models.py` - Add BulkStatusUpdateRequest, BulkStatusUpdateResponse
- `src/storeops/activities/routes.py` - Add bulk_update_status route handler
- `src/storeops/activities/service.py` - Add bulk_update_status method

**Created:**
- `tests/test_activities_bulk.py` - New test file with 10 tests (optional; can add to test_activities.py)

### Documentation Files

**Created:**
- `.harness/output/spec.md` - Detailed specification (this document)
- `.harness/output/sprint-2-contract.md` - Sprint contract (this document)

### Artifacts (Post-Completion)

**Generated by Generator Agent:**
- `.harness/output/generator-summary.md` - Implementation summary

**Generated by Evaluator Agent:**
- `.harness/output/evaluator-feedback.md` - Evaluation verdict

**Archived by Monitor Agent:**
- `.harness/reviews/run-log-sprint-2.md` - Final sprint log

---

## ACCEPTANCE GATE

**This sprint is ready to proceed when:**
1. Developer reviews spec.md and accepts feature definition
2. Developer reviews sprint-2-contract.md and accepts acceptance criteria
3. Developer enters: **APPROVED** in conversation
4. Harness advances to Generator phase

**Developer may request changes:**
- Clarify acceptance criteria
- Adjust scope boundaries
- Modify success measures
- Request different story point estimate

**Restart condition:** Any change request triggers Planner re-run

---

## ESTIMATION CONFIDENCE

**Confidence Level:** HIGH (90%)

**Rationale:**
- Similar pattern to existing PATCH /api/activities/:id endpoint
- Service method structure clear from existing examples
- Error handling well-defined (AppError hierarchy)
- Tests follow established patterns
- No architectural complexity
- No cross-module dependencies

**Confidence Factors:**
- ✓ Existing Activities module mature
- ✓ Clear spec with 6 concrete acceptance criteria
- ✓ HTTP status codes well-defined
- ✓ Audit mechanism already in place
- ✓ No new technologies/patterns needed

---

## SPRINT PHASE FLOW

This sprint follows the standard harness lifecycle:

```
Sprint 2 Contract (This Document) - STATUS: AWAITING APPROVAL
    ↓
Developer Approval (APPROVED in chat)
    ↓
Generator Phase (Create code + tests)
    ↓
Evaluator Phase (Run hard gates)
    ↓
Verdict (PASS / CONDITIONAL PASS / FAIL)
    ↓
Monitor Phase (Archive and log)
    ↓
Sprint 2 Complete
```

**Max Iterations:** 3 (Fail → Generator retry max 2x before escalation)

---

## KEY CONTACTS

**Feature Owner:** PROMPT.md author (shift handover business context)  
**Code Owner:** Activities module maintainer  
**QA Lead:** Evaluator agent (hard gates verification)  

---

## REVISION HISTORY

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-11-07 | Planner Agent | Initial sprint contract |

---

## APPENDIX: REFERENCE MATERIALS

### Specification
- Full spec in `.harness/output/spec.md`
- 6 acceptance criteria with verification steps
- HTTP contract with request/response examples
- Implementation pattern and code examples
- Testing strategy and coverage targets

### Skills
- `app-context.md` - Module reference
- `architecture-principles.md` - Layer and boundary rules
- `coding-conventions.md` - Code style and patterns

### Related Sprints
- Sprint 1: Baseline (22 tests, 9 endpoints, 88% coverage)
- Sprint 2: This sprint (bulk status endpoint)
- Sprint N: Future features

---

## SIGN-OFF

**Planner Agent:** Claude Haiku 4.5  
**Generated:** 2026-11-07  
**Harness Version:** Sprint 2 (Autonomous Loop Ready)  

**Next Step:** Await developer approval to proceed to Generator phase.
