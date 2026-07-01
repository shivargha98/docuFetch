# Test Suite

_Generated from: docs/frontend/prd.md, docs/frontend/features.md, docs/frontend/issues.md_

---

## Unit Tests

Unit tests render a single component or exercise a pure function in isolation. No network calls, no real hooks — only the component under test and the props it receives.

---

### sources.ts

#### Test: strips a single citation from the middle of a sentence
**Type:** Unit
**Source:** Feature: Source Citation Strip — criterion 1; Issue 3 AC 1
**Given:** The string `"See this [source: report.pdf] for details"`
**When:** `stripCitations` is called
**Then:**
- [ ] The returned string contains no `[source: report.pdf]` text
- [ ] No stray brackets remain in the output

---

#### Test: strips multiple citations scattered at arbitrary positions
**Type:** Unit
**Source:** Feature: Source Citation Strip — criterion 2; Issue 3 AC 2
**Given:** A string with two `[source: ...]` patterns, one mid-sentence and one at the end
**When:** `stripCitations` is called
**Then:**
- [ ] Both citation patterns are removed from the returned string
- [ ] The surrounding words are preserved

---

#### Test: strips citation with a filename containing spaces
**Type:** Unit
**Source:** Feature: Source Citation Strip — criterion 3; Issue 3 AC 3
**Given:** The string `"Answer [source: my notes.txt] here"`
**When:** `stripCitations` is called
**Then:**
- [ ] The citation including the space-separated filename is fully removed

---

#### Test: strips citation with a filename containing hyphens and dots
**Type:** Unit
**Source:** Feature: Source Citation Strip — criterion 3; Issue 3 AC 3
**Given:** The string `"See [source: project-brief.v2.pdf]"`
**When:** `stripCitations` is called
**Then:**
- [ ] The citation is removed and the returned string contains no brackets

---

#### Test: returns an unchanged string when no citation is present
**Type:** Unit
**Source:** Feature: Source Citation Strip — criterion 4; Issue 3 AC 4
**Given:** A plain string with no `[source: ...]` pattern
**When:** `stripCitations` is called
**Then:**
- [ ] The returned string is identical to the input

---

#### Test: does not mutate the input string
**Type:** Unit
**Source:** Feature: Source Citation Strip — criterion 5; Issue 3 AC 5
**Given:** A string containing a citation pattern
**When:** `stripCitations` is called and the returned value is inspected
**Then:**
- [ ] The original string variable is unchanged after the call

---

### MessageBubble

#### Test: user-role message renders with user-side styling
**Type:** Unit
**Source:** Feature: MessageBubble — criterion 1; Issue 6 AC 1
**Given:** A message object with `role: "user"` and a text body
**When:** `MessageBubble` is rendered
**Then:**
- [ ] The component has a CSS class or attribute indicating user alignment/styling
- [ ] No assistant-side styling class is present

---

#### Test: assistant-role message renders with assistant-side styling
**Type:** Unit
**Source:** Feature: MessageBubble — criterion 1; Issue 6 AC 1
**Given:** A message object with `role: "assistant"` and a text body
**When:** `MessageBubble` is rendered
**Then:**
- [ ] The component has a CSS class or attribute indicating assistant alignment/styling

---

#### Test: assistant message strips inline citation markers from the displayed text
**Type:** Unit
**Source:** Feature: MessageBubble — criterion 2; PRD user story 10; Issue 6 AC 2
**Given:** An assistant message whose text is `"The answer is X [source: notes.pdf]."`
**When:** `MessageBubble` is rendered
**Then:**
- [ ] The text `"[source: notes.pdf]"` does not appear in the rendered output
- [ ] The phrase `"The answer is X"` is visible

---

#### Test: assistant message with non-empty sources renders a sources block
**Type:** Unit
**Source:** Feature: MessageBubble — criterion 3; PRD user story 11; Issue 6 AC 2
**Given:** An assistant message with `sources: ["notes.pdf", "summary.txt"]`
**When:** `MessageBubble` is rendered
**Then:**
- [ ] A sources block is present in the rendered output
- [ ] Both `"notes.pdf"` and `"summary.txt"` appear in that block

---

#### Test: assistant message with empty sources array renders no sources block
**Type:** Unit
**Source:** Feature: MessageBubble — criterion 4; Issue 6 AC 3
**Given:** An assistant message with `sources: []`
**When:** `MessageBubble` is rendered
**Then:**
- [ ] No sources block, label, or source filename appears in the rendered output

---

