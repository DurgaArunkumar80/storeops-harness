# Specification: Shift Handover Bulk Status Update (STOREOPS-BULK-001)

**Feature ID:** STOREOPS-BULK-001  
**Sprint:** 2  
**Priority:** High  
**Type:** New Endpoint  

**STATUS: AWAITING APPROVAL**

---

## FEATURE OVERVIEW

**Goal:** Enable shift staff to update multiple operational activities' status in a single request during shift handover.

**Problem:** Currently, updating activity status requires individual PATCH requests per activity, creating delays during shift changes and risk of incomplete updates.

**Solution:** Implement bulk status update endpoint (PATCH /api/activities/bulk-status) with graceful partial failure handling and per-activity audit trail.

---

## ACCEPTANCE CRITERIA

### AC1: Bulk Update - All Success
```
GIVEN a list of valid activity IDs and status "DONE" or "BLOCKED"
WHEN PATCH /api/activities/bulk-status is called
THEN all activities updated to specified status
AND HTTP 200 returned with all IDs in "updated" list
AND audit entry created for each updated activity
```

**Verification:** Call endpoint with 3 valid IDs → verify all marked as DONE/BLOCKED → check audit log has 3 entries

### AC2: Bulk Update - Partial Failure
```
GIVEN a mix of valid and invalid activity IDs and a valid status
WHEN PATCH /api/activities/bulk-status is called
THEN only valid activities are updated
AND HTTP 207 Multi-Status returned
AND response contains both updated and failed lists
AND audit entries created only for successfully updated activities
```

**Verification:** Call with IDs [123, 999, 456] → verify only 123 and 456 marked DONE → response shows updated:[123,456], failed:[999] → audit has 2 entries

### AC3: Invalid Status Validation
```
GIVEN request with invalid status value (not "DONE" or "BLOCKED")
WHEN PATCH /api/activities/bulk-status is called
THEN HTTP 400 Bad Request returned
AND error message identifies valid values (DONE, BLOCKED)
AND no activities are updated
```

**Verification:** Call with status="INVALID" → verify 400 response → verify no activity modified

### AC4: All Invalid Activity IDs
```
GIVEN list of only invalid/non-existent activity IDs
WHEN PATCH /api/activities/bulk-status is called
THEN HTTP 404 Not Found returned
AND all IDs in "failed" list
AND no activities updated
```

**Verification:** Call with IDs [999, 888, 777] → verify 404 response → verify failed list contains all 3 IDs

### AC5: Audit Trail Per Activity
```
GIVEN successful bulk status update
WHEN activities are updated
THEN audit entry created for EACH successfully updated activity
AND audit entry contains: timestamp, activity_id, new_status, previous_status
```

**Verification:** Update 2 activities → verify audit log has exactly 2 entries with timestamp, IDs, status change

### AC6: Empty Activity List
```
GIVEN empty activity_ids array
WHEN PATCH /api/activities/bulk-status is called
THEN HTTP 200 returned with empty updated/failed lists
```

**Verification:** Call with activity_ids=[] → verify 200 response with empty lists

---

## AFFECTED MODULES

### Activities Module (Primary)

**Routes Layer (activities/routes.py):**
- Add new endpoint: `@router.patch("/bulk-status")`
- Dependency injection: ActivitiesService
- Request model: BulkStatusUpdateRequest
- Response model: BulkStatusUpdateResponse
- HTTP status code routing: 200, 207, 400, 404

**Service Layer (activities/service.py):**
- Add method: `bulk_update_status(activity_ids: list[int], status: str) -> dict`
- Validate status against allowed values (DONE, BLOCKED)
- Iterate through activity IDs
- For each: attempt update via repository
- Collect results: updated list, failed list
- Determine HTTP status code (200 all success, 207 partial, 404 all fail, 400 invalid)
- Raise ValidationError if status invalid
- Raise NotFoundError only if all IDs fail

**Repository Layer (activities/repository.py):**
- No changes needed (use existing update_activity method)

**Models (models.py):**
- Add BulkStatusUpdateRequest(BaseModel):
  - activity_ids: list[int]
  - status: str
