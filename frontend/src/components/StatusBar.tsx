// StatusBar component — displays the current ingested document count and the timestamp
// of the last ingestion run, plus a "New chat" button to reset the conversation.

import React from 'react';

interface StatusBarProps {
  docCount: number;
  lastRunAt: string | null;
  onNewChat: () => void;
}

/**
 * Renders a thin status bar showing how many documents are indexed and when the last
 * ingestion ran. Displays "Never" when lastRunAt is null. Calls onNewChat when the
 * "New chat" button is clicked.
 */
function StatusBar({ docCount, lastRunAt, onNewChat }: StatusBarProps): React.ReactElement {
  /** Formats lastRunAt as a locale string, or returns "Never" when null. */
  function formatLastRun(lastRun: string | null): string {
    if (!lastRun) return 'Never';
    const d = new Date(lastRun);
    return isNaN(d.getTime()) ? 'Never' : d.toLocaleString();
  }

  return (
    <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200 text-sm text-gray-600">
      <span>Docs: {docCount} | Last indexed: {formatLastRun(lastRunAt)}</span>
      <button
        className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 text-sm"
        onClick={onNewChat}
      >
        New chat
      </button>
    </div>
  );
}

export default StatusBar;
