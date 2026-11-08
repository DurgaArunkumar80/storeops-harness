# CLAUDE.md - StoreOps Harness Orchestrator

**Purpose:** Root orchestration brain for multi-agent harness lifecycle.

---

## LIFECYCLE STATE MACHINE

```
Developer Feature Request
    ↓
    [Planner Agent]
    ↓
spec.md + sprint-N-contract.md
    ↓
STATUS: AWAITING APPROVAL
    ↓
[Developer Reviews and Enters: APPROVED]
    ↓
    [Generator Agent] ← Loop Start
    ↓
Code + Tests + generator-summary.md
    ↓
    [Evaluator Agent]
    ↓
    verdict?
    ├─ PASS → [Monitor Agent] → Next Sprint
    ├─ CONDITIONAL PASS → [Monitor Agent] → Next Sprint
    └─ FAIL → Iteration Check
           ├─ < 3 iterations → [Generator Agent] ← Loop Back
           └─ ≥ 3 iterations → escalation.md
```

---

## PHASE 1: PLANNING

**Entry:** Feature request in PROMPT.md  
**Agent:** Planner  
**Output:** spec.md + sprint-N-contract.md

**Planner Responsibilities:**
1. Read PROMPT.md (feature request)
2. Read StoreOps skills (app-context, architecture-principles, coding-conventions)
3. Generate spec.md with:
   - Feature description
   - Acceptance criteria (GIVEN/WHEN/THEN format)
   - Affected modules
   - Architecture impact
   - EventBus impact
   - Known gaps
4. Generate sprint-N-contract.md with:
   - Sprint ID
   - Story points estimate
   - Acceptance criteria checklist
   - Success measures
5. Mark both files with: **STATUS: AWAITING APPROVAL**

**Output Files:**
- `.harness/output/spec.md`
- `.harness/output/sprint-1-contract.md` (or sprint-N)

---

## APPROVAL GATE

**User Action Required:** Explicit review and approval

**User Must:**
1. Read spec.md
2. Review acceptance criteria
3. Confirm understanding
4. Enter: **APPROVED** (in conversation)

**User Can:**
- Request changes (restarts Planner)
- Clarify requirements (restarts Planner)
- Approve as-is (proceeds to Generator)

---

## PHASE 2: GENERATION (Autonomous Loop)

**Entry:** APPROVED status  
**Agent:** Generator  
**Output:** Code + Tests + generator-summary.md  
**Max Iterations:** 3

**Generator Responsibilities:**
1. Read approved spec.md
2. Read sprint-N-contract.md
3. Read StoreOps skills (app-context, architecture-principles, coding-conventions, how-to-test)
4. Implement ONLY the approved sprint
5. Create tests
6. Create generator-summary.md with:
   - Sprint ID
   - Files created/modified
   - Tests created/modified
   - Acceptance criteria self-check
   - Architecture impacts
   - EventBus impacts
   - Known gaps

**Output Files:**
- `src/storeops/<module>/<file>.py` (new/modified)
- `tests/test_<feature>.py` (new tests)
- `.harness/output/generator-summary.md`

---

## PHASE 3: EVALUATION (Autonomous Loop)

**Entry:** Generated code  
**Agent:** Evaluator  
**Output:** evaluator-feedback.md

**Evaluator Responsibilities:**
1. Run hard gates (deterministic checks):
   - Pytest: All tests pass
   - Ruff: All linting passes
   - Mypy: All type checking passes
   - Coverage: Thresholds met
   - Architecture audit: 0 violations
2. Verify acceptance criteria behavior
3. Generate evaluator-feedback.md with:
   - Verdict: PASS | CONDITIONAL PASS | FAIL
   - Each hard gate result
   - Detailed findings
   - Recommended actions if FAIL

**Output Files:**
- `.harness/output/evaluator-feedback.md`

---

## LOOP LOGIC

