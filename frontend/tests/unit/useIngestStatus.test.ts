// Unit tests for the useIngestStatus hook — covers initial poll, subsequent poll updates,
// failed-poll value preservation, and interval cleanup on unmount.

import { renderHook, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useIngestStatus } from '../../src/hooks/useIngestStatus';

function makeFetchResponse(body: object): Response {
  return {
    ok: true,
    json: () => Promise.resolve(body),
  } as unknown as Response;
}

/** Flushes pending promise microtasks without advancing fake timers. */
async function flushPromises(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
  });
}

describe('useIngestStatus', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('docCount and lastRunAt are populated from the first poll', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        makeFetchResponse({
          files_processed: 7,
          files_failed: 0,
          files_skipped: 0,
          last_run: '2026-07-01T10:00:00Z',
        }),
      ),
    );

    const { result } = renderHook(() => useIngestStatus());

    // Let the initial poll's promises resolve
    await flushPromises();

    expect(result.current.docCount).toBe(7);
    expect(result.current.lastRunAt).toBe('2026-07-01T10:00:00Z');
  });

  it('values update after a subsequent poll', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        makeFetchResponse({
          files_processed: 7,
          files_failed: 0,
          files_skipped: 0,
          last_run: '2026-07-01T10:00:00Z',
        }),
      )
      .mockResolvedValue(
        makeFetchResponse({
          files_processed: 12,
          files_failed: 0,
          files_skipped: 0,
          last_run: '2026-07-01T11:00:00Z',
        }),
      );

    vi.stubGlobal('fetch', fetchMock);

    const { result } = renderHook(() => useIngestStatus());

    // First poll fires immediately — flush promises
    await flushPromises();
    expect(result.current.docCount).toBe(7);

    // Advance 60s to trigger the second poll, then flush its promises
    await act(async () => {
      vi.advanceTimersByTime(60000);
      await Promise.resolve();
    });

    expect(result.current.docCount).toBe(12);
  });

  it('a failed poll leaves previous values unchanged', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        makeFetchResponse({
          files_processed: 5,
          files_failed: 0,
          files_skipped: 0,
          last_run: '2026-07-01T10:00:00Z',
        }),
      )
      .mockRejectedValue(new Error('network error'));

    vi.stubGlobal('fetch', fetchMock);

    const { result } = renderHook(() => useIngestStatus());

    // First poll succeeds
    await flushPromises();
    expect(result.current.docCount).toBe(5);

    // Second poll fails — values must remain at 5
    await act(async () => {
      vi.advanceTimersByTime(60000);
      await Promise.resolve();
    });

    expect(result.current.docCount).toBe(5);
  });

  it('polling interval is cleared on unmount — no additional fetch fires after unmount', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      makeFetchResponse({
        files_processed: 3,
        files_failed: 0,
        files_skipped: 0,
        last_run: null,
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const { unmount } = renderHook(() => useIngestStatus());

    // Allow the initial poll to complete
    await flushPromises();
    const callCountAfterMount = fetchMock.mock.calls.length;

    unmount();

    // Advance well past one interval — no extra calls should fire
    await act(async () => {
      vi.advanceTimersByTime(120000);
      await Promise.resolve();
    });

    expect(fetchMock.mock.calls.length).toBe(callCountAfterMount);
  });
});
