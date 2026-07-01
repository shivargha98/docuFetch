// Unit tests for TypingIndicator component — verifies testid presence and
// that exactly three animated dot spans are rendered.

import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import TypingIndicator from '../../src/components/TypingIndicator'

describe('TypingIndicator', () => {
  it('renders as assistant-side bubble with testid', () => {
    const { getByTestId } = render(<TypingIndicator />)
    const indicator = getByTestId('typing-indicator')
    expect(indicator).toBeInTheDocument()
    expect(indicator.className).toContain('justify-start')
  })

  it('renders exactly three animated dots', () => {
    const { getByTestId } = render(<TypingIndicator />)
    const indicator = getByTestId('typing-indicator')
    const dots = indicator.querySelectorAll('span.animate-bounce')
    expect(dots).toHaveLength(3)
  })
})
