// App.tsx — root component. Manages theme (dark/light), IST-based greeting, and the
// two-state layout: a centered landing view before the first message, and a full
// chat view once conversation begins. Theme preference is persisted to localStorage.

import { useState, useEffect, useMemo } from 'react'
import useHealthGate from './hooks/useHealthGate'
import useChat from './hooks/useChat'
import { useIngestStatus } from './hooks/useIngestStatus'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'
import StatusBar from './components/StatusBar'

/** Computes a time-appropriate greeting in IST (UTC+5:30). */
function getGreeting(): string {
  const utcMs = Date.now() + new Date().getTimezoneOffset() * 60000
  const h = new Date(utcMs + 5.5 * 3600000).getHours()
  if (h >= 5 && h < 12) return 'Good morning'
  if (h >= 12 && h < 17) return 'Good afternoon'
  if (h >= 17 && h < 21) return 'Good evening'
  return 'Good night'
}

/** Formats an ISO timestamp as a human-relative string ("3m ago", "2h ago"). */
function formatRelative(ts: string | null): string {
  if (!ts) return ''
  const d = new Date(ts)
  if (isNaN(d.getTime())) return ''
  const diffMin = Math.floor((Date.now() - d.getTime()) / 60000)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffH = Math.floor(diffMin / 60)
  if (diffH < 24) return `${diffH}h ago`
  return d.toLocaleDateString()
}

// ─── Sub-components ──────────────────────────────────────────────────────────

interface LandingViewProps {
  greeting: string
  docCount: number
  lastRunAt: string | null
  onSend: (text: string) => void
  isLoading: boolean
}

/**
 * Full-page centered view shown before the first message. Displays an IST-based
 * greeting, subtitle, the chat input with a breathing glow border, and a subtle
 * doc count hint below the input.
 */
function LandingView({ greeting, docCount, lastRunAt, onSend, isLoading }: LandingViewProps) {
  const indexedAt = formatRelative(lastRunAt)
  return (
    <div
      className="flex-1 flex flex-col items-center justify-center px-4 landing-glow anim-fade-in"
    >
      {/* Greeting block */}
      <div className="text-center mb-10 anim-fade-up">
        <h1 className="font-display text-4xl sm:text-5xl font-semibold mb-3 leading-tight" style={{ color: 'var(--text)' }}>
          {greeting},{' '}
          <span className="gradient-name">Shivargha.</span>
        </h1>
        <p className="text-lg" style={{ color: 'var(--text-muted)' }}>
          What would you like to explore today?
        </p>
      </div>

      {/* Input */}
      <div className="w-full max-w-2xl anim-fade-up-2">
        <ChatInput onSend={onSend} isLoading={isLoading} variant="landing" />
      </div>

      {/* Subtle status hint */}
      <p className="mt-4 text-sm anim-fade-up-3" style={{ color: 'var(--text-muted)' }}>
        {docCount} {docCount === 1 ? 'doc' : 'docs'} indexed
        {indexedAt ? ` · last indexed ${indexedAt}` : ''}
      </p>
    </div>
  )
}

/** Startup gate shown while the backend completes its initial ingestion pass. */
function StartupGate() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 anim-fade-in">
      <div
        className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
        style={{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }}
      />
      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
        Preparing your documents…
      </p>
    </div>
  )
}

// ─── App ─────────────────────────────────────────────────────────────────────

/**
 * App — wires all hooks together and decides which layout to render:
 * StartupGate → LandingView → ChatView, based on backend readiness and message state.
 */
function App() {
  const [dark, setDark] = useState<boolean>(() => {
    return (localStorage.getItem('df-theme') ?? 'dark') === 'dark'
  })

  const { ready } = useHealthGate()
  const { messages, isLoading, sendMessage, resetChat } = useChat()
  const { docCount, lastRunAt } = useIngestStatus()
  const greeting = useMemo(() => getGreeting(), [])

  const hasMessages = messages.length > 0

  // Sync theme to <html> and localStorage whenever it changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
    localStorage.setItem('df-theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <div className="flex flex-col h-screen" style={{ background: 'var(--bg)' }}>
      <StatusBar
        docCount={docCount}
        lastRunAt={lastRunAt}
        dark={dark}
        onToggleDark={() => setDark(d => !d)}
        hasMessages={hasMessages}
        onNewChat={resetChat}
      />

      {!ready ? (
        <StartupGate />
      ) : !hasMessages ? (
        <LandingView
          greeting={greeting}
          docCount={docCount}
          lastRunAt={lastRunAt}
          onSend={sendMessage}
          isLoading={isLoading}
        />
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden anim-fade-in">
          <ChatWindow messages={messages} isLoading={isLoading} />
          <ChatInput onSend={sendMessage} isLoading={isLoading} variant="chat" />
        </div>
      )}
    </div>
  )
}

export default App
