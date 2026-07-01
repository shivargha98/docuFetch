# Worker Brief: Issue 3 — Source Citation Strip Utility

## Prerequisite

Issue 1 (Scaffold) must be complete. The Vite project at `/workspace/frontend/` must exist with `src/utils/` directory before you start.

## Your Mission

Create `src/utils/sources.ts` — a single pure function that strips `[source: filename]` patterns from answer text. This is the only place in the codebase that transforms answer text before display. Also write the unit tests for it.

## What to Build

### File 1: `src/utils/sources.ts`

```
/workspace/frontend/src/utils/sources.ts
```

Export one function:

```typescript
export function stripCitations(text: string): string
```

- Removes all occurrences of `[source: <filename>]` from the input string
- The regex must handle filenames with spaces, hyphens, and dots (e.g., `[source: my notes.txt]`, `[source: project-brief.v2.pdf]`)
- Collapses any double spaces left behind by removal
- Returns the original string unchanged if no citation pattern is found
- Does NOT mutate the input string (strings in JS are immutable, so this is guaranteed by returning a new string)
- Has no side effects

Suggested regex: `/\[source:[^\]]+\]/g` — matches `[source:` followed by any characters that are not `]`, followed by `]`. This handles spaces, hyphens, dots, and any other valid filename characters.

After stripping citations, trim any leading/trailing whitespace from the result and collapse internal double spaces to single spaces.

Add a file description comment at the top. Add a docstring to the function.

### File 2: `src/utils/sources.test.ts`

```
/workspace/frontend/tests/unit/sources.test.ts
```

Write Vitest tests covering all six test cases from tests.md:

1. **strips a single citation from the middle of a sentence**
   - Input: `"See this [source: report.pdf] for details"`
   - Expected: no `[source: report.pdf]` in output, no stray brackets

2. **strips multiple citations scattered at arbitrary positions**
   - Input: string with two `[source: ...]` patterns, one mid-sentence, one at end
   - Expected: both removed, surrounding words preserved

3. **strips citation with a filename containing spaces**
   - Input: `"Answer [source: my notes.txt] here"`
   - Expected: citation fully removed including the space-separated filename

4. **strips citation with a filename containing hyphens and dots**
   - Input: `"See [source: project-brief.v2.pdf]"`
   - Expected: citation removed, no brackets remain

5. **returns an unchanged string when no citation is present**
   - Input: plain string with no `[source: ...]`
   - Expected: output === input

6. **does not mutate the input string**
   - Input: string containing a citation
   - Expected: original variable is unchanged after calling `stripCitations`

Test file structure:
```typescript
import { describe, it, expect } from 'vitest'
import { stripCitations } from '../../src/utils/sources'

describe('stripCitations', () => {
  it('...', () => { ... })
  // ...
})
```

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first

## Acceptance Criteria (from issues.md Issue 3)

- [ ] `stripCitations("Some text [source: report.pdf] here")` returns string with no leftover brackets
- [ ] All `[source: ...]` occurrences are removed when multiple citations appear
- [ ] Filenames with spaces, hyphens, and dots are matched and removed
- [ ] A string with no citation patterns is returned unchanged
- [ ] The original string is not mutated

## Verification

Run `npm run test` from `/workspace/frontend/` — all 6 tests must pass.

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-citation-strip-report.md` with:
- Status: DONE or FAILED
- Files created
- Test results (pass/fail counts)
- Any deviations from this brief
