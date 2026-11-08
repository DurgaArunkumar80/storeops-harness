# Sprint 1 Contract: Bulk Task Status Update

**Sprint ID:** SPRINT-001  
**Feature:** Bulk Task Status Update for Shift Handover  
**Generated:** 2026-11-05  
**Status:** ✅ **AWAITING APPROVAL**

---

## SPRINT GOALS

1. **Implement** PATCH /api/activities/bulk-status endpoint
2. **Enable** shift staff to update multiple task statuses atomically
3. **Maintain** authorization and audit trail requirements
4. **Achieve** all acceptance criteria and quality gates

---

## ACCEPTANCE CRITERIA CHECKLIST

### Functional Criteria
- [ ] **AC1:** Bulk update executes successfully (all tasks updated when authorized)
- [ ] **AC2:** Partial failure handled gracefully (mix of success/fail returns 200)
- [ ] **AC3:** Authorization enforced per-task (non-owner gets 403)
- [ ] **AC4:** Audit trail created for each updated task (timestamps, reason captured)
- [ ] **AC5:** Invalid status rejected (400 Bad Request for invalid enum)
- [ ] **AC6:** Empty request handled (200 OK with empty arrays)

### Quality Criteria
- [ ] **Tests:** All new tests passing + existing 22 tests still passing
- [ ] **Coverage:** Service ≥85%, Routes ≥75%, Overall ≥70%
- [ ] **Lint:** Ruff all checks passing (0 violations)
- [ ] **Types:** Mypy all checks passing (0 errors)
- [ ] **Architecture:** Audit passing (0 module boundary violations)

---

## WORK BREAKDOWN

### Task 1: Define Models
**Objective:** Create request/response Pydantic models  
**Files to Create/Modify:**
- `src/storeops/models.py` - Add BulkStatusUpdateRequest, BulkUpdateDetail, BulkStatusUpdateResponse

**Acceptance:**
- Models defined with proper validation
- All fields typed
- Defaults specified where needed

---

### Task 2: Implement Service Method
**Objective:** Add bulk_update_status to ActivitiesService  
**Files to Modify:**
- `src/storeops/activities/service.py` - Add bulk_update_status method

**Acceptance:**
- Authorization enforced per-task
- Partial failure handled (don't bail on first error)
- Audit entries created via event or directly
- Returns properly formatted response

**Acceptance Criteria Verified:**
- ✅ AC1: All authorized tasks updated
- ✅ AC2: Partial failures handled
- ✅ AC3: Authorization per-task
- ✅ AC4: Audit trail created
- ✅ AC5: Status validation

---

### Task 3: Implement Route Handler
**Objective:** Create endpoint in ActivitiesService routes  
**Files to Modify:**
- `src/storeops/activities/routes.py` - Add bulk_update_status route

**Acceptance:**
- Endpoint properly decorated as PATCH
- Path is `/bulk-status`
- Full route: `PATCH /api/activities/bulk-status`
- Service injection via Depends
- Auth context extracted
- Response properly modeled

---

### Task 4: Write Tests
**Objective:** Create comprehensive test coverage  
**Files to Create/Modify:**
- `tests/test_activities.py` - Add 8+ new tests

**Tests Required:**
1. test_bulk_update_all_succeed
2. test_bulk_update_partial_failure
3. test_bulk_update_authorization_enforcement
4. test_bulk_update_invalid_status_rejected
5. test_bulk_update_empty_list
6. test_bulk_update_audit_trail_created
7. test_bulk_update_max_items_limit
8. test_bulk_update_reason_field_captured

**Acceptance:**
- All 8 tests passing
- Service coverage ≥85%
- Route coverage ≥75%
- Existing 22 tests still passing

---

## SUCCESS MEASURES

| Measure | Target | Verification |
|---------|--------|--------------|
| All AC met | 6/6 | Manual test per AC |
| Tests passing | 30/30 (22 existing + 8 new) | pytest -q |
| Linting | 0 violations | ruff check |
| Type checking | 0 errors | mypy check |
| Service coverage | ≥85% | pytest --cov |
| Routes coverage | ≥75% | pytest --cov |
| Overall coverage | ≥70% | pytest --cov |
| Architecture | 0 violations | Architecture audit |
| Code quality | All gates passing | All above measures |

---

## DEPENDENCIES

- ✅ StoreOps baseline (already complete)
- ✅ Activities module structure (already in place)
- ✅ TaskStatus enum (already defined)
- ✅ AppError hierarchy (already implemented)
- ✅ Test fixtures (already created)

**No external dependencies required**

---

## KNOWN CONSTRAINTS

1. **Max Items:** 100 tasks per request (prevent abuse)
2. **Status Values:** Only "done" or "blocked" allowed
3. **No Atomicity:** Partial success is acceptable (no rollback)
4. **Authorization:** Per-task, not batch-level
5. **Reason Field:** Optional, max 500 characters

---

## DECISION POINTS

| Decision | Resolution |
|----------|-----------|
| Where to create audit trail? | Service layer (not route, not repo) |
| How to handle auth failures? | Include in failed array with error, continue processing |
| What's max batch size? | 100 items (configurable later) |
| EventBus integration? | Not for this sprint (can add in future) |
| Database persistence? | In-memory storage (project spec) |

---

## ESTIMATED TIMELINE

| Phase | Time | Who |
|-------|------|-----|
| Models | 10 min | Generator |
| Service | 15-20 min | Generator |
| Routes | 10-15 min | Generator |
| Tests | 15-20 min | Generator |
| Verification | 5-10 min | Evaluator |
| **Total** | **60-90 min** | - |

---

## QUALITY GATES (Hard Requirements)

**All must pass for DONE:**

1. **Pytest Hard Gate**
   ```
   pytest -q
   Expected: 30+ passed (22 existing + 8 new)
   Fail if: Any test fails
   ```

2. **Ruff Hard Gate**
   ```
   ruff check src/ tests/
   Expected: All checks passed
   Fail if: Any violation found
   ```

3. **Mypy Hard Gate**
   ```
   mypy src/
   Expected: Success - 0 errors
   Fail if: Any type error found
   ```

4. **Coverage Hard Gate**
   ```
   pytest --cov=src/storeops
   Expected: Overall ≥70%, Service ≥85%, Routes ≥75%
   Fail if: Any threshold not met
   ```

5. **Architecture Hard Gate**
   ```
   Architecture Audit
   Expected: 0 cross-module repository imports
   Fail if: Any violation found
   ```

---

## ROLLBACK PLAN

**If sprint fails after 3 iterations:**

1. Review escalation.md for blocking issue
2. Determine root cause
3. Options:
   - Simplify acceptance criteria
   - Split into multiple sprints
   - Adjust scope (e.g., no audit trail in sprint 1)
   - Fix baseline if blocker in architecture

---

## SIGN-OFF

**Sprint 1 Contract:** ✅ **READY FOR DEVELOPER APPROVAL**

**Developer Approval Required:** Confirm understanding and commitment to acceptance criteria

**Next Step:** Developer reads spec.md + this contract, then enters: **APPROVED**

Once APPROVED, Generator will implement the feature autonomously.

