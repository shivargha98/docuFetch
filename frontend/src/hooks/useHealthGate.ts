// useHealthGate — polling hook that watches GET /health every 3 seconds
// and exposes a `ready` boolean that becomes true once initial ingestion is complete.

import { useState, useEffect, useRef } from 'react'
import { getHealth } from '../api/client'

interface UseHealthGateReturn {
  ready: boolean
}

/**
 * Polls the backend /health endpoint every 3 seconds.
 * Sets `ready` to true when `initial_ingestion_complete` is true in the response,
 * then stops polling. Silently catches errors and retries on the next interval.
 * Clears the interval on unmount to prevent memory leaks.
 */
export default function useHealthGate(): UseHealthGateReturn {
  const [ready, setReady] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    /**
     * Fires a single health check. If ingestion is complete, marks ready and
     * stops the polling interval. Errors are swallowed so the next poll fires.
     */
    const poll = async () => {
      try {
        const result = await getHealth()
        if (result.initial_ingestion_complete) {
          setReady(true)
          if (intervalRef.current !== null) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      } catch {
        // stay not-ready, next poll will retry
      }
    }

    poll() // immediate first poll
    intervalRef.current = setInterval(poll, 3000)

    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [])

  return { ready }
}
