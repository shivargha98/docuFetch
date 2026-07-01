// Renders a single chat message bubble. Handles user, assistant, and error roles
// with distinct styling. Assistant messages have citations stripped from display
// text and optionally show a sources block below the answer.

import { stripCitations } from '../utils/sources'
import type { Message } from '../types/message'

interface MessageBubbleProps {
  message: Message;
}

/**
 * Renders a single message bubble with role-appropriate styling.
 * User messages are right-aligned blue bubbles.
 * Assistant messages are left-aligned gray bubbles with optional sources block.
 * Error messages are left-aligned red/orange bubbles with no sources block.
 */
export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  const containerClass = `flex mb-3 ${isUser ? 'justify-end' : 'justify-start'}`

  const bubbleClass = isUser
    ? 'bg-blue-600 text-white px-4 py-2 rounded-lg max-w-[70%] whitespace-pre-wrap'
    : isAssistant
      ? 'bg-gray-100 text-gray-800 px-4 py-2 rounded-lg max-w-[70%] whitespace-pre-wrap'
      : 'bg-red-50 text-red-700 border border-red-200 px-4 py-2 rounded-lg max-w-[70%] whitespace-pre-wrap'

  const displayText = isAssistant ? stripCitations(message.text) : message.text
  const hasSources = isAssistant && message.sources && message.sources.length > 0

  return (
    <div className={containerClass}>
      <div data-role={message.role} className={bubbleClass}>
        {displayText}
        {hasSources && (
          <div className="mt-2 text-xs text-gray-500">
            <span className="font-semibold">Sources: </span>
            {message.sources!.join(', ')}
          </div>
        )}
      </div>
    </div>
  )
}