#### Test: error-role message renders in a distinct error style
**Type:** Unit
**Source:** Feature: MessageBubble — criterion 5; Issue 6 AC 4
**Given:** A message object with `role: "error"` and an error text body
**When:** `MessageBubble` is rendered
**Then:**
- [ ] The component has a CSS class or attribute indicating error styling
- [ ] Neither user-side nor standard assistant-side styling classes are present

---

### TypingIndicator

#### Test: renders as an assistant-side bubble
**Type:** Unit
**Source:** Feature: TypingIndicator — criterion 1
**Given:** No props
**When:** `TypingIndicator` is rendered
**Then:**
- [ ] The root element has the assistant-side styling class (matching `MessageBubble` assistant style)

---

#### Test: renders exactly three animated dots
**Type:** Unit
**Source:** Feature: TypingIndicator — criterion 2
**Given:** No props
**When:** `TypingIndicator` is rendered
**Then:**
- [ ] Exactly three dot elements are present in the rendered output

---

### ChatInput

#### Test: Enter with non-empty text calls onSend with the trimmed value and clears the field
**Type:** Unit
**Source:** Feature: ChatInput — criterion 1; PRD user story 4; Issue 7 AC 1
**Given:** A `ChatInput` rendered with an `onSend` spy and `isLoading={false}`; the user has typed `"  Hello  "`
**When:** The user presses Enter
**Then:**
- [ ] `onSend` is called exactly once with `"Hello"` (trimmed)
- [ ] The textarea value is empty after the call

---

#### Test: Shift+Enter inserts a newline without calling onSend
**Type:** Unit
**Source:** Feature: ChatInput — criterion 2; PRD user story 5; Issue 7 AC 2
**Given:** A `ChatInput` rendered with an `onSend` spy; the user has typed `"line one"`
**When:** The user presses Shift+Enter
**Then:**
- [ ] `onSend` is not called
- [ ] The textarea value now contains a newline character

---

#### Test: Enter with whitespace-only content does not call onSend
**Type:** Unit
**Source:** Feature: ChatInput — criterion 5; Issue 7 AC 5
**Given:** A `ChatInput` with the value `"   "` (spaces only)
**When:** The user presses Enter
**Then:**
- [ ] `onSend` is not called
- [ ] The textarea is not cleared

---

#### Test: isLoading=true disables the textarea and send button
**Type:** Unit
**Source:** Feature: ChatInput — criterion 3; PRD user story 8; Issue 7 AC 3
**Given:** A `ChatInput` rendered with `isLoading={true}`
**When:** The component is rendered
**Then:**
- [ ] The textarea element has the `disabled` attribute
- [ ] The send button element has the `disabled` attribute

---

### StatusBar

#### Test: displays the current document count
**Type:** Unit
**Source:** Feature: StatusBar — criterion 1; PRD user story 17; Issue 5 AC 1
**Given:** `StatusBar` rendered with `docCount={42}` and any `lastRunAt`
**When:** The component is rendered
**Then:**
- [ ] The number `42` is visible in the rendered output

---

#### Test: displays the last ingestion time as a readable string
**Type:** Unit
**Source:** Feature: StatusBar — criterion 2; PRD user story 18; Issue 5 AC 2
**Given:** `StatusBar` rendered with a non-null `lastRunAt` timestamp string
**When:** The component is rendered
**Then:**
- [ ] A human-readable representation of the timestamp is visible

---

#### Test: displays "Never" when lastRunAt is null
**Type:** Unit
**Source:** Feature: StatusBar — criterion 2; Issue 5 AC 2
**Given:** `StatusBar` rendered with `lastRunAt={null}`
**When:** The component is rendered
**Then:**
- [ ] The text "Never" (or equivalent) appears in place of a timestamp

---

#### Test: clicking New chat calls the onNewChat handler exactly once
**Type:** Unit
**Source:** Feature: StatusBar — criterion 3; PRD user story 16; Issue 5 AC 4
**Given:** `StatusBar` rendered with an `onNewChat` spy
**When:** The user clicks the "New chat" button
**Then:**
- [ ] `onNewChat` has been called exactly once

---

#### Test: renders without error when docCount is zero and lastRunAt is null
**Type:** Unit
**Source:** Feature: StatusBar — criterion 4; Issue 5 AC 4 (edge case)
**Given:** `StatusBar` rendered with `docCount={0}` and `lastRunAt={null}`
**When:** The component renders
**Then:**
- [ ] No runtime error or React warning is thrown
- [ ] `0` is visible for the doc count

---

