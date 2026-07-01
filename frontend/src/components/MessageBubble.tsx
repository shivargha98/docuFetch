// Renders a single chat message. User messages appear as right-aligned accent-colored
// pills. Assistant messages appear left-aligned with a subtle source-file citation block
// in monospace below the answer. Error messages appear left-aligned in muted red.

import { stripCitations } from '../utils/sources'
import type { Message } from '../types/message'

interface MessageBubbleProps {
  message: Message
}

/**
 * Role-differentiated bubble component.
 * - user: right-aligned, accent background
 * - assistant: left-aligned, surface-2 background, with optional sources chips
 * - error: left-aligned, error styling
 */
export default function MessageBubble({ message }: MessageBubbleProps) {
  const { role, text, sources } = message
  const isUser = role === 'user'
  const isAssistant = role === 'assistant'

  const displayText = isAssistant ? stripCitations(text) : text
  const hasSources = isAssistant && sources && sources.length > 0

  if (isUser) {
    return (
      <div className="flex justify-end mb-2">
        <div
          className="px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed max-w-[75%] whitespace-pre-wrap"
          style={{
            background: 'var(--user-bg)',
            color: 'var(--user-text)',
          }}
          data-role="user"
        >
          {displayText}
        </div>
      </div>
    )
  }

  if (isAssistant) {
    return (
      <div className="flex justify-start mb-4">
        <div className="flex flex-col gap-2 max-w-[80%]">
          <div
            className="px-4 py-3 rounded-2xl rounded-tl-sm text-sm leading-relaxed whitespace-pre-wrap"
            style={{
              background: 'var(--asst-bg)',
              color: 'var(--asst-text)',
            }}
            data-role="assistant"
          >
            {displayText}
          </div>
          {hasSources && (
            <div className="flex flex-wrap gap-1.5 pl-1">
              {sources!.map((src) => (
                <span
                  key={src}
                  className="font-mono text-xs px-2 py-0.5 rounded-full"
                  style={{
                    background: 'var(--accent-light)',
                    color: 'var(--accent)',
                  }}
                >
                  {src}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  // error role
  return (
    <div className="flex justify-start mb-2">
      <div
        className="px-4 py-2.5 rounded-2xl text-sm leading-relaxed max-w-[80%] whitespace-pre-wrap"
        style={{
          background: 'var(--err-bg)',
          color: 'var(--err-text)',
          border: '1px solid var(--err-border)',
        }}
        data-role="error"
      >
        {displayText}
      </div>
    </div>
  )
}
