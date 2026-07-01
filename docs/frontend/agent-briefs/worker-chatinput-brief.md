# Worker Brief: Issue 7 — ChatInput Component

## Prerequisite

Issue 1 (Scaffold) must be complete. The Vite project at `/workspace/frontend/` must exist with `src/components/` directory.

## Your Mission

Create `src/components/ChatInput.tsx` — an auto-growing textarea with a send button. Also write its unit tests.

## What to Build

### File 1: `src/components/ChatInput.tsx`

```
/workspace/frontend/src/components/ChatInput.tsx
```

**Props interface:**
```typescript
interface ChatInputProps {
  onSend: (text: string) => void;
  isLoading: boolean;
}
```

**Behaviour:**
- Renders a `<textarea>` and a send `<button>`
- Enter key (without Shift): calls `onSend(value.trim())` and clears the textarea — but only if `value.trim()` is non-empty. If the trimmed value is empty/whitespace-only, do nothing.
- Shift+Enter: inserts a newline into the textarea. Do NOT call `onSend`. Prevent the default newline behavior by the browser and manually append `\n` to the value.
- When `isLoading` is `true`: both textarea and button must have the `disabled` attribute, and should appear visually muted (use Tailwind's `disabled:opacity-50` or similar)
- The textarea grows vertically as content exceeds one line. Implement this with `overflow-hidden` + auto-height resize via an `onInput` handler that sets `element.style.height = 'auto'` then `element.style.height = element.scrollHeight + 'px'`. The initial height is 1 row.

**Auto-grow implementation:**
```typescript
const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
  setValue(e.target.value)
}
```

**Enter key handler:**
```typescript
const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    const trimmed = value.trim()
    if (trimmed) {
      onSend(trimmed)
      setValue('')
      // reset height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }
}
```

**Styling (Tailwind):**
- Container: `flex items-end gap-2 p-4 border-t border-gray-200`
- Textarea: `flex-1 resize-none overflow-hidden rounded-lg border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed`
- Button: `px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed`
- Button text: "Send"

Add a file description comment at the top of the file. Add docstrings to the component and any helper functions.

### File 2: `tests/unit/ChatInput.test.tsx`

```
/workspace/frontend/tests/unit/ChatInput.test.tsx
```

Write Vitest + RTL tests covering the 4 unit test cases from tests.md:

1. **Enter with non-empty text calls onSend with the trimmed value and clears the field**
   - Render with `onSend` spy (`vi.fn()`), `isLoading={false}`
   - Type `"  Hello  "` into textarea
   - Press Enter
   - Assert: `onSend` called once with `"Hello"`, textarea is empty

2. **Shift+Enter inserts a newline without calling onSend**
   - Render with `onSend` spy, type `"line one"`
   - Press Shift+Enter
   - Assert: `onSend` not called, textarea value contains newline

3. **Enter with whitespace-only content does not call onSend**
   - Render with `onSend` spy, type `"   "`
   - Press Enter
   - Assert: `onSend` not called

4. **isLoading=true disables the textarea and send button**
   - Render with `isLoading={true}`
   - Assert: textarea has `disabled` attribute, button has `disabled` attribute

Test imports:
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect } from 'vitest'
import ChatInput from '../../src/components/ChatInput'
```

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first — minimum code

## Acceptance Criteria (from issues.md Issue 7)

- [ ] Pressing Enter with text calls `onSend` with trimmed value and clears the field
- [ ] Pressing Shift+Enter inserts a newline and does not call `onSend`
- [ ] When `isLoading` is `true`, textarea and button are both disabled
- [ ] The textarea grows in height without showing a scrollbar
- [ ] Pressing Enter with whitespace-only does not call `onSend`

## Verification

Run `npm run test` from `/workspace/frontend/` — all ChatInput tests must pass.

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-chatinput-report.md` with:
- Status: DONE or FAILED
- Files created
- Test results
- Any deviations from this brief
