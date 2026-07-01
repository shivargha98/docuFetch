// ChatInput — auto-growing textarea with an integrated send button. Supports two
// variants: "landing" (centered, breathing glow border) and "chat" (bottom-pinned,
// separated by a top border). Enter submits; Shift+Enter inserts a newline.

import { useRef, useState, useEffect } from 'react'

interface ChatInputProps {
  onSend: (text: string) => void
  isLoading: boolean
  variant?: 'landing' | 'chat'
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="19" x2="12" y2="5" />
      <polyline points="5 12 12 5 19 12" />
    </svg>
  )
}

/**
 * Renders a controlled auto-growing textarea with an integrated send button.
 * In "landing" variant, the container has a breathing glow animation and no border-top.
 * In "chat" variant, it sits in a bar with a top separator.
 */
export default function ChatInput({ onSend, isLoading, variant = 'chat' }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-focus on mount in landing mode
  useEffect(() => {
    if (variant === 'landing') {
      textareaRef.current?.focus()
    }
  }, [variant])

  /** Resets textarea height after send. */
  function resetHeight() {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  /** Grows the textarea to fit content. */
  function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    const el = e.target
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
    setValue(e.target.value)
  }

  /** Enter submits; Shift+Enter inserts a newline. */
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    const trimmed = value.trim()
    if (!trimmed || isLoading) return
    onSend(trimmed)
    setValue('')
    resetHeight()
  }

  const canSend = value.trim().length > 0 && !isLoading

  if (variant === 'landing') {
    return (
      <div
        className="relative rounded-2xl anim-breathe transition-shadow"
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
        }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          rows={1}
          disabled={isLoading}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your documents…"
          className="w-full resize-none bg-transparent px-5 py-4 pr-14 text-base leading-relaxed focus:outline-none disabled:opacity-50"
          style={{
            color: 'var(--text)',
            maxHeight: '200px',
            overflowY: 'auto',
          }}
        />
        <button
          onClick={submit}
          disabled={!canSend}
          title="Send (Enter)"
          className="absolute right-3 bottom-3 w-9 h-9 flex items-center justify-center rounded-xl transition-all duration-150"
          style={{
            background: canSend ? 'var(--accent)' : 'var(--surface-2)',
            color: canSend ? '#FFFFFF' : 'var(--text-muted)',
          }}
        >
          <SendIcon />
        </button>
      </div>
    )
  }

  // variant === 'chat'
  return (
    <div
      className="px-4 py-3"
      style={{
        background: 'var(--surface)',
        borderTop: '1px solid var(--border)',
      }}
    >
      <div
        className="relative flex items-end rounded-xl max-w-3xl mx-auto"
        style={{
          background: 'var(--surface-2)',
          border: '1px solid var(--border)',
        }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          rows={1}
          disabled={isLoading}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask a follow-up…"
          className="flex-1 resize-none bg-transparent px-4 py-3 pr-12 text-sm leading-relaxed focus:outline-none disabled:opacity-50"
          style={{
            color: 'var(--text)',
            maxHeight: '160px',
            overflowY: 'auto',
          }}
        />
        <button
          onClick={submit}
          disabled={!canSend}
          title="Send (Enter)"
          className="absolute right-2.5 bottom-2.5 w-7 h-7 flex items-center justify-center rounded-lg transition-all duration-150"
          style={{
            background: canSend ? 'var(--accent)' : 'transparent',
            color: canSend ? '#FFFFFF' : 'var(--text-muted)',
          }}
        >
          <SendIcon />
        </button>
      </div>
      <p className="text-center text-xs mt-1.5" style={{ color: 'var(--text-muted)', opacity: 0.6 }}>
        Enter to send · Shift+Enter for newline
      </p>
    </div>
  )
}
