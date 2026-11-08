# Feature Request: Shift Handover Bulk Status Update

**Feature Name:** PATCH /api/activities/bulk-status  
**Feature ID:** STOREOPS-BULK-001  
**Priority:** High  
**Type:** New Endpoint

---

## BUSINESS CONTEXT

**Scenario:** End-of-shift operations

Outgoing shift staff need to quickly mark multiple operational activities as DONE or BLOCKED during shift handover. Currently, they must update each activity individually via PATCH /api/activities/:id.

**Problem:** 
- Time-consuming to update many activities one-by-one
- Risk of incomplete status updates during shift change
- No visibility into partial success if network issues occur

**Solution:** Bulk status update endpoint that:
- Updates multiple activity IDs in one request
- Handles partial failure gracefully
- Creates audit trail for each updated activity
- Provides clear feedback on what succeeded and what failed

---

## FEATURE REQUIREMENTS

### Endpoint Specification

**Method:** PATCH  
**Path:** /api/activities/bulk-status  
**Request Body:**
```json
{
  "activity_ids": [123, 456, 789],
  "status": "DONE" | "BLOCKED"
}
```

**Response - All Success (HTTP 200):**
```json
{
  "updated": [123, 456, 789],
  "failed": [],
  "total": 3
}
```

**Response - Partial Success (HTTP 207):**
```json
{
  "updated": [123, 456],
  "failed": [789],
  "total": 3
}
```

### Acceptance Criteria

**AC1: Bulk Update - All Success**
- GIVEN a list of valid activity IDs and status "DONE" or "BLOCKED"
- WHEN PATCH /api/activities/bulk-status is called
- THEN all activities updated to specified status
- AND HTTP 200 returned with all IDs in "updated" list
- AND audit entry created for each updated activity

**AC2: Bulk Update - Partial Failure**
- GIVEN a mix of valid and invalid activity IDs and a valid status
- WHEN PATCH /api/activities/bulk-status is called
- THEN only valid activities are updated
- AND HTTP 207 Multi-Status returned
- AND response contains both updated and failed lists
- AND audit entries created only for successfully updated activities

**AC3: Invalid Status Validation**
- GIVEN request with invalid status value
- WHEN PATCH /api/activities/bulk-status is called
- THEN HTTP 400 Bad Request returned
- AND error message identifies valid values (DONE, BLOCKED)
- AND no activities are updated

**AC4: All Invalid Activity IDs**
- GIVEN list of only invalid/non-existent activity IDs
- WHEN PATCH /api/activities/bulk-status is called
- THEN HTTP 404 Not Found returned
- AND all IDs in "failed" list
- AND no activities updated

**AC5: Audit Trail Per Activity**
- GIVEN successful bulk status update
- WHEN activities are updated
- THEN audit entry created for EACH successfully updated activity
- AND audit entry contains: timestamp, activity_id, new_status, previous_status

**AC6: Empty Activity List**
- GIVEN empty activity_ids array
- WHEN PATCH /api/activities/bulk-status is called
- THEN HTTP 200 returned with empty updated/failed lists

---

## TECHNICAL REQUIREMENTS

### Architecture

**Endpoint Layer:** Add route to activities/routes.py
```python
@router.patch("/bulk-status")
async def bulk_update_status(
    request: BulkStatusUpdateRequest,
    service: ActivitiesService = Depends(get_activities_service),
) -> BulkStatusUpdateResponse:
    """Update status for multiple activities in single request."""
```

**Service Layer:** Add method to ActivitiesService
```python
def bulk_update_status(
    self,
    activity_ids: list[int],
    status: str,
) -> dict:
    """Bulk update activity status with partial failure handling."""
```

**Repository Layer:** Use existing update_activity method for each ID

### Models

**Create Request/Response Models:**
```python
class BulkStatusUpdateRequest(BaseModel):
    activity_ids: list[int]
    status: str  # "DONE" or "BLOCKED"

class BulkStatusUpdateResponse(BaseModel):
    updated: list[int]      # IDs successfully updated
    failed: list[int]       # IDs that failed to update
    total: int              # Total IDs requested
```

### HTTP Status Codes

- `200 OK`: All activities updated successfully
- `207 Multi-Status`: Partial success (some updated, some failed)
- `400 Bad Request`: Invalid status value or malformed request
- `404 Not Found`: All activity IDs invalid or not found

### Error Handling

- Invalid status → HTTP 400 with error message
- All invalid IDs → HTTP 404
- Partial success → HTTP 207 with updated/failed arrays
- Each failed ID included in response for visibility

### Testing Requirements

**Unit Tests (Service):**
- test_bulk_update_all_valid_ids
- test_bulk_update_partial_failure
- test_bulk_update_invalid_status
- test_bulk_update_all_invalid_ids
- test_bulk_update_empty_list
- test_bulk_update_audit_entries

**Integration Tests (Endpoint):**
- test_endpoint_bulk_status_success
- test_endpoint_bulk_status_partial
- test_endpoint_bulk_status_validation
- test_endpoint_bulk_status_not_found

### Coverage Target
- Service method: ≥80%
- Route handler: ≥75%

---

## DEFINITION OF DONE

- ✓ Endpoint PATCH /api/activities/bulk-status implemented
- ✓ Request validates activity_ids (list of integers) and status (DONE or BLOCKED only)
- ✓ Response contains updated, failed, total fields
- ✓ All 6 acceptance criteria pass with real data
- ✓ All tests pass (including new tests for bulk endpoint)
- ✓ Ruff: 0 violations
- ✓ Mypy: 0 type errors
- ✓ Coverage targets met
- ✓ Audit entries created for each successfully updated activity
- ✓ Endpoint called successfully with real activity IDs from database
- ✓ Partial failure case demonstrated with mixed valid/invalid IDs

---

## DEPENDENCIES

- StoreOps baseline with Activity model
- Existing activities service and repository
- Existing audit mechanism
- Activity model with status field

---

## NOTES

- Demonstration uses existing harness agents (Planner, Generator, Evaluator, Monitor)
- Feature request will exercise multi-agent orchestration
- Implementation follows strict route → service → repository pattern
- Endpoint will be tested against real database data
- Partial failure handling is critical requirement
