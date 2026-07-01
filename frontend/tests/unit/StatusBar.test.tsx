// Unit tests for the StatusBar component — covers doc count display, last-run formatting,
// "Never" fallback, New chat button callback, and zero-state rendering.

import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import StatusBar from '../../src/components/StatusBar';

describe('StatusBar', () => {
  it('displays the current document count', () => {
    render(<StatusBar docCount={42} lastRunAt={null} onNewChat={vi.fn()} />);
    expect(screen.getByText(/42/)).toBeInTheDocument();
  });

  it('displays the last ingestion time as a human-readable string', () => {
    render(
      <StatusBar docCount={0} lastRunAt="2026-07-01T10:00:00Z" onNewChat={vi.fn()} />,
    );
    // The raw ISO string should not appear and "Never" should not appear
    expect(screen.queryByText('Never')).not.toBeInTheDocument();
    // A formatted date string from toLocaleString() should be present somewhere in the bar
    const formatted = new Date('2026-07-01T10:00:00Z').toLocaleString();
    expect(screen.getByText(new RegExp(formatted.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))).toBeInTheDocument();
  });

  it('displays "Never" when lastRunAt is null', () => {
    render(<StatusBar docCount={0} lastRunAt={null} onNewChat={vi.fn()} />);
    expect(screen.getByText(/Never/)).toBeInTheDocument();
  });

  it('clicking New chat calls the onNewChat handler exactly once', () => {
    const onNewChat = vi.fn();
    render(<StatusBar docCount={0} lastRunAt={null} onNewChat={onNewChat} />);
    fireEvent.click(screen.getByRole('button', { name: 'New chat' }));
    expect(onNewChat).toHaveBeenCalledTimes(1);
  });

  it('renders without error when docCount is 0 and lastRunAt is null', () => {
    render(<StatusBar docCount={0} lastRunAt={null} onNewChat={vi.fn()} />);
    expect(screen.getByText(/Docs: 0/)).toBeInTheDocument();
    expect(screen.getByText(/Never/)).toBeInTheDocument();
  });
});
