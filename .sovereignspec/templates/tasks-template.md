# Tasks: {spec-id} v{version}

<!--
This file contains the task decomposition for the specification.
Tasks are ordered by dependency. Tasks marked with [P] can run in parallel.
Complete tasks by changing [ ] to [x] and adding a completion note.
-->

<!--
## [P] Task N: Title
Description of the task.
Status: [ ] pending
Files to create/modify:
  - path/to/file.ts
  - path/to/another-file.ts
Acceptance: What must be true for this task to be complete
-->

## Task 1: Implement Core Functionality

<!--
Describe the core implementation task here. This usually corresponds
to the first requirement in the spec.
-->

Status: [ ] pending
Files to create/modify:
  - (list file paths here)
Acceptance: (define acceptance criteria for this task)

---

## [P] Task 2: Implement Supporting Feature A

<!--
This task can run in parallel with Task 3 if it has no dependency on it.
Mark with [P] if parallel, omit if sequential.
-->

Status: [ ] pending
Files to create/modify:
  - (list file paths here)
Acceptance: (define acceptance criteria for this task)

---

## [P] Task 3: Implement Supporting Feature B

<!--
This task can run in parallel with Task 2.
-->

Status: [ ] pending
Files to create/modify:
  - (list file paths here)
Acceptance: (define acceptance criteria for this task)

---

## Task 4: Write Tests (depends on Tasks 1, 2, 3)

<!--
Testing happens after implementation tasks are complete.
Tests verify the spec's acceptance criteria.
-->

Status: [ ] pending
Files to create/modify:
  - (list test file paths here)
Acceptance: All acceptance criteria in the spec are covered by tests.
  All tests pass.

---

## Task 5: Generate Documentation (depends on Tasks 1, 2, 3)

<!--
Documentation is generated after implementation.
-->

Status: [ ] pending
Files to create/modify:
  - (list doc file paths here)
Acceptance: Every new module and endpoint is documented.

---

## Task 6: Update Knowledge Graph (depends on Tasks 1-5)

<!--
After all implementation is complete, update the knowledge graph.
-->

Status: [ ] pending
Files to create/modify:
  - .sovereignspec/graph/graph.json
Acceptance: All new modules and endpoints are added as nodes.
  All edges from spec to new nodes are created.
  Artifacts are registered.

---

## Task 7: Create ADR Drafts (if applicable)

<!--
If implementation revealed architectural decisions not covered by existing ADRs,
create ADR drafts. This task may not apply to all specs.
-->

Status: [ ] pending
Files to create/modify:
  - .sovereignspec/adr/ADR-NNN.md
Acceptance: ADR follows the template. Context, decision, rationale, and
  consequences are documented.

---

## Task 8: Register Artifacts

<!--
Final step: register all generated files in the artifact registry.
-->

Status: [ ] pending
Files to create/modify:
  - .sovereignspec/agents/{agent-name}/artifacts.json
Acceptance: All generated files are registered with correct types.

---

## Completion Checklist

<!--
Mark each item when verified:
[ ] All implementation tasks complete
[ ] All tests pass
[ ] Documentation generated
[ ] Knowledge graph updated
[ ] ADR drafts created (if needed)
[ ] Artifacts registered
[ ] Spec status updated in .sspec file
-->
