// Thin fetch-based client wrapping the three backend endpoints used by the frontend.
// All functions throw on non-2xx responses; network errors propagate naturally.

import type { ChatResponse, HealthResponse, IngestStatusResponse } from '../types/api';

const BASE_URL = 'http://localhost:8000';

/**
 * Sends a chat query to the backend and returns the model's answer with source citations.
 * Body is sent as JSON with field names matching the backend ChatRequest schema.
 */
export async function postChat(query: string, sessionId: string): Promise<ChatResponse> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId }),
  });
  if (!response.ok) {
    throw new Error('Request failed: ' + response.status);
  }
  return response.json() as Promise<ChatResponse>;
}

/**
 * Fetches the backend health status, including whether initial ingestion has completed.
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Request failed: ' + response.status);
  }
  return response.json() as Promise<HealthResponse>;
}

/**
 * Fetches the current ingestion status — counts of processed, failed, and skipped files
 * plus the timestamp of the last ingestion run.
 */
export async function getIngestStatus(): Promise<IngestStatusResponse> {
  const response = await fetch(`${BASE_URL}/ingest/status`);
  if (!response.ok) {
    throw new Error('Request failed: ' + response.status);
  }
  return response.json() as Promise<IngestStatusResponse>;
}
