# Worker Brief: Issue 6 — MessageBubble, TypingIndicator, and ChatWindow Components

## Prerequisites

- Issue 1 (Scaffold) complete — Vite project exists at `/workspace/frontend/`
- Issue 3 (Citation Strip Utility) complete — `src/utils/sources.ts` exists and exports `stripCitations`

Verify this file exists before starting:
- `/workspace/frontend/src/utils/sources.ts` (must export `stripCitations`)

## Your Mission

Create three components: `MessageBubble`, `TypingIndicator`, and `ChatWindow`. Also write their unit tests.

## What to Build

### Message type (shared)

All three components work with messages. Define this type in `src/types/message.ts` (create this file):

```typescript
// src/types/message.ts
// Description: Shared Message type used across chat components

export type MessageRole = 'user' | 'assistant' | 'error'

export interface Message {
  id: string;
  role: MessageRole;
  text: string;
  sources?: string[];
}
```

### File 1: `src/components/MessageBubble.tsx`

```
/workspace/frontend/src/components/MessageBubble.tsx
```

**Props interface:**
```typescript
interface MessageBubbleProps {
  message: Message;
}
```

**Behaviour:**
- `role: "user"`: render right-aligned blue bubble
- `role: "assistant"`: render left-aligned gray bubble; strip citations from `message.text` using `stripCitations` before display; if `message.sources` is a non-empty array, render a sources block below the answer text listing each filename
- `role: "error"`: render left-aligned red/orange bubble with distinct styling; no sources block

**Sources block** (for assistant messages with non-empty sources):
```tsx
<div className="mt-2 text-xs text-gray-500">
  <span className="font-semibold">Sources: </span>
  {message.sources.join(', ')}
</div>
```

Only render the sources block if `message.sources && message.sources.length > 0`.

**Tailwind styling:**
- Container: `flex mb-3` + `justify-end` (user) or `justify-start` (assistant/error)
- User bubble: `bg-blue-600 text-white px-4 py-2 rounded-lg max-w-[70%] whitespace-pre-wrap`
- Assistant bubble: `bg-gray-100 text-gray-800 px-4 py-2 rounded-lg max-w-[70%] whitespace-pre-wrap`
- Error bubble: `bg-red-50 text-red-700 border border-red-200 px-4 py-2 rounded-lg max-w-[70%] whitespace-pre-wrap`

To make testing role detection easy, add a `data-role` attribute to the bubble element:
```tsx
<div data-role={message.role} className={...}>
```

Add file description comment at top. Add docstrings.

### File 2: `src/components/TypingIndicator.tsx`

```
/workspace/frontend/src/components/TypingIndicator.tsx
```

No props. Renders as an assistant-side bubble (same container/bubble structure as MessageBubble assistant style) containing three animated dots.

```tsx
// Three dots with CSS bounce animation via Tailwind animate-bounce with staggered delays
<div className="flex mb-3 justify-start">
  <div className="bg-gray-100 px-4 py-3 rounded-lg">
    <div className="flex gap-1">
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
    </div>
  </div>
</div>
```

Add `data-testid="typing-indicator"` to the root element for testability.

Add file description comment at top. Add docstring to the component.

### File 3: `src/components/ChatWindow.tsx`

```
/workspace/frontend/src/components/ChatWindow.tsx
```

**Props interface:**
```typescript
interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
}
```

**Behaviour:**
- Renders a scrollable container
- Renders a `MessageBubble` for each message in `messages`
- When `isLoading` is `true`, renders a `TypingIndicator` after the last bubble
- Auto-scrolls to the bottom whenever `messages.length` changes or `isLoading` changes to `true`

**Auto-scroll implementation:**
```typescript
const bottomRef = useRef<HTMLDivElement>(null)

useEffect(() => {
  bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [messages.length, isLoading])
```

Place a `<div ref={bottomRef} />` at the end of the scroll container.

**Styling:**
- Container: `flex-1 overflow-y-auto p-4`
- No outer wrapper needed — App.tsx will provide the layout context

