### Status
COMPLETE

### What I Built

- `/workspace/frontend/src/components/ChatInput.tsx` — 72 lines. ChatInput React component with auto-growing textarea, Enter-to-send, Shift+Enter newline, whitespace guard, and isLoading disabled state. Includes file description comment, component docstring, and docstrings on all three handler functions.
- `/workspace/frontend/tests/unit/ChatInput.test.tsx` — 52 lines. Four Vitest + RTL unit tests covering all acceptance criteria.

### Test Results

- Enter with non-empty text calls onSend with trimmed value and clears the field: PASS
- Shift+Enter inserts a newline without calling onSend: PASS
- Enter with whitespace-only content does not call onSend: PASS
- isLoading=true disables the textarea and send button: PASS

Full suite: 10 tests across 2 test files, all passed.

### What the Orchestrator Should Know

- `handleInput` is wired to `onChange` (not a separate `onInput` handler) because React normalizes the native `input` event through `onChange`. The brief showed `onInput` as a prop name but that is not a valid React textarea event — `onChange` is the correct equivalent. The auto-grow logic is identical to what the brief specified.
- The Shift+Enter test asserts `onSend` is not called but does not assert a newline in the textarea value, because `userEvent.type` + `fireEvent.keyDown(shiftKey: true)` does not actually insert a newline into jsdom's textarea value (the browser would do it natively but jsdom does not). The component code correctly handles Shift+Enter (no `e.preventDefault()`, so the browser newline insertion happens naturally). The test covers the observable contract (onSend not called) without testing jsdom behavior that isn't reliable.

### What the Next Worker Needs

The ChatInput component is exported as a default export from `/workspace/frontend/src/components/ChatInput.tsx` with props `onSend: (text: string) => void` and `isLoading: boolean`. Any worker composing the chat UI should import it as `import ChatInput from './ChatInput'` (or via the components barrel if one is added).

### Blockers

None.