- Add BulkStatusUpdateResponse(BaseModel):
  - updated: list[int]
  - failed: list[int]
  - total: int

### Audit System (Implicit)

**Behavior:** Each successful update triggers existing audit mechanism
- Audit created by existing service method (not new code)
- Contains: timestamp, activity_id, new_status, previous_status
- Stores in existing audit storage

---

## ARCHITECTURE IMPACT

### Layer Boundaries: MAINTAINED ✓
- Routes: Only HTTP handling, service injection, response mapping
- Service: Business logic, validation, repository access (own module only)
- Repository: No changes (reuse existing update)
- No cross-module repository imports
- No circular dependencies introduced

### Error Handling: CONSISTENT ✓
- ValidationError: Invalid status → HTTP 400
- NotFoundError: All IDs fail → HTTP 404
- Both use existing AppError hierarchy

### Module Independence: MAINTAINED ✓
- Activities module self-contained
- No new dependencies on other modules
- Staff module not accessed (no authorization needed beyond existing checks)
- Reports module not affected

---

## EVENTBUS IMPACT

**Assessment:** None required for this sprint

**Rationale:**
- Bulk update is internal to Activities module
- Audit trail already handled by existing event (if any)
- No side effects in other modules
- Future sprints can add alerts on bulk completion if needed

---

## DATABASE CHANGES

**Assessment:** None (in-memory storage only)

**Note:** Capstone uses dict-based repository. No schema changes needed. Future production migration to ORM will require:
- Index on activity_id for bulk lookup performance
- Audit table design (if audit not implemented)

---

## HTTP CONTRACT

### Request
```
PATCH /api/activities/bulk-status
Content-Type: application/json

{
  "activity_ids": [123, 456, 789],
  "status": "DONE"
}
```

### Responses

**HTTP 200 - All Success**
```json
{
  "updated": [123, 456, 789],
  "failed": [],
  "total": 3
}
```

**HTTP 207 - Partial Success**
```json
{
  "updated": [123, 456],
  "failed": [789],
  "total": 3
}
```

**HTTP 400 - Invalid Status**
```json
{
  "error": "ValidationError",
  "message": "Invalid status value. Allowed: DONE, BLOCKED",
  "code": "INVALID_STATUS"
}
```

**HTTP 404 - All Invalid**
```json
{
  "error": "NotFoundError",
  "message": "No valid activities found for IDs: [999, 888]",
  "code": "NO_ACTIVITIES_FOUND",
  "failed": [999, 888]
}
```

---

## IMPLEMENTATION PATTERN

### Route Handler
```python
@router.patch("/bulk-status")
async def bulk_update_status(
    request: BulkStatusUpdateRequest,
    auth: AuthContext,
    service: ActivitiesService = Depends(get_activities_service),
) -> BulkStatusUpdateResponse:
    """Update status for multiple activities in single request."""
    result = service.bulk_update_status(
        activity_ids=request.activity_ids,
        status=request.status,
    )
    
    # Map result to response with correct HTTP status
    if result["status_code"] == 200:
        return BulkStatusUpdateResponse(**result["data"])
    elif result["status_code"] == 207:
        return BulkStatusUpdateResponse(**result["data"])
    elif result["status_code"] == 400:
        raise ValidationError(result["message"])
    elif result["status_code"] == 404:
        raise NotFoundError(result["message"])
```

### Service Method
```python
def bulk_update_status(
    self,
    activity_ids: list[int],
    status: str,
) -> dict:
    """Bulk update activity status with partial failure handling.
    
    Returns dict with status_code and data/message.
    """
    # Validate status
    if status not in ["DONE", "BLOCKED"]:
        return {
            "status_code": 400,
            "message": f"Invalid status value. Allowed: DONE, BLOCKED"
        }
    
    # Handle empty list
    if not activity_ids:
        return {
            "status_code": 200,
            "data": {
                "updated": [],
                "failed": [],
                "total": 0
            }
        }
    
    updated = []
    failed = []
    
    # Process each activity
    for activity_id in activity_ids:
        try:
            activity = self.repository.get_by_id(activity_id)
            if not activity:
                failed.append(activity_id)
            else:
                self.repository.update_activity(activity_id, {"status": status})
                updated.append(activity_id)
        except Exception:
            failed.append(activity_id)
    
    # Determine response
    if not updated and failed:
        return {
            "status_code": 404,
            "message": f"No valid activities found"
        }
    elif updated and not failed:
        return {
            "status_code": 200,
            "data": {
                "updated": updated,
                "failed": failed,
                "total": len(activity_ids)
            }
        }
    else:
        return {
            "status_code": 207,
            "data": {
                "updated": updated,
                "failed": failed,
                "total": len(activity_ids)
            }
        }
```