### ChatWindow

#### Test: renders a MessageBubble for each message in the list
**Type:** Unit
**Source:** Feature: ChatWindow — criterion 1; Issue 6 (ChatWindow AC)
**Given:** `ChatWindow` rendered with a list of three messages and `isLoading={false}`
**When:** The component renders
**Then:**
- [ ] Three message bubble elements are present in the output

---

#### Test: renders TypingIndicator when isLoading is true
**Type:** Unit
**Source:** Feature: ChatWindow — criterion 2; PRD user story 7; Issue 6 AC 5
**Given:** `ChatWindow` rendered with a non-empty message list and `isLoading={true}`
**When:** The component renders
**Then:**
- [ ] A typing indicator element is present after the last message bubble

---

#### Test: does not render TypingIndicator when isLoading is false
**Type:** Unit
**Source:** Feature: ChatWindow — criterion 2 (negative case)
**Given:** `ChatWindow` rendered with `isLoading={false}`
**When:** The component renders
**Then:**
- [ ] No typing indicator element is present

---

#### Test: empty message list renders without error
**Type:** Unit
**Source:** Feature: ChatWindow — criterion 4; Issue 6 AC (no crash)
**Given:** `ChatWindow` rendered with an empty `messages` array and `isLoading={false}`
**When:** The component renders
**Then:**
- [ ] No runtime error or React warning is thrown
- [ ] No message bubble elements are present

---

#### Test: scrolls to the bottom when a new message is appended
**Type:** Unit
**Source:** Feature: ChatWindow — criterion 3; PRD user story 12; Issue 6 AC 6
**Given:** `ChatWindow` rendered with two messages; `scrollIntoView` is stubbed on the scroll sentinel element
**When:** The component re-renders with a third message appended
**Then:**
- [ ] `scrollIntoView` (or equivalent scroll method) is called after the re-render

---

---

## Integration Tests

Integration tests exercise hooks or a composition of components through real interactions. `fetch` is mocked at the network boundary. React internals are not mocked.

---

### useHealthGate

#### Test: ready is false on initial render
**Type:** Integration
**Source:** Feature: useHealthGate — criterion 1; Issue 4 AC 1
**Given:** `useHealthGate` rendered with `fetch` mocked to never resolve
**When:** The hook mounts
**Then:**
- [ ] `ready` is `false` immediately after mount

---

#### Test: ready becomes true after a poll returns initial_ingestion_complete: true
**Type:** Integration
**Source:** Feature: useHealthGate — criterion 2; Issue 4 AC 2; PRD user story 3
**Given:** `fetch` mocked to return `{ status: "ok", initial_ingestion_complete: true }` on the first call
**When:** The hook mounts and the poll fires
**Then:**
- [ ] `ready` transitions from `false` to `true`

---

#### Test: no further fetch calls are made after ready becomes true
**Type:** Integration
**Source:** Feature: useHealthGate — criterion 3; Issue 4 AC (no revert)
**Given:** `fetch` mocked to return `initial_ingestion_complete: true` on the first call; `vi.useFakeTimers` controls the 3-second interval
**When:** The hook becomes ready and the timer advances another full interval
**Then:**
- [ ] `fetch` is called exactly once (no second poll after ready)

---

#### Test: a failed health poll keeps ready false without showing an error state
**Type:** Integration
**Source:** Feature: useHealthGate — criterion 4; Issue 4 AC 4
**Given:** `fetch` mocked to reject on the first call
**When:** The hook mounts and the poll fires
**Then:**
- [ ] `ready` remains `false`
- [ ] No error property or thrown exception escapes the hook

---

#### Test: polling interval is cleared on unmount
**Type:** Integration
**Source:** Feature: useHealthGate — criterion 5; Issue 4 AC 5
**Given:** `useHealthGate` mounted and then unmounted; `vi.useFakeTimers` is active
**When:** The timer advances past the poll interval after unmount
**Then:**
- [ ] No additional `fetch` call is made after the component unmounts

---

### useIngestStatus

#### Test: docCount and lastRunAt are populated from the first poll
**Type:** Integration
**Source:** Feature: useIngestStatus — criterion 1; Issue 5 AC 1
**Given:** `fetch` mocked to return `{ doc_count: 7, last_run_at: "2026-07-01T10:00:00Z", last_error: null }`
**When:** The hook mounts and the first poll fires
**Then:**
- [ ] `docCount` equals `7`
- [ ] `lastRunAt` equals `"2026-07-01T10:00:00Z"`

---

