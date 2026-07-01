### Status
COMPLETE

### What I Built
- `/workspace/frontend/src/utils/sources.ts` — 17 lines. Exports `stripCitations(text: string): string`. Uses regex `/\[source:[^\]]+\]/g` to remove all citation patterns, then collapses double spaces and trims. File-level description comment and function docstring included.
- `/workspace/frontend/tests/unit/sources.test.ts` — 47 lines. Six Vitest test cases covering all scenarios from the brief.

### Test Results
1. strips a single citation from the middle of a sentence — PASS
2. strips multiple citations scattered at arbitrary positions — PASS
3. strips a citation with a filename containing spaces — PASS
4. strips a citation with a filename containing hyphens and dots — PASS
5. returns an unchanged string when no citation is present — PASS
6. does not mutate the input string — PASS

All 6 tests passed (1 test file, 6 tests).

### What the Orchestrator Should Know
No deviations from the brief. Implementation is exactly as specified. The `tests/unit/` directory already existed from a prior worker; no directory creation was needed beyond the agent-reports directory.

### What the Next Worker Needs
Any component that renders answer text should import `stripCitations` from `src/utils/sources`. Signature: `stripCitations(text: string): string` — call it on the raw answer string before rendering.

### Blockers
None.
