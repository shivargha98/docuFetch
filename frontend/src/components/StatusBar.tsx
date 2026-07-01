// StatusBar — always-visible header bar. Shows the docuFetch brand on the left,
// a doc-count badge in the center, and a theme toggle + New Chat button on the right.

import React from 'react'

interface StatusBarProps {
  docCount: number
  lastRunAt: string | null
  dark: boolean
  onToggleDark: () => void
  hasMessages: boolean
  onNewChat: () => void
}

function SunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  )
}

function DocIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  )
}

/**
 * Renders the top header bar with brand, status, and controls.
 * The "New chat" button only appears when there are messages to clear.
 */
export default function StatusBar({ docCount, dark, onToggleDark, hasMessages, onNewChat }: StatusBarProps): React.ReactElement {
  return (
    <header
      className="flex items-center justify-between px-4 sm:px-6 h-12 shrink-0"
      style={{
        background: 'var(--surface)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      {/* Brand */}
      <div className="flex items-center gap-2">
        <span className="text-lg" role="img" aria-label="docuFetch">✦</span>
        <span
          className="font-display font-semibold text-sm tracking-wide"
          style={{ color: 'var(--text)' }}
        >
          docuFetch
        </span>
      </div>

      {/* Doc count badge */}
      <div
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono"
        style={{
          background: 'var(--accent-light)',
          color: 'var(--accent)',
        }}
      >
        <DocIcon />
        <span>{docCount} {docCount === 1 ? 'doc' : 'docs'}</span>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        {hasMessages && (
          <button
            onClick={onNewChat}
            className="px-3 py-1 rounded-lg text-xs font-medium transition-colors"
            style={{
              background: 'var(--surface-2)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border)',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = 'var(--text)')}
            onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            New chat
          </button>
        )}
        <button
          onClick={onToggleDark}
          title={dark ? 'Switch to light mode' : 'Switch to dark mode'}
          className="w-8 h-8 flex items-center justify-center rounded-lg transition-colors"
          style={{
            background: 'var(--surface-2)',
            color: 'var(--text-muted)',
            border: '1px solid var(--border)',
          }}
          onMouseEnter={e => (e.currentTarget.style.color = 'var(--text)')}
          onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
        >
          {dark ? <SunIcon /> : <MoonIcon />}
        </button>
      </div>
    </header>
  )
}
