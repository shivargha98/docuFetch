// Hook that polls the backend /ingest/status endpoint every 60 seconds and exposes
// the most recently fetched document count and last-run timestamp. A failed poll
// leaves the previously-fetched values unchanged rather than resetting them.

import { useState, useEffect } from 'react';
import { getIngestStatus } from '../api/client';

interface UseIngestStatusReturn {
  docCount: number;
  lastRunAt: string | null;
}

/**
 * Polls getIngestStatus() immediately on mount and then every 60 seconds.
 * Returns the latest docCount (files_processed) and lastRunAt (last_run) values.
 * A failed poll silently retains the previous values; the interval is cleared on unmount.
 */
export function useIngestStatus(): UseIngestStatusReturn {
  const [docCount, setDocCount] = useState<number>(0);
  const [lastRunAt, setLastRunAt] = useState<string | null>(null);

  useEffect(() => {
    /** Fetches ingest status and updates state; ignores errors to preserve prior values. */
    async function poll(): Promise<void> {
      try {
        const data = await getIngestStatus();
        setDocCount(data.files_processed);
        setLastRunAt(data.last_run);
      } catch {
        // Leave previous values unchanged on failure
      }
    }

    poll();
    const id = setInterval(poll, 60000);
    return () => clearInterval(id);
  }, []);

  return { docCount, lastRunAt };
}