Add file description at top. Add docstring.

### File 4: `tests/unit/MessageBubble.test.tsx`

```
/workspace/frontend/tests/unit/MessageBubble.test.tsx
```

Write RTL unit tests for the 5 MessageBubble test cases from tests.md:

**Test 1: user-role message renders with user-side styling**
- Render with `{ id: '1', role: 'user', text: 'Hello' }`
- Assert element with `data-role="user"` is present
- No assistant-side class present

**Test 2: assistant-role message renders with assistant-side styling**
- Render with `{ id: '2', role: 'assistant', text: 'Hi there', sources: [] }`
- Assert element with `data-role="assistant"` is present

**Test 3: assistant message strips inline citation markers from displayed text**
- Render with `{ id: '3', role: 'assistant', text: 'The answer is X [source: notes.pdf].', sources: ['notes.pdf'] }`
- Assert `[source: notes.pdf]` does NOT appear in rendered output
- Assert "The answer is X" IS visible

**Test 4: assistant message with non-empty sources renders a sources block**
- Render with `{ id: '4', role: 'assistant', text: 'Answer', sources: ['notes.pdf', 'summary.txt'] }`
- Assert sources block is present
- Assert both filenames appear in output

**Test 5: assistant message with empty sources array renders no sources block**
- Render with `{ id: '5', role: 'assistant', text: 'Answer', sources: [] }`
- Assert no sources block (no element containing "Sources:")

**Test 6: error-role message renders in distinct error style**
- Render with `{ id: '6', role: 'error', text: 'Something went wrong' }`
- Assert element with `data-role="error"` is present
- No user or standard assistant class

### File 5: `tests/unit/TypingIndicator.test.tsx`

```
/workspace/frontend/tests/unit/TypingIndicator.test.tsx
```

**Test 1: renders as assistant-side bubble**
- Render `<TypingIndicator />`
- Assert `data-testid="typing-indicator"` is present
- Assert it has the same assistant-side container structure (justify-start in class or structure)

**Test 2: renders exactly three animated dots**
- Render `<TypingIndicator />`
- Assert exactly 3 span/dot elements with the animate-bounce class (or query by `getByTestId` and check children count)

### File 6: `tests/unit/ChatWindow.test.tsx`

```
/workspace/frontend/tests/unit/ChatWindow.test.tsx
```

**Test 1: renders a MessageBubble for each message in the list**
- Render with 3 messages, `isLoading={false}`
- Assert 3 elements with `[data-role]` attribute are present

**Test 2: renders TypingIndicator when isLoading is true**
- Render with non-empty message list, `isLoading={true}`
- Assert element with `data-testid="typing-indicator"` is present

**Test 3: does not render TypingIndicator when isLoading is false**
- Render with `isLoading={false}`
- Assert no element with `data-testid="typing-indicator"`

**Test 4: empty message list renders without error**
- Render with `messages={[]}`, `isLoading={false}`
- Assert no runtime error, no `[data-role]` elements

**Test 5: scrolls to bottom when a new message is appended**
- Stub `scrollIntoView` on the `Element.prototype`
- Render with 2 messages
- Rerender with 3 messages
- Assert `scrollIntoView` was called

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first — no speculative features

## Acceptance Criteria (from issues.md Issue 6)

- [ ] User message renders right-aligned (or user-side styling); assistant message renders left-aligned
- [ ] Assistant message with `[source: notes.pdf]` in text: citation stripped, "notes.pdf" in sources block
- [ ] Assistant message with empty sources: no sources block rendered
- [ ] Error-role message renders in distinct error style
- [ ] `ChatWindow` with `isLoading={true}` renders `TypingIndicator` after last message bubble
- [ ] `ChatWindow` scrolls to bottom when new message appended

## Verification

Run `npm run test` from `/workspace/frontend/` — all tests must pass.

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-components-report.md` with:
- Status: DONE or FAILED
- Files created (including `src/types/message.ts`)
- Test results
- Any deviations from this brief
