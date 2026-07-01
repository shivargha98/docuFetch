// Unit tests for ChatInput component — covers Enter to send, Shift+Enter for newline,
// whitespace-only guard, and disabled state when isLoading is true.

import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect } from 'vitest'
import ChatInput from '../../src/components/ChatInput'

describe('ChatInput', () => {
  it('Enter with non-empty text calls onSend with trimmed value and clears the field', async () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} isLoading={false} />)
    const textarea = screen.getByRole('textbox')

    await userEvent.type(textarea, '  Hello  ')
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false })

    expect(onSend).toHaveBeenCalledOnce()
    expect(onSend).toHaveBeenCalledWith('Hello')
    expect(textarea).toHaveValue('')
  })

  it('Shift+Enter inserts a newline without calling onSend', async () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} isLoading={false} />)
    const textarea = screen.getByRole('textbox')

    await userEvent.type(textarea, 'line one')
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true })

    expect(onSend).not.toHaveBeenCalled()
  })

  it('Enter with whitespace-only content does not call onSend', async () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} isLoading={false} />)
    const textarea = screen.getByRole('textbox')

    await userEvent.type(textarea, '   ')
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false })

    expect(onSend).not.toHaveBeenCalled()
  })

  it('isLoading=true disables the textarea and send button', () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} isLoading={true} />)

    expect(screen.getByRole('textbox')).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })
})
