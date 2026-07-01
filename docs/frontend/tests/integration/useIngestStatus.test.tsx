/**
 * Integration tests for src/hooks/useIngestStatus.ts.
 *
 * Covers: initial poll populates values, values update on subsequent polls,
 * failed poll leaves previous values unchanged, interval cleared on unmount.
 *
 * fetch is mocked via the shared mockFetch helper.
 * vi.useFakeTimers() controls the 60-second polling interval.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { mockFetch, restoreFetch, advanceTimersByMs, resetLocalStorage } from "../setup";
// import { useIngestStatus } from "../../src/hooks/useIngestStatus";

describe("useIngestStatus", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    resetLocalStorage();
  });

  afterEach(() => {
    restoreFetch();
    vi.useRealTimers();
  });

  it("populates docCount and lastRunAt from the first successful poll", () => {
    /**
     * Given: fetch returns { doc_count: 7, last_run_at: "2026-07-01T10:00:00Z", last_error: null }
     * When:  the hook mounts and the first poll fires
     * Then:  docCount equals 7; lastRunAt equals "2026-07-01T10:00:00Z"
     *
     * Source: Feature: useIngestStatus — criterion 1; Issue 5 AC 1
     */
    throw new Error("Not implemented");
  });

  it("updates docCount after a subsequent 60-second poll", () => {
    /**
     * Given: first poll returns doc_count: 7; second poll (after 60s) returns doc_count: 12
     * When:  vi fake timer advances 60 seconds
     * Then:  docCount updates to 12
     *
     * Source: Feature: useIngestStatus — criterion 2; PRD user story 19; Issue 5 AC 2
     */
    throw new Error("Not implemented");
  });

  it("leaves previous values unchanged after a failed poll", () => {
    /**
     * Given: first poll returns doc_count: 5; second poll rejects with a network error
     * When:  the timer advances and the second poll fires
     * Then:  docCount remains 5
     *
     * Source: Feature: useIngestStatus — criterion 3; Issue 5 AC 5
     */
    throw new Error("Not implemented");
  });

  it("clears the polling interval on unmount", () => {
    /**
     * Given: useIngestStatus mounted then unmounted; fake timers active
     * When:  the timer advances past 60 seconds after unmount
     * Then:  no additional fetch call fires
     *
     * Source: Feature: useIngestStatus — criterion 4
     */
    throw new Error("Not implemented");
  });
});
