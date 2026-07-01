// Typing indicator — three dots with staggered bounce animation, styled to match
// the assistant bubble so it reads as a placeholder response in progress.

/**
 * Shows three animated dots in an assistant-styled bubble. Used while the backend
 * is generating a response.
 */
export default function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4" data-testid="typing-indicator">
      <div
        className="px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-1.5"
        style={{ background: 'var(--asst-bg)' }}
      >
        {[0, 150, 300].map((delay) => (
          <span
            key={delay}
            className="block w-2 h-2 rounded-full"
            style={{
              background: 'var(--text-muted)',
              animation: `dotBounce 1.2s ease-in-out ${delay}ms infinite`,
            }}
          />
        ))}
      </div>
    </div>
  )
}
