# StoreOps Evaluation Criteria Skill

**Purpose:** Deterministic hard gates for harness verdict (PASS/CONDITIONAL PASS/FAIL).

---

## EVALUATION FRAMEWORK

**Total Weight:** 100%

### Dimension 1: Correctness (35%)
- **Weight:** 35%
- **Purpose:** Code works correctly for acceptance criteria

**Checklist:**
- [ ] All acceptance criteria behavior implemented
- [ ] No logic errors in critical paths
- [ ] Boundary cases handled
- [ ] State transitions correct
- [ ] Authorization rules enforced

**Pass Criteria:**
- All acceptance criteria exhibit correct behavior
- No critical bugs found
- Edge cases handled

**Hard Gate:** Acceptance criteria behavior test MUST PASS
```
if any_acceptance_criteria_fail:
    verdict = FAIL
    return immediately
```

**Failure:** Code doesn't exhibit required behavior

---

### Dimension 2: Architecture Compliance (25%)
- **Weight:** 25%
- **Purpose:** Module boundaries and layer separation maintained

**Checklist:**
- [ ] Zero cross-module repository imports
- [ ] Routes don't import repositories
- [ ] Services contain business logic only
- [ ] Repositories are pure storage
- [ ] No raw Error throws in services/routes
- [ ] All AppErrors properly typed
- [ ] No circular module dependencies
- [ ] Staff module accessed read-only only
- [ ] Reports module doesn't mutate others
- [ ] EventBus used for side effects

**Pass Criteria:**
- Architecture audit passes (all 10 checks)
- No violations detected

**Hard Gate:** Architecture audit MUST PASS
```
violations = run_architecture_audit()
if len(violations) > 0:
    verdict = FAIL
    return immediately
```

**Failure:** Module boundary violation detected

---

### Dimension 3: Quality Gates (20%)
- **Weight:** 20%
- **Purpose:** Lint, type, and test quality maintained

**Checklist:**
- [ ] Pytest: All tests pass (0 failures)
- [ ] Ruff: All linting checks pass (0 violations)
- [ ] Mypy: All type checking passes (0 errors)
- [ ] Coverage: Service layer ≥80%, Routes ≥70%, Overall ≥70%
- [ ] No skipped tests
- [ ] No warnings ignored

**Pass Criteria:**
- pytest: 100% pass rate
- ruff: 0 violations
- mypy: 0 errors
- coverage: All thresholds met

**Hard Gates:**
```
if pytest_failures > 0:
    verdict = FAIL
    return immediately

if ruff_violations > 0:
    verdict = FAIL
    return immediately

if mypy_errors > 0:
    verdict = FAIL
    return immediately

if coverage_below_threshold:
    verdict = FAIL
    return immediately
```

**Failure:** Quality gate not met

---

### Dimension 4: Type Safety (10%)
- **Weight:** 10%
- **Purpose:** All code properly typed per spec

**Checklist:**
- [ ] All functions have return type hints
- [ ] All parameters have type hints
- [ ] Enums used for categorical values
- [ ] No `Any` types except where required
- [ ] Model fields properly typed

**Pass Criteria:**
- mypy: 0 errors (complete type coverage)
- No suspicious type patterns

**Hard Gate:** Mypy must pass (already covered in Quality Gates)

**Failure:** Type safety violations found

---

### Dimension 5: Error Handling (10%)
- **Weight:** 10%
- **Purpose:** Errors properly typed and handled

**Checklist:**
- [ ] No raw `Error` throws in services
- [ ] All business errors use AppError subclasses
- [ ] Error codes match status codes
- [ ] Authorization errors use ForbiddenError
- [ ] Not found errors use NotFoundError
- [ ] Validation errors use ValidationError
- [ ] Conflict errors use ConflictError

**Pass Criteria:**
- All application errors properly typed
- Status codes correct for each error type
- No unhandled exceptions

**Failure:** Raw Error throw found or improper error type

---

## VERDICT DETERMINATION

### PASS
```
if (correctness == PASS AND
    architecture == PASS AND
    quality_gates == PASS AND
    type_safety == PASS AND
    error_handling == PASS):
    verdict = PASS
```

**Conditions:**
- All 5 dimensions pass
- All hard gates pass
- No violations

---

### CONDITIONAL PASS
```
if (correctness == PASS AND
    architecture == PASS AND
    quality_gates == PASS AND
    type_safety == PASS AND
    error_handling == PASS AND
    minor_issues_found):
    verdict = CONDITIONAL_PASS
```

**Valid only if:**
- All hard gates pass
- Minor code quality improvements suggested (not blocking)
- Documentation gaps (not blocking)
- Performance opportunities (not blocking)

**Examples of CONDITIONAL PASS triggers:**
- Code works, all tests pass, but variable naming could be clearer
- All tests pass, but one unit test could be more thorough
- Architecture correct, but one comment needs clarification

---

### FAIL
```
if (ANY hard gate fails):
    verdict = FAIL
```

**Automatic FAIL triggers:**
1. Acceptance criteria not met
2. Architecture audit finds violations
3. Any test fails
4. Linting violations present
5. Type checking errors present
6. Coverage below threshold
7. Raw Error throw found

**Examples:**
- "Activity update doesn't persist status change" → FAIL
- "Activities service imports staff.repository" → FAIL
- "1 test failing" → FAIL
- "Type error in service layer" → FAIL
- "Coverage 65% (below 70%)" → FAIL

---

## EVALUATION OUTPUT FORMAT

```yaml
verdict: PASS | CONDITIONAL_PASS | FAIL
iterations_used: 1-3
timestamp: 2026-11-05T10:30:00Z

dimensions:
  correctness:
    score: 35/35
    status: PASS
    findings: []
  
  architecture:
    score: 25/25
    status: PASS
    violations: 0
  
  quality_gates:
    score: 20/20
    status: PASS
    metrics:
      pytest: 22/22 passed
      ruff: 0 violations
      mypy: 0 errors
      coverage: 88%
  
  type_safety:
    score: 10/10
    status: PASS
  
  error_handling:
    score: 10/10
    status: PASS

hard_gates:
  - name: "Acceptance Criteria"
    status: PASS
    detail: "All GIVEN/WHEN/THEN scenarios execute correctly"
  
  - name: "Architecture Audit"
    status: PASS
    detail: "0 cross-module violations detected"
  
  - name: "Pytest"
    status: PASS
    detail: "22/22 tests passing"
  
  - name: "Ruff"
    status: PASS
    detail: "0 linting violations"
  
  - name: "Mypy"
    status: PASS
    detail: "0 type errors"
  
  - name: "Coverage"
    status: PASS
    detail: "88% (target 70%)"

summary: "All dimensions passed. Code is ready for production."
```

---

## ESCALATION CRITERIA

**Trigger escalation.md if:**
1. Max iterations (3) exceeded with FAIL
2. Repeated same failure across iterations
3. Conflicting requirements detected
4. Blocker outside harness scope

**Escalation includes:**
- Sprint ID
- Iterations used
- Blocking failure
- Failed hard gates
- Affected files
- Recommended human action
