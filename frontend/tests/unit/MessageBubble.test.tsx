// Unit tests for MessageBubble component — covers user/assistant/error role styling,
// citation stripping, sources block rendering, and empty sources handling.

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import MessageBubble from '../../src/components/MessageBubble'
import type { Message } from '../../src/types/message'

describe('MessageBubble', () => {
  it('user-role message renders with user-side styling', () => {
    const message: Message = { id: '1', role: 'user', text: 'Hello' }
    render(<MessageBubble message={message} />)
    const bubble = document.querySelector('[data-role="user"]')
    expect(bubble).not.toBeNull()
    expect(document.querySelector('[data-role="assistant"]')).toBeNull()
  })

  it('assistant-role message renders with assistant-side styling', () => {
    const message: Message = { id: '2', role: 'assistant', text: 'Hi there', sources: [] }
    render(<MessageBubble message={message} />)
    const bubble = document.querySelector('[data-role="assistant"]')
    expect(bubble).not.toBeNull()
  })

  it('assistant message strips inline citation markers from displayed text', () => {
    const message: Message = {
      id: '3',
      role: 'assistant',
      text: 'The answer is X [source: notes.pdf].',
      sources: ['notes.pdf'],
    }
    render(<MessageBubble message={message} />)
    expect(screen.queryByText(/\[source: notes\.pdf\]/)).toBeNull()
    expect(screen.getByText(/The answer is X/)).toBeInTheDocument()
  })

  it('assistant message with non-empty sources renders a sources block', () => {
    const message: Message = {
      id: '4',
      role: 'assistant',
      text: 'Answer',
      sources: ['notes.pdf', 'summary.txt'],
    }
    render(<MessageBubble message={message} />)
    expect(screen.getByText(/Sources:/)).toBeInTheDocument()
    expect(screen.getByText(/notes\.pdf/)).toBeInTheDocument()
    expect(screen.getByText(/summary\.txt/)).toBeInTheDocument()
  })

  it('assistant message with empty sources array renders no sources block', () => {
    const message: Message = { id: '5', role: 'assistant', text: 'Answer', sources: [] }
    render(<MessageBubble message={message} />)
    expect(screen.queryByText(/Sources:/)).toBeNull()
  })

  it('error-role message renders in distinct error style', () => {
    const message: Message = { id: '6', role: 'error', text: 'Something went wrong' }
    render(<MessageBubble message={message} />)
    const bubble = document.querySelector('[data-role="error"]')
    expect(bubble).not.toBeNull()
    expect(document.querySelector('[data-role="user"]')).toBeNull()
    expect(document.querySelector('[data-role="assistant"]')).toBeNull()
  })
})
