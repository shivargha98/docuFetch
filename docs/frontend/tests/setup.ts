/**
 * Shared Vitest setup for docuFetch frontend tests.
 *
 * Provides:
 *   - mockFetch: stub global fetch with controlled per-endpoint responses
 *   - resetLocalStorage: wipe localStorage between tests
 *   - advancePollingInterval: move fake timers forward by a given ms
 *
 * All unit and integration tests should import helpers from here rather than
 * stubbing fetch or localStorage inline. This keeps the mock boundary consistent:
 * we only ever mock at the network boundary (fetch), never inside React hooks or
 * component internals.
 */
import { vi, beforeEach, afterEach } from "vitest";
import "@testing-library/jest-dom";

// ---------------------------------------------------------------------------
// localStorage reset
// ---------------------------------------------------------------------------

/**
 * Clears all localStorage entries between tests.
 * Call this in a beforeEach to prevent state leaking across tests.
 */
export function resetLocalStorage(): void {
  throw new Error("Not implemented");
}

// ---------------------------------------------------------------------------
// fetch mock helpers
// ---------------------------------------------------------------------------

/**
 * Response shape accepted by mockFetch per endpoint.
 */
export interface MockEndpointConfig {
  /** HTTP status to return (default: 200). */
  status?: number;
  /** JSON body to return. */
  body: Record<string, unknown>;
  /** If true, the fetch promise rejects with a network error instead. */
  rejectWithNetworkError?: boolean;
}

/**
 * Stubs global fetch so that each known endpoint returns a controlled response.
 *
 * Usage:
 *   mockFetch({
 *     "/health":         { body: { status: "ok", initial_ingestion_complete: true } },
 *     "/ingest/status":  { body: { doc_count: 5, last_run_at: null, last_error: null } },
 *     "/chat":           { body: { answer: "42", sources: ["notes.pdf"], session_id: "abc" } },
 *   });
 *
 * Any endpoint not listed throws an assertion error so tests fail loudly on
 * unexpected calls rather than silently returning undefined.
 */
export function mockFetch(
  _endpoints: Partial<Record<"/health" | "/ingest/status" | "/chat", MockEndpointConfig>>
): void {
  throw new Error("Not implemented");
}

/**
 * Restores global fetch to its original value.
 * Called automatically in afterEach if you use the setupFetchMocking() helper below.
 */
export function restoreFetch(): void {
  throw new Error("Not implemented");
}

// ---------------------------------------------------------------------------
// Timer helpers
// ---------------------------------------------------------------------------

/**
 * Advances fake timers by the given number of milliseconds and flushes any
 * queued React state updates.
 *
 * Requires vi.useFakeTimers() to have been called before using this helper.
 * Call vi.useRealTimers() in afterEach to clean up.
 */
export async function advanceTimersByMs(_ms: number): Promise<void> {
  throw new Error("Not implemented");
}

// ---------------------------------------------------------------------------
// Automatic setup / teardown
// ---------------------------------------------------------------------------

/**
 * Call once at the top of a describe block to automatically:
 *   - clear localStorage before each test
 *   - restore fetch after each test
 *
 * Individual tests still call mockFetch() to configure responses.
 */
export function setupTestEnvironment(): void {
  beforeEach(() => {
    resetLocalStorage();
  });

  afterEach(() => {
    restoreFetch();
    vi.clearAllTimers();
  });
}
