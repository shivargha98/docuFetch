// App.tsx — root component that composes all hooks and components into the full
// single-page layout: a status bar, a startup gate while ingestion is in progress,
// and the chat window + input once the backend is ready.

import useHealthGate from './hooks/useHealthGate'
import useChat from './hooks/useChat'
import { useIngestStatus } from './hooks/useIngestStatus'
import StatusBar from './components/StatusBar'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'

/**
 * Shown instead of the chat UI while the backend has not yet completed its
 * initial ingestion. Disappears automatically once useHealthGate reports ready.
 */
function StartupGate() {
  return (
    <div className="flex-1 flex items-center justify-center text-gray-500">
      <div className="text-center">
        <div className="text-lg font-medium mb-2">Preparing your documents…</div>
        <div className="text-sm">Please wait while the index is being built.</div>
      </div>
    </div>
  )
}

/**
 * App — top-level component that wires together all hooks and renders the full UI.
 *
 * Layout:
 *  - StatusBar is always visible at the top.
 *  - While ready is false, StartupGate fills the remaining space.
 *  - Once ready is true, ChatWindow (scrollable) and ChatInput (pinned bottom) appear.
 */
function App() {
  const { ready } = useHealthGate()
  const { messages, isLoading, sendMessage, resetChat } = useChat()
  const { docCount, lastRunAt } = useIngestStatus()

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <StatusBar docCount={docCount} lastRunAt={lastRunAt} onNewChat={resetChat} />
      {!ready ? (
        <StartupGate />
      ) : (
        <>
          <ChatWindow messages={messages} isLoading={isLoading} />
          <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </>
      )}
    </div>
  )
}

export default App