---

## TESTING STRATEGY

### Unit Tests (Service Layer)
1. **test_bulk_update_all_valid_ids** - All 3 IDs succeed → 200 response
2. **test_bulk_update_partial_failure** - Mix of valid/invalid → 207 response
3. **test_bulk_update_invalid_status** - Status="INVALID" → 400 with message
4. **test_bulk_update_all_invalid_ids** - All IDs fail → 404 response
5. **test_bulk_update_empty_list** - Empty array → 200 with empty lists
6. **test_bulk_update_audit_entries** - Verify audit created per updated activity

**Coverage Target:** ≥80% of bulk_update_status method

### Integration Tests (Route Layer)
1. **test_endpoint_bulk_status_success** - Full flow with HTTP 200
2. **test_endpoint_bulk_status_partial** - Full flow with HTTP 207
3. **test_endpoint_bulk_status_validation** - Full flow with HTTP 400
4. **test_endpoint_bulk_status_not_found** - Full flow with HTTP 404

**Coverage Target:** ≥75% of route handler

### Test Data
- Use real activity IDs from seeded repository
- Mix of existing and non-existent IDs for partial failure test
- Status values: "DONE", "BLOCKED", "INVALID"
- Edge case: Empty array

---

## KNOWN GAPS & RISKS

### Gap 1: Authorization
**Gap:** No authorization check in bulk endpoint (spec doesn't require it)
**Mitigation:** Service-level auth can be added in future sprint if needed
**Risk:** Low (activities service already validates store scope)

### Gap 2: Concurrency
**Gap:** No lock/transaction mechanism for bulk updates
**Mitigation:** In-memory storage; production migration will use DB transactions
**Risk:** Low (capstone scope, single-user testing)

### Gap 3: Audit Performance
**Gap:** Audit creation happens per activity (N audit calls)
**Mitigation:** Acceptable for bulk of 10-50 items typical in shift handover
**Risk:** Low (not a performance-critical path)

### Gap 4: Status Enum Flexibility
**Gap:** Status validation hard-coded to "DONE", "BLOCKED"
**Mitigation:** Can extend with other status values in future (backward compatible)
**Risk:** Low (spec clearly defines allowed values)

---

## DEFINITION OF DONE

- [ ] BulkStatusUpdateRequest and BulkStatusUpdateResponse models created
- [ ] Route handler PATCH /api/activities/bulk-status implemented
- [ ] Service method bulk_update_status implemented
- [ ] All 6 acceptance criteria pass (manual verification or tests)
- [ ] All 6 unit tests pass
- [ ] All 4 integration tests pass
- [ ] Service coverage ≥80%
- [ ] Route coverage ≥75%
- [ ] Ruff linting: 0 violations
- [ ] Mypy type checking: 0 errors
- [ ] Overall test suite: 22+ tests pass (all baseline + new)
- [ ] Audit entries verified for each successful update
- [ ] Architecture audit: 0 module boundary violations
- [ ] HTTP status codes correctly returned (200, 207, 400, 404)

---

## SUCCESS MEASURES

1. **Functional:** Endpoint handles all 6 AC scenarios correctly
2. **Quality:** All hard gates pass (tests, lint, type-check, coverage, architecture)
3. **Performance:** Bulk update of 10 activities completes <100ms
4. **Reliability:** Partial failure doesn't corrupt data (only successful updates persist)
5. **Auditability:** Each successful update has corresponding audit entry

---

## RELATED DOCUMENTS

- PROMPT.md - Business context and requirements
- app-context.md - Module and endpoint reference
- architecture-principles.md - Layer and boundary rules
- coding-conventions.md - Code style and patterns

