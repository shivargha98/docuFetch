// Integration tests for the useChat hook — covers message appending, loading state,
// error handling, localStorage persistence, session ID management, and resetChat.

import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import useChat from '../../src/hooks/useChat'

/** Returns a mock fetch response that resolves with the given JSON body. */
function makeFetchResponse(body: object) {
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve(body),
  } as Response)
}

beforeEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
})

describe('useChat', () => {
  it('Test 1: sendMessage appends a user message immediately and an assistant message after resolution', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => makeFetchResponse({ answer: '42', sources: [], session_id: 'abc' }))
    )

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.sendMessage('What is the answer?')
    })

    const msgs = result.current.messages
    expect(msgs.some((m) => m.role === 'user' && m.text === 'What is the answer?')).toBe(true)
    expect(msgs.some((m) => m.role === 'assistant' && m.text === '42')).toBe(true)
  })

  it('Test 2: isLoading is true during the request and false after resolution', async () => {
    let resolveRequest!: (value: Response) => void
    const pendingResponse = new Promise<Response>((resolve) => {
      resolveRequest = resolve
    })
    vi.stubGlobal('fetch', vi.fn(() => pendingResponse))

    const { result } = renderHook(() => useChat())

    // Start sendMessage without awaiting so we can inspect mid-flight state.
    act(() => {
      result.current.sendMessage('question')
    })

    expect(result.current.isLoading).toBe(true)

    // Resolve the network call.
    await act(async () => {
      resolveRequest({
        ok: true,
        json: () => Promise.resolve({ answer: 'done', sources: [], session_id: 'x' }),
      } as Response)
    })

    expect(result.current.isLoading).toBe(false)
  })

  it('Test 3: API failure appends an error entry and resets isLoading to false', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('network'))))

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.sendMessage('question')
    })

    expect(result.current.messages.some((m) => m.role === 'error')).toBe(true)
    expect(result.current.isLoading).toBe(false)
  })

  it('Test 4: session ID is read from localStorage if one already exists', async () => {
    localStorage.setItem('docufetch_session_id', 'existing-uuid')

    const fetchMock = vi.fn(() =>
      makeFetchResponse({ answer: 'ok', sources: [], session_id: 'existing-uuid' })
    )
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useChat())

    await act(async () => {
      await result.current.sendMessage('hello')
    })

    const body = JSON.parse((fetchMock.mock.calls[0][1] as RequestInit).body as string)
    expect(body.session_id).toBe('existing-uuid')
  })

  it('Test 5: a new UUID4 is generated and saved to localStorage if no session ID exists', () => {
    renderHook(() => useChat())

    const stored = localStorage.getItem('docufetch_session_id')
    expect(stored).not.toBeNull()
    expect(stored).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    )
  })

  it('Test 6: message list is rehydrated from localStorage on mount', () => {
    localStorage.setItem(
      'docufetch_messages',
      JSON.stringify([
        { id: '1', role: 'user', text: 'hi' },
        { id: '2', role: 'assistant', text: 'hello', sources: [] },
      ])
    )

    const { result } = renderHook(() => useChat())

    expect(result.current.messages).toHaveLength(2)
  })

  it('Test 7: message list is capped at 20 entries', () => {
    const msgs = Array.from({ length: 21 }, (_, i) => ({
      id: String(i),
      role: 'user',
      text: `msg ${i}`,
    }))
    localStorage.setItem('docufetch_messages', JSON.stringify(msgs))

    const { result } = renderHook(() => useChat())

    expect(result.current.messages.length).toBeLessThanOrEqual(20)
  })

  it('Test 8: resetChat generates a fresh session ID and clears message list in localStorage', async () => {
    const originalId = 'original-session-id'
    localStorage.setItem('docufetch_session_id', originalId)
    localStorage.setItem(
      'docufetch_messages',
      JSON.stringify([
        { id: '1', role: 'user', text: 'hi' },
        { id: '2', role: 'assistant', text: 'hello', sources: [] },
      ])
    )

    const { result } = renderHook(() => useChat())

    act(() => {
      result.current.resetChat()
    })

    expect(result.current.messages).toHaveLength(0)
    expect(localStorage.getItem('docufetch_session_id')).not.toBe(originalId)
    expect(localStorage.getItem('docufetch_messages')).toBe('[]')
  })
})
