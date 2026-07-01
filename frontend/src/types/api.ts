// TypeScript interfaces mirroring the FastAPI backend response/request shapes exactly.
// Field names must remain in sync with the backend API contracts.

export interface ChatRequest {
  query: string;
  session_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  session_id: string;
}

export interface HealthResponse {
  status: string;
  initial_ingestion_complete: boolean;
}

export interface IngestStatusResponse {
  doc_count: number;
  last_run_at: string | null;
  last_error: string | null;
}
