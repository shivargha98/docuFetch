// Scrollable chat window that renders all messages and optionally shows a typing
// indicator at the bottom. Auto-scrolls to the bottom when new messages arrive
// or when the loading state becomes active.

import { useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import type { Message } from '../types/message'

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
}

/**
 * Renders a scrollable list of MessageBubble components, one per message.
 * Appends a TypingIndicator after the last bubble when isLoading is true.
 * Auto-scrolls to the bottom whenever messages.length changes or isLoading becomes true.
 */
export default function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, isLoading])

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
