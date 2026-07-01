// Renders an animated typing indicator in the style of an assistant message bubble.
// Shows three staggered bouncing dots to signal the assistant is generating a response.

/**
 * Displays three animated dots with staggered bounce delays,
 * styled as an assistant-side bubble. Used to indicate the assistant is typing.
 */
export default function TypingIndicator() {
  return (
    <div data-testid="typing-indicator" className="flex mb-3 justify-start">
      <div className="bg-gray-100 px-4 py-3 rounded-lg">
        <div className="flex gap-1">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  )
}
