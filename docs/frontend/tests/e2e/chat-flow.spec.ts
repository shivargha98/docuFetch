/**
 * End-to-end tests for the docuFetch chat UI.
 *
 * Run against the real FastAPI backend at http://localhost:8000.
 * The backend must be running and WATCH_FOLDER must contain at least one indexed document.
 *
 * Prerequisite: start the backend before running these tests:
 *   uvicorn server:app --port 8000 --reload-dir backend
 *
 * Run with: npx playwright test
 */
import { test, expect } from "@playwright/test";

const APP_URL = "http://localhost:5173";

test.describe("startup gate", () => {
  test("gate appears on load and resolves automatically after ingestion completes", async ({ page }) => {
    /**
     * Given: the app is loaded in a fresh browser tab; backend is running and completing ingestion
     * When:  the page loads and the user waits
     * Then:  "Preparing your documents…" (or equivalent) is visible immediately on load;
     *        within a reasonable timeout the gate disappears and the chat input is active
     *
     * Source: PRD user stories 2–3; Issue 4 AC 1–2
     */
    throw new Error("Not implemented");
  });
});

test.describe("chat flow", () => {
  test.beforeEach(async ({ page }) => {
    /**
     * Navigate to the app and wait for the startup gate to clear before each test.
     * This ensures the chat input is active and the index is ready.
     */
    throw new Error("Not implemented — implement navigation + gate wait here");
  });

  test("user sends a question and receives an answer with a sources block", async ({ page }) => {
    /**
     * Given: app past the startup gate; watched folder has at least one indexed document
     * When:  user types a question related to an indexed document and presses Enter
     * Then:  a typing indicator appears while the response is pending;
     *        the assistant's answer appears as a message bubble;
     *        no [source: ...] markers appear inside the answer text;
     *        a sources block listing at least one filename appears below the answer
     *
     * Source: PRD user stories 1, 9–11; Issue 9 AC 3
     */
    throw new Error("Not implemented");
  });

  test("New chat clears history and the next message starts a fresh session", async ({ page }) => {
    /**
     * Given: user has sent at least one message visible in the chat window
     * When:  user clicks "New chat" then sends a new question
     * Then:  previous messages are no longer visible in the chat window;
     *        the new question is answered without context from the previous session
     *
     * Source: PRD user story 16; Issue 9 AC 6
     */
    throw new Error("Not implemented");
  });
});