#### Test: values update after a subsequent poll
**Type:** Integration
**Source:** Feature: useIngestStatus — criterion 2; PRD user story 19; Issue 5 AC 2
**Given:** First poll returns `doc_count: 7`; second poll (after 60s) returns `doc_count: 12`; `vi.useFakeTimers` is active
**When:** The timer advances 60 seconds
**Then:**
- [ ] `docCount` updates to `12` after the second poll

---

#### Test: a failed poll leaves previous values unchanged
**Type:** Integration
**Source:** Feature: useIngestStatus — criterion 3; Issue 5 AC 5
**Given:** First poll returns `doc_count: 5`; second poll rejects; `vi.useFakeTimers` is active
**When:** The timer advances and the second poll fires
**Then:**
- [ ] `docCount` remains `5` after the failed poll

---

#### Test: polling interval is cleared on unmount
**Type:** Integration
**Source:** Feature: useIngestStatus — criterion 4
**Given:** `useIngestStatus` mounted then unmounted; `vi.useFakeTimers` is active
**When:** The timer advances past 60 seconds after unmount
**Then:**
- [ ] No additional `fetch` call fires after unmount

---

### useChat

#### Test: sendMessage appends a user message immediately and an assistant message after resolution
**Type:** Integration
**Source:** Feature: useChat — criterion 1; PRD user story 1; Issue 8 AC 1
**Given:** `fetch` mocked to return `{ answer: "42", sources: [], session_id: "abc" }` after a short delay
**When:** `sendMessage("What is the answer?")` is called
**Then:**
- [ ] A user message with text `"What is the answer?"` appears in the message list before the fetch resolves
- [ ] An assistant message with text `"42"` appears in the message list after the fetch resolves

---

#### Test: isLoading is true during the request and false after resolution
**Type:** Integration
**Source:** Feature: useChat — criterion 2; PRD user story 7/8; Issue 8 AC 2
**Given:** `fetch` mocked with a controlled promise
**When:** `sendMessage` is called and then the promise resolves
**Then:**
- [ ] `isLoading` is `true` between the call and resolution
- [ ] `isLoading` is `false` after resolution

---

#### Test: API failure appends an error entry and resets isLoading to false
**Type:** Integration
**Source:** Feature: useChat — criterion 3; PRD user stories 20–22; Issue 8 AC 3
**Given:** `fetch` mocked to reject
**When:** `sendMessage("question")` is called and the promise rejects
**Then:**
- [ ] An error-role message entry is appended to the message list
- [ ] `isLoading` is `false` after the rejection

---

#### Test: session ID is read from localStorage if one already exists
**Type:** Integration
**Source:** Feature: useChat — criterion 4; PRD user story 13; Issue 8 AC 4
**Given:** `localStorage` pre-populated with `sessionId = "existing-uuid"`
**When:** `useChat` mounts
**Then:**
- [ ] The session ID used in the first `postChat` call is `"existing-uuid"`

---

#### Test: a new UUID4 is generated and saved to localStorage if no session ID exists
**Type:** Integration
**Source:** Feature: useChat — criterion 4; Issue 8 AC 4
**Given:** `localStorage` is empty
**When:** `useChat` mounts and `sendMessage` is called
**Then:**
- [ ] `localStorage` contains a new session ID after mount
- [ ] The generated session ID is a valid UUID4 format

---

#### Test: message list is rehydrated from localStorage on mount
**Type:** Integration
**Source:** Feature: useChat — criterion 5; PRD user story 14; Issue 8 AC 5
**Given:** `localStorage` contains a persisted message list with two entries
**When:** `useChat` mounts
**Then:**
- [ ] The initial message list contains those two entries

---

#### Test: message list is capped at 20 entries
**Type:** Integration
**Source:** Feature: useChat — criterion 5; PRD user story 15; Issue 8 AC 5
**Given:** `localStorage` contains 21 persisted messages; `fetch` is mocked
**When:** `useChat` mounts
**Then:**
- [ ] The message list contains at most 20 entries

---

#### Test: resetChat generates a fresh session ID and clears the message list in localStorage
**Type:** Integration
**Source:** Feature: useChat — criterion 6; PRD user story 16; Issue 8 AC 6
**Given:** `useChat` mounted with an existing session ID and two messages in state
**When:** `resetChat()` is called
**Then:**
- [ ] The message list in state is empty
- [ ] `localStorage` contains a new session ID different from the original
- [ ] `localStorage` contains an empty message list

---

### App (full composition with mocked fetch)