### Success Path (PASS or CONDITIONAL PASS)
```
Evaluator verdict: PASS or CONDITIONAL PASS
    ↓
    [Monitor Agent]
    ↓
Log to .harness/reviews/run-log.md
    ↓
HARNESS COMPLETE FOR THIS SPRINT
```

### Retry Path (FAIL + iterations < 3)
```
Evaluator verdict: FAIL
iterations_used = 1 or 2
    ↓
[Generator Agent] - Retry
    ↓
Read evaluator-feedback.md
Fix identified issues
Generate new code/tests
    ↓
[Evaluator Agent] - Re-evaluate
    ↓
Verdict?
├─ PASS → Monitor Agent
└─ FAIL + iterations < 3 → Loop again
```

### Escalation Path (FAIL + iterations ≥ 3)
```
Evaluator verdict: FAIL
iterations_used = 3
    ↓
Create .harness/output/escalation.md
    ↓
Include:
  - sprint ID
  - iterations used
  - blocking failure
  - failed hard gates
  - affected files
  - recommended human action
    ↓
ESCALATE TO HUMAN
```

---

## PHASE 4: MONITORING

**Entry:** Final verdict (PASS or CONDITIONAL PASS)  
**Agent:** Monitor  
**Output:** run-log.md

**Monitor Responsibilities:**
1. Archive all sprint evidence to .harness/reviews/
2. Create run-log.md with:
   - Sprint ID
   - Final verdict
   - Iterations used (1-3)
   - Escalation flag (yes/no)
   - Automated check outcome
   - Estimated token cost
   - Quality trend notes
3. Move to next sprint if ready

**Output Files:**
- `.harness/reviews/run-log-<sprint-id>.md`
- `.harness/reviews/<sprint-id>/` (evidence archive)

---

## MAXIMUM RETRIES

```
Per Sprint: 3 iterations maximum

Iteration 1: Generator → Evaluator → FAIL
Iteration 2: Generator → Evaluator → FAIL
Iteration 3: Generator → Evaluator → FAIL
    ↓
Exceeded max retries
    ↓
Create escalation.md
    ↓
Human review required
```

---

## CONTEXT SCOPING STRATEGY

### What Agents See
- **Planner:** PROMPT.md, app-context.md, architecture-principles.md
- **Generator:** spec.md, sprint-N-contract.md, all skills, baseline code
- **Evaluator:** Generated code, all tests, baseline code, evaluation-criteria.md
- **Monitor:** All output from Generator + Evaluator

### What Agents Don't See
- Prior iterations (only current state)
- Other sprints (only current sprint)
- Future features (only current request)

### Why This Matters
- Each agent solves for current state only
- Fresh perspective reduces bias
- Prevents local optimization in wrong direction

---

## CURRENT STATUS

**Baseline:** ✅ Complete
- 5 modules, 9 endpoints
- All tests passing (22/22)
- Quality gates passing

**Harness:** ✅ Ready
- Skills created (5 core)
- Agent definitions pending
- CLAUDE.md (this file) complete
- PROMPT.md ready

**Next:** Planner invocation awaiting feature request approval

---

## COMMAND REFERENCE

### Verify Application State
```bash
cd /Users/949394/Library/CloudStorage/OneDrive-Cognizant/Documents/storeops-harness
source venv/bin/activate
pytest -q              # Should: 22 passed
ruff check src/ tests/ # Should: All checks passed
mypy src/              # Should: Success
```

### Invoke Agents (Manual)
```bash
# After APPROVED, manually invoke:
# Planner reads PROMPT.md
# Generator reads spec.md
# Evaluator runs tests/lint/type-check
# Monitor logs results
```

---

## ESCALATION CONTACTS

If harness fails after 3 iterations:
1. Review escalation.md for blocking issue
2. Determine root cause
3. Decide: Bug in generator? Impossible requirements? Architecture mismatch?
4. Take human action:
   - Fix baseline code
   - Clarify requirements
   - Adjust acceptance criteria
   - Restart from Planner

