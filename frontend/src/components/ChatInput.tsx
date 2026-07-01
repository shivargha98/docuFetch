// ChatInput component — renders an auto-growing textarea with a send button.
// Calls onSend with the trimmed text on Enter (without Shift); Shift+Enter inserts a newline.
// Disables both textarea and button while isLoading is true.

import { useRef, useState } from 'react'

interface ChatInputProps {
  onSend: (text: string) => void
  isLoading: boolean
}

/**
 * ChatInput renders a controlled textarea that grows vertically as the user types,
 * plus a Send button. Pressing Enter submits; Shift+Enter adds a newline.
 */
export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  /**
   * Handles textarea input: resizes the element to fit its content, then updates state.
   */
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const el = e.target
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
    setValue(e.target.value)
  }

  /**
   * Handles keydown events: Enter submits the message; Shift+Enter inserts a newline.
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      const trimmed = value.trim()
      if (trimmed) {
        onSend(trimmed)
        setValue('')
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto'
        }
      }
    }
  }

  /**
   * Handles the Send button click: trims the value and calls onSend if non-empty.
   */
  const handleSend = () => {
    const trimmed = value.trim()
    if (trimmed) {
      onSend(trimmed)
      setValue('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  return (
    <div className="flex items-end gap-2 p-4 border-t border-gray-200">
      <textarea
        ref={textareaRef}
        value={value}
        rows={1}
        disabled={isLoading}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        className="flex-1 resize-none overflow-hidden rounded-lg border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <button
        onClick={handleSend}
        disabled={isLoading}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </div>
  )
}
