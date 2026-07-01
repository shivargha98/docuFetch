// Scrollable chat window that renders all messages and auto-scrolls to the
// bottom when new messages arrive or the loading state activates.

import { useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import type { Message } from '../types/message'

interface ChatWindowProps {
  messages: Message[]
  isLoading: boolean
}

/**
 * Renders a scrollable list of MessageBubble components. Appends a TypingIndicator
 * when isLoading is true. Auto-scrolls to bottom on new messages or loading changes.
 */
export default function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, isLoading])

  return (
    <div
      className="flex-1 overflow-y-auto"
      style={{ background: 'var(--bg)' }}
    >
      <div className="max-w-3xl mx-auto px-4 py-6 flex flex-col gap-1">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
