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
  files_processed: number;
  files_failed: number;
  files_skipped: number;
  last_run: string | null;
}
