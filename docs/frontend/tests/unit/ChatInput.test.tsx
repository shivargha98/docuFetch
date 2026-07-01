/**
 * Unit tests for src/components/ChatInput.tsx.
 *
 * Covers: Enter-to-send (with trimming and clear), Shift+Enter newline,
 * whitespace-only no-op, disabled state when isLoading is true.
 *
 * No network calls. onSend is a vi.fn() spy.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
// import { ChatInput } from "../../src/components/ChatInput";

describe("ChatInput", () => {
  it("Enter with non-empty text calls onSend with the trimmed value and clears the field", () => {
    /**
     * Given: ChatInput rendered with onSend spy and isLoading=false;
     *        user has typed "  Hello  "
     * When:  user presses Enter
     * Then:  onSend called once with "Hello"; textarea value is empty afterward
     *
     * Source: Feature: ChatInput — criterion 1; PRD user story 4; Issue 7 AC 1
     */
    throw new Error("Not implemented");
  });

  it("Shift+Enter inserts a newline without calling onSend", () => {
    /**
     * Given: ChatInput rendered with onSend spy; user has typed "line one"
     * When:  user presses Shift+Enter
     * Then:  onSend is not called; textarea value contains a newline
     *
     * Source: Feature: ChatInput — criterion 2; PRD user story 5; Issue 7 AC 2
     */
    throw new Error("Not implemented");
  });

  it("Enter with whitespace-only content does not call onSend", () => {
    /**
     * Given: ChatInput with value "   " (spaces only)
     * When:  user presses Enter
     * Then:  onSend is not called; textarea is not cleared
     *
     * Source: Feature: ChatInput — criterion 5; Issue 7 AC 5
     */
    throw new Error("Not implemented");
  });

  it("disables the textarea when isLoading is true", () => {
    /**
     * Given: ChatInput rendered with isLoading=true
     * When:  the component renders
     * Then:  the textarea element has the disabled attribute
     *
     * Source: Feature: ChatInput — criterion 3; PRD user story 8; Issue 7 AC 3
     */
    throw new Error("Not implemented");
  });

  it("disables the send button when isLoading is true", () => {
    /**
     * Given: ChatInput rendered with isLoading=true
     * When:  the component renders
     * Then:  the send button element has the disabled attribute
     *
     * Source: Feature: ChatInput — criterion 3; PRD user story 8; Issue 7 AC 3
     */
    throw new Error("Not implemented");
  });
});
