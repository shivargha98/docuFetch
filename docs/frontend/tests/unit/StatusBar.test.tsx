/**
 * Unit tests for src/components/StatusBar.tsx.
 *
 * Covers: doc count display, last run time display (string and null/"Never"),
 * New chat click handler, zero-state rendering.
 *
 * No network calls. Values are passed as props; onNewChat is a vi.fn() spy.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
// import { StatusBar } from "../../src/components/StatusBar";

describe("StatusBar", () => {
  it("displays the current document count", () => {
    /**
     * Given: StatusBar rendered with docCount=42 and any lastRunAt
     * When:  the component renders
     * Then:  the number 42 is visible in the output
     *
     * Source: Feature: StatusBar — criterion 1; PRD user story 17; Issue 5 AC 1
     */
    throw new Error("Not implemented");
  });

  it("displays the last ingestion time as a readable string", () => {
    /**
     * Given: StatusBar rendered with lastRunAt="2026-07-01T10:00:00Z"
     * When:  the component renders
     * Then:  a human-readable date/time representation is visible
     *
     * Source: Feature: StatusBar — criterion 2; PRD user story 18; Issue 5 AC 2
     */
    throw new Error("Not implemented");
  });

  it('displays "Never" when lastRunAt is null', () => {
    /**
     * Given: StatusBar rendered with lastRunAt=null
     * When:  the component renders
     * Then:  the text "Never" (or equivalent) appears in place of a timestamp
     *
     * Source: Feature: StatusBar — criterion 2; Issue 5 AC 2
     */
    throw new Error("Not implemented");
  });

  it("calls the onNewChat handler exactly once when New chat is clicked", () => {
    /**
     * Given: StatusBar rendered with an onNewChat spy
     * When:  the user clicks the "New chat" button
     * Then:  onNewChat has been called exactly once
     *
     * Source: Feature: StatusBar — criterion 3; PRD user story 16; Issue 5 AC 4
     */
    throw new Error("Not implemented");
  });

  it("renders without error when docCount is 0 and lastRunAt is null", () => {
    /**
     * Given: StatusBar rendered with docCount=0 and lastRunAt=null
     * When:  the component renders
     * Then:  no runtime error or React warning is thrown; 0 is visible for doc count
     *
     * Source: Feature: StatusBar — criterion 4; Issue 5 AC (edge case)
     */
    throw new Error("Not implemented");
  });
});
