// Integration tests for the useHealthGate hook — verifies polling behaviour,
// ready-state transitions, error resilience, and interval cleanup on unmount.

import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, afterEach, beforeEach } from 'vitest'
import useHealthGate from '../../src/hooks/useHealthGate'

describe('useHealthGate', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('ready is false on initial render', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {}))) // never resolves
    const { result } = renderHook(() => useHealthGate())
    expect(result.current.ready).toBe(false)
  })

  it('ready becomes true after poll returns initial_ingestion_complete: true', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: 'ok', initial_ingestion_complete: true }),
      })
    )
    const { result } = renderHook(() => useHealthGate())
    await act(async () => {
      await vi.runAllTimersAsync()
    })
    expect(result.current.ready).toBe(true)
  })

  it('no further fetch calls are made after ready becomes true', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'ok', initial_ingestion_complete: true }),
    })
    vi.stubGlobal('fetch', mockFetch)
    const { result } = renderHook(() => useHealthGate())

    // Let the immediate poll resolve and mark ready
    await act(async () => {
      await vi.runAllTimersAsync()
    })
    expect(result.current.ready).toBe(true)

    const callsAfterReady = mockFetch.mock.calls.length

    // Advance another full interval — should fire no new fetch calls
    await act(async () => {
      await vi.advanceTimersByTimeAsync(3000)
    })
    expect(mockFetch.mock.calls.length).toBe(callsAfterReady)
  })

  it('a failed health poll keeps ready false without showing an error state', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))
    const { result } = renderHook(() => useHealthGate())
    // Advance a few intervals — hook must not transition to ready despite repeated polls
    await act(async () => {
      await vi.advanceTimersByTimeAsync(9000)
    })
    expect(result.current.ready).toBe(false)
    // Confirm no unexpected property leaks from the hook
    expect(Object.keys(result.current)).toEqual(['ready'])
  })

  it('polling interval is cleared on unmount', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'ok', initial_ingestion_complete: false }),
    })
    vi.stubGlobal('fetch', mockFetch)
    const { unmount } = renderHook(() => useHealthGate())

    // Let the immediate poll fire
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0)
    })

    const callsBeforeUnmount = mockFetch.mock.calls.length
    unmount()

    // Advance past the poll interval — no new calls should happen after unmount
    await act(async () => {
      await vi.advanceTimersByTimeAsync(9000)
    })
    expect(mockFetch.mock.calls.length).toBe(callsBeforeUnmount)
  })
})