#### Test: startup gate is visible and chat input is not interactive on initial render
**Type:** Integration
**Source:** Feature: App Root and Startup Gate — criterion 1; PRD user story 2; Issue 9 AC 1
**Given:** `App` rendered; `fetch` mocked to return `initial_ingestion_complete: false` for `/health`
**When:** The app mounts
**Then:**
- [ ] A "Preparing" or "Preparing your documents" message is visible
- [ ] No chat textarea is interactive (disabled or absent)

---

#### Test: startup gate clears and chat input activates when health poll returns ready
**Type:** Integration
**Source:** Feature: App Root and Startup Gate — criterion 2; PRD user story 3; Issue 9 AC 2
**Given:** `App` rendered; first `/health` poll returns `initial_ingestion_complete: false`; second returns `true`; `vi.useFakeTimers` controls the 3-second interval
**When:** The timer advances one interval
**Then:**
- [ ] The gate message is no longer visible
- [ ] The chat textarea is enabled

---

#### Test: StatusBar is visible during the startup gate
**Type:** Integration
**Source:** Feature: App Root and Startup Gate — criterion 5; PRD user story 17/18; Issue 9 AC 7
**Given:** `App` rendered; `/health` returns `initial_ingestion_complete: false`
**When:** The app mounts
**Then:**
- [ ] The StatusBar (doc count + last run time area) is present in the rendered output

---

#### Test: sending a message shows typing indicator then appends the response
**Type:** Integration
**Source:** Feature: App Root — criterion 3; PRD user stories 7, 9; Issue 9 AC 3–4
**Given:** `App` in the ready state (health gate resolved); `fetch` mocked for `/chat` to return an answer with sources after a delay
**When:** The user types a question and presses Enter
**Then:**
- [ ] A typing indicator is visible while the fetch is pending
- [ ] The assistant's answer appears in the chat window after resolution
- [ ] The sources block appears under the answer
- [ ] The typing indicator is gone after resolution

---

#### Test: chat API failure shows an inline error bubble and re-enables the input
**Type:** Integration
**Source:** Feature: useChat — criterion 3; PRD user stories 20–22; Issue 9 AC 5
**Given:** `App` in the ready state; `fetch` for `/chat` mocked to reject
**When:** The user sends a message
**Then:**
- [ ] An error-styled message bubble is visible in the chat window
- [ ] The chat textarea is re-enabled after the failure

---

#### Test: New chat clears the visible message list
**Type:** Integration
**Source:** Feature: App Root — criterion 4; PRD user story 16; Issue 9 AC 6
**Given:** `App` in the ready state with two messages visible; `fetch` for `/ingest/status` mocked
**When:** The user clicks "New chat"
**Then:**
- [ ] The chat window no longer shows the previous messages
- [ ] The input is still active

---

---

## E2E Tests

E2E tests run in a real browser via Playwright against the actual FastAPI backend. The backend must be running and initial ingestion must be possible. Keep this tier small — only the highest-value flows.

**Prerequisite:** FastAPI backend running at `http://localhost:8000` with a non-empty `WATCH_FOLDER` configured.

---

#### Test: startup gate appears on load and resolves after backend ingestion completes
**Type:** E2E
**Source:** PRD user stories 2–3; Issue 4 AC 1–2
**Given:** The app is loaded in a fresh browser tab; the backend is running and completing its initial ingestion
**When:** The page loads and the user waits
**Then:**
- [ ] The "Preparing your documents…" message (or equivalent) is visible immediately on load
- [ ] Within a reasonable timeout, the gate disappears and the chat input becomes active

---

#### Test: user sends a question and receives an answer with a sources block
**Type:** E2E
**Source:** PRD user stories 1, 9–11; Issue 9 AC 3
**Given:** The app is past the startup gate (ingestion complete); the watched folder contains at least one indexed document
**When:** The user types a question related to an indexed document and presses Enter
**Then:**
- [ ] A typing indicator appears while the response is pending
- [ ] The assistant's answer appears as a message bubble
- [ ] No `[source: ...]` markers appear inside the answer text
- [ ] A sources block listing at least one filename appears below the answer

---

#### Test: New chat clears history and the next message starts a fresh backend session
**Type:** E2E
**Source:** PRD user story 16; Issue 9 AC 6
**Given:** The user has sent at least one message and can see it in the chat window
**When:** The user clicks "New chat" and then sends a new question
**Then:**
- [ ] The previous messages are no longer visible in the chat window
- [ ] The new question is answered without any context from the previous session bleeding in
