// useChat hook — owns all chat state: message list, loading indicator, session ID,
// localStorage persistence, and error handling. Calls postChat from the API client
// and exposes sendMessage / resetChat to the UI.

import { useState } from 'react'
import { postChat } from '../api/client'
import type { Message } from '../types/message'

const SESSION_KEY = 'docufetch_session_id'
const MESSAGES_KEY = 'docufetch_messages'
const MESSAGE_CAP = 20

/** Shape returned by the useChat hook. */
interface UseChatReturn {
  messages: Message[]
  isLoading: boolean
  sendMessage: (query: string) => Promise<void>
  resetChat: () => void
}

/**
 * Reads the session ID from localStorage or generates a new UUID4 and persists it.
 * Returns the session ID string.
 */
function initSessionId(): string {
  const existing = localStorage.getItem(SESSION_KEY)
  if (existing) return existing
  const newId = crypto.randomUUID()
  localStorage.setItem(SESSION_KEY, newId)
  return newId
}

/**
 * Reads the persisted message list from localStorage and returns it, capped at
 * MESSAGE_CAP entries. Returns an empty array if nothing is stored or parsing fails.
 */
function initMessages(): Message[] {
  try {
    const stored = localStorage.getItem(MESSAGES_KEY)
    if (!stored) return []
    const parsed = JSON.parse(stored) as Message[]
    return parsed.slice(-MESSAGE_CAP)
  } catch {
    return []
  }
}

/**
 * Saves the most recent MESSAGE_CAP messages to localStorage.
 */
function persistMessages(msgs: Message[]): void {
  const capped = msgs.slice(-MESSAGE_CAP)
  localStorage.setItem(MESSAGES_KEY, JSON.stringify(capped))
}

/**
 * useChat — manages conversation state for the docuFetch chat UI.
 *
 * Provides:
 *  - messages: the current list of Message objects
 *  - isLoading: true while a backend request is in flight
 *  - sendMessage(query): appends the user turn, calls the backend, appends the
 *    assistant reply (or an error entry on failure), and persists everything to
 *    localStorage
 *  - resetChat(): clears message history and generates a fresh session ID
 */
export default function useChat(): UseChatReturn {
  const [sessionId, setSessionId] = useState<string>(() => initSessionId())
  const [messages, setMessages] = useState<Message[]>(() => initMessages())
  const [isLoading, setIsLoading] = useState(false)

  /**
   * Appends the user's query as a message, calls the backend, then appends the
   * assistant response or an error message. Persists the updated list to
   * localStorage after each state change.
   */
  async function sendMessage(query: string): Promise<void> {
    setIsLoading(true)

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      text: query,
    }

    // Append user message and persist immediately so it shows before the response.
    setMessages((prev) => {
      const updated = [...prev, userMsg]
      persistMessages(updated)
      return updated
    })

    try {
      const response = await postChat(query, sessionId)
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: response.answer,
        sources: response.sources,
      }
      setMessages((prev) => {
        const updated = [...prev, assistantMsg]
        persistMessages(updated)
        return updated
      })
    } catch {
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: 'error',
        text: 'Request failed. Is the server running?',
      }
      setMessages((prev) => {
        const updated = [...prev, errorMsg]
        persistMessages(updated)
        return updated
      })
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Clears the conversation: generates a new session ID, resets the message
   * list to empty, and persists both changes to localStorage.
   */
  function resetChat(): void {
    const newId = crypto.randomUUID()
    setSessionId(newId)
    localStorage.setItem(SESSION_KEY, newId)
    setMessages([])
    persistMessages([])
  }

  return { messages, isLoading, sendMessage, resetChat }
}
