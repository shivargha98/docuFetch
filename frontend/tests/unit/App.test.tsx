// Integration tests for App.tsx — verifies the startup gate, chat flow, error handling,
// and new-chat reset behaviour using RTL with a stubbed global fetch.

import { render, screen, act, waitFor } from '@testing-library/react'
import { fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import App from '../../src/App'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Builds a fetch stub that routes /health and /ingest/status to fixed JSON responses.
 * healthReady controls what initial_ingestion_complete returns for /health.
 */
function makeFetchStub(healthReady: boolean) {
  return vi.fn(async (url: string) => {
    if ((url as string).includes('/health')) {
      return {
        ok: true,
        json: async () => ({ status: 'ok', initial_ingestion_complete: healthReady }),
      }
    }
    if ((url as string).includes('/ingest/status')) {
      return {
        ok: true,
        json: async () => ({
          files_processed: 5,
          files_failed: 0,
          files_skipped: 0,
          last_run: null,
        }),
      }
    }
    throw new Error('unexpected fetch: ' + url)
  })
}

/**
 * Flushes all immediately-resolved microtasks (one tick) so that React state
 * updates triggered by async fetch responses are applied to the DOM.
 */
async function flushMicrotasks() {
  await act(async () => {
    await Promise.resolve()
    await Promise.resolve()
  })
}

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------

beforeEach(() => {
  vi.useFakeTimers()
  localStorage.clear()
  // jsdom does not implement scrollIntoView; stub it to avoid test errors.
  Element.prototype.scrollIntoView = vi.fn()
})

afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
})

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('App', () => {
  it('Test 1: startup gate is visible and chat input is not interactive on initial render', async () => {
    vi.stubGlobal('fetch', makeFetchStub(false))

    render(<App />)
    await flushMicrotasks()

    expect(screen.getByText(/preparing your documents/i)).toBeInTheDocument()

    // The textarea should either be absent or disabled.
    const textarea = screen.queryByRole('textbox')
    if (textarea) {
      expect(textarea).toBeDisabled()
    }
  })

  it('Test 2: startup gate clears and chat input activates when health poll returns ready', async () => {
    // Flip to ready after the first health call.
    let healthCallCount = 0
    const fetchMock = vi.fn(async (url: string) => {
      if ((url as string).includes('/health')) {
        healthCallCount++
        return {
          ok: true,
          json: async () => ({
            status: 'ok',
            initial_ingestion_complete: healthCallCount > 1,
          }),
        }
      }
      if ((url as string).includes('/ingest/status')) {
        return {
          ok: true,
          json: async () => ({
            files_processed: 5,
            files_failed: 0,
            files_skipped: 0,
            last_run: null,
          }),
        }
      }
      throw new Error('unexpected fetch: ' + url)
    })
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await flushMicrotasks()

    expect(screen.getByText(/preparing your documents/i)).toBeInTheDocument()

    // Advance past the 3-second polling interval so the second health call fires.
    await act(async () => {
      vi.advanceTimersByTime(3000)
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(screen.queryByText(/preparing your documents/i)).not.toBeInTheDocument()
    expect(screen.getByRole('textbox')).not.toBeDisabled()
  })

  it('Test 3: StatusBar is visible during the startup gate', async () => {
    vi.stubGlobal('fetch', makeFetchStub(false))

    render(<App />)
    await flushMicrotasks()

    // StatusBar always renders the "New chat" button.
    expect(screen.getByRole('button', { name: /new chat/i })).toBeInTheDocument()
  })

  it('Test 4: sending a message shows typing indicator then appends the response', async () => {
    let resolveChatRequest!: () => void
    const chatPending = new Promise<void>((res) => { resolveChatRequest = res })

    const fetchMock = vi.fn(async (url: string) => {
      if ((url as string).includes('/health')) {
        return {
          ok: true,
          json: async () => ({ status: 'ok', initial_ingestion_complete: true }),
        }
      }
      if ((url as string).includes('/ingest/status')) {
        return {
          ok: true,
          json: async () => ({
            files_processed: 5,
            files_failed: 0,
            files_skipped: 0,
            last_run: null,
          }),
        }
      }
      if ((url as string).includes('/chat')) {
        await chatPending
        return {
          ok: true,
          json: async () => ({
            answer: 'The sky is blue.',
            sources: ['weather.pdf'],
            session_id: 'abc',
          }),
        }
      }
      throw new Error('unexpected fetch: ' + url)
    })
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await flushMicrotasks()

    const textarea = screen.getByRole('textbox')

    // Type a question and press Enter using fireEvent (works reliably with fake timers).
    await act(async () => {
      fireEvent.change(textarea, { target: { value: 'What color is the sky?' } })
    })
    await act(async () => {
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter', charCode: 13 })
    })
    await flushMicrotasks()

    // While the chat request is pending, the typing indicator must be visible.
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument()

    // Resolve the chat request and flush React updates.
    await act(async () => {
      resolveChatRequest()
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(screen.getByText('The sky is blue.')).toBeInTheDocument()
    expect(screen.getByText(/weather\.pdf/i)).toBeInTheDocument()
    expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument()
  })

  it('Test 5: chat API failure shows inline error bubble and re-enables the input', async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if ((url as string).includes('/health')) {
        return {
          ok: true,
          json: async () => ({ status: 'ok', initial_ingestion_complete: true }),
        }
      }
      if ((url as string).includes('/ingest/status')) {
        return {
          ok: true,
          json: async () => ({
            files_processed: 0,
            files_failed: 0,
            files_skipped: 0,
            last_run: null,
          }),
        }
      }
      if ((url as string).includes('/chat')) {
        throw new Error('network error')
      }
      throw new Error('unexpected fetch: ' + url)
    })
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await flushMicrotasks()

    const textarea = screen.getByRole('textbox')

    await act(async () => {
      fireEvent.change(textarea, { target: { value: 'Will this fail?' } })
    })
    await act(async () => {
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter', charCode: 13 })
      await Promise.resolve()
      await Promise.resolve()
    })

    // Error message bubble should be visible and textarea should be re-enabled.
    expect(screen.getByText(/request failed/i)).toBeInTheDocument()
    expect(screen.getByRole('textbox')).not.toBeDisabled()
  })

  it('Test 6: New chat clears the visible message list', async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if ((url as string).includes('/health')) {
        return {
          ok: true,
          json: async () => ({ status: 'ok', initial_ingestion_complete: true }),
        }
      }
      if ((url as string).includes('/ingest/status')) {
        return {
          ok: true,
          json: async () => ({
            files_processed: 0,
            files_failed: 0,
            files_skipped: 0,
            last_run: null,
          }),
        }
      }
      if ((url as string).includes('/chat')) {
        return {
          ok: true,
          json: async () => ({
            answer: 'Some answer',
            sources: [],
            session_id: 'abc',
          }),
        }
      }
      throw new Error('unexpected fetch: ' + url)
    })
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)
    await flushMicrotasks()

    const textarea = screen.getByRole('textbox')

    // Send a message so there is at least one visible bubble.
    await act(async () => {
      fireEvent.change(textarea, { target: { value: 'First question' } })
    })
    await act(async () => {
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter', charCode: 13 })
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(screen.getByText('First question')).toBeInTheDocument()

    // Click "New chat".
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /new chat/i }))
    })

    expect(screen.queryByText('First question')).not.toBeInTheDocument()
    expect(screen.getByRole('textbox')).not.toBeDisabled()
  })
})
