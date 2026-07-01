// Unit tests for ChatWindow component — covers message rendering, TypingIndicator
// visibility, empty state, and auto-scroll behavior.

import { render } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ChatWindow from '../../src/components/ChatWindow'
import type { Message } from '../../src/types/message'

const makeMessages = (count: number): Message[] =>
  Array.from({ length: count }, (_, i) => ({
    id: String(i + 1),
    role: 'user' as const,
    text: `Message ${i + 1}`,
  }))

describe('ChatWindow', () => {
  beforeEach(() => {
    // jsdom does not implement scrollIntoView; stub it globally for all tests.
    Element.prototype.scrollIntoView = vi.fn()
  })
  it('renders a MessageBubble for each message in the list', () => {
    const messages = makeMessages(3)
    const { container } = render(<ChatWindow messages={messages} isLoading={false} />)
    const bubbles = container.querySelectorAll('[data-role]')
    expect(bubbles).toHaveLength(3)
  })

  it('renders TypingIndicator when isLoading is true', () => {
    const messages = makeMessages(1)
    const { getByTestId } = render(<ChatWindow messages={messages} isLoading={true} />)
    expect(getByTestId('typing-indicator')).toBeInTheDocument()
  })

  it('does not render TypingIndicator when isLoading is false', () => {
    const messages = makeMessages(1)
    const { queryByTestId } = render(<ChatWindow messages={messages} isLoading={false} />)
    expect(queryByTestId('typing-indicator')).toBeNull()
  })

  it('empty message list renders without error and no bubbles', () => {
    const { container } = render(<ChatWindow messages={[]} isLoading={false} />)
    expect(container.querySelectorAll('[data-role]')).toHaveLength(0)
  })

  it('scrolls to bottom when a new message is appended', () => {
    const { rerender } = render(<ChatWindow messages={makeMessages(2)} isLoading={false} />)
    rerender(<ChatWindow messages={makeMessages(3)} isLoading={false} />)

    expect(Element.prototype.scrollIntoView).toHaveBeenCalled()
  })
})
