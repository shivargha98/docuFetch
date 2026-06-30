# Test Suite

_Generated from: prd.md, features.md, issues.md_

---

## Unit Tests

### Scanner (Change Detection)

#### Test: New file is classified as new
**Type:** Unit
**Source:** Feature: File Change Detection — criterion 1 | Issue 5 — criterion 1
**Given:** An empty `hash_store.json` and a folder containing one TXT file
**When:** The scanner runs and computes SHA256 hashes for all files
**Then:**
- [ ] The file is returned in the `new` list
- [ ] The file is NOT in the `modified` or `deleted` lists

---

#### Test: Modified file is classified as modified
**Type:** Unit
**Source:** Feature: File Change Detection — criterion 2 | Issue 5 — criterion 2
**Given:** A `hash_store.json` containing a file's old hash, and that file now has a different hash on disk
**When:** The scanner runs
**Then:**
- [ ] The file is returned in the `modified` list
- [ ] The file is NOT in the `new` or `deleted` lists

---

#### Test: Deleted file is classified as deleted
**Type:** Unit
**Source:** Feature: File Change Detection — criterion 3 | Issue 5 — criterion 3
**Given:** A `hash_store.json` containing a file record, but the file no longer exists on disk
**When:** The scanner runs
**Then:**
- [ ] The file is returned in the `deleted` list
- [ ] The file is NOT in the `new` or `modified` lists

---

#### Test: Unchanged file produces no action
**Type:** Unit
**Source:** Feature: File Change Detection — criterion 5
**Given:** A `hash_store.json` containing a file's hash, and the file on disk has the same hash
**When:** The scanner runs
**Then:**
- [ ] The file does not appear in `new`, `modified`, or `deleted` lists

---

#### Test: hash_store.json is updated after scan
**Type:** Unit
**Source:** Feature: File Change Detection — criterion 4
**Given:** A folder with one new file and one deleted file relative to `hash_store.json`
**When:** The scanner runs and the store is persisted
**Then:**
- [ ] The new file's SHA256 hash is written to `hash_store.json`
- [ ] The deleted file's entry is removed from `hash_store.json`

---

### Loaders

#### Test: PDF loader returns non-empty text string
**Type:** Unit
**Source:** Feature: Per-File-Type Document Loaders — criterion 1
**Given:** A valid PDF file with known text content
**When:** The PDF loader is called
**Then:**
- [ ] The return value is a non-empty string
- [ ] The returned string contains text from the PDF

---

#### Test: TXT loader returns raw text content
**Type:** Unit
**Source:** Feature: Per-File-Type Document Loaders — criterion 3
**Given:** A TXT file with known content
**When:** The TXT loader is called
**Then:**
- [ ] The returned string exactly matches the file's contents

---

#### Test: Markdown loader returns text preserving heading markers
**Type:** Unit
**Source:** Feature: Per-File-Type Document Loaders — criterion 2
**Given:** A Markdown file containing `#`, `##`, and `###` headers
**When:** The Markdown loader is called
**Then:**
- [ ] The returned string contains the `#` heading markers intact
- [ ] The returned string is a non-empty string

---

#### Test: Image loader returns raw bytes
**Type:** Unit
**Source:** Feature: Per-File-Type Document Loaders — criterion 4
**Given:** A valid JPEG file
**When:** The image loader is called
**Then:**
- [ ] The return value is a non-empty `bytes` object
- [ ] The same test passes for JPG and PNG files

---

#### Test: Unsupported file extension raises a clear error
**Type:** Unit
**Source:** Feature: Per-File-Type Document Loaders — criterion 5
**Given:** A file with an unsupported extension (e.g. `.docx`)
**When:** Any loader is called for this file
**Then:**
- [ ] A specific, named exception is raised (not a generic `Exception`)
- [ ] The exception message identifies the unsupported extension

---

### Chunkers

#### Test: Markdown chunks split at header boundaries
**Type:** Unit
**Source:** Feature: Structure-Aware Chunkers — criterion 1
**Given:** A Markdown string with three `##` sections
**When:** The Markdown chunker is applied
**Then:**
- [ ] Exactly three chunks are produced (one per section)
- [ ] No chunk contains content from more than one section

---

#### Test: PDF/TXT chunks do not exceed 512 characters
**Type:** Unit
**Source:** Feature: Structure-Aware Chunkers — criterion 2
**Given:** A long plain text string (well over 512 characters)
**When:** The RecursiveCharacterTextSplitter chunker is applied
**Then:**
- [ ] Every produced chunk is at most 512 characters in length

---

#### Test: Consecutive PDF/TXT chunks have 64-character overlap
**Type:** Unit
**Source:** Feature: Structure-Aware Chunkers — criterion 2
**Given:** A plain text string long enough to produce at least two chunks
**When:** The RecursiveCharacterTextSplitter chunker is applied
**Then:**
- [ ] The last 64 characters of chunk N match the first 64 characters of chunk N+1

---

#### Test: Image produces exactly one chunk
**Type:** Unit
**Source:** Feature: Structure-Aware Chunkers — criterion 3
**Given:** A JPEG image file
**When:** The image chunker is applied
**Then:**
- [ ] Exactly one chunk is returned regardless of file size

---

#### Test: Text chunks carry filename and file_type metadata
**Type:** Unit
**Source:** Feature: Structure-Aware Chunkers — criterion 4
**Given:** A TXT file named `notes.txt`
**When:** The TXT chunker produces chunks
**Then:**
- [ ] Each chunk's metadata contains `filename: "notes.txt"`
- [ ] Each chunk's metadata contains `file_type: "txt"`

---

#### Test: Image chunk carries file_path in metadata
**Type:** Unit
**Source:** Feature: Structure-Aware Chunkers — criterion 4 | Feature: ChromaDB Store Operations — criterion 2
**Given:** A PNG file at a known absolute path
**When:** The image chunker produces a chunk
**Then:**
- [ ] The chunk's metadata contains the exact `file_path` of the image
- [ ] The chunk's content field is empty or absent

---

### Retrieval (Unit)

#### Test: RRF score is computed correctly
**Type:** Unit
**Source:** Feature: Hybrid Retriever with RRF Fusion — criterion 3
**Given:** Two ranked lists with a shared document at rank 2 in list A and rank 1 in list B
**When:** RRF scores are computed with k=60
**Then:**
- [ ] The shared document's fused score equals `1/(2+60) + 1/(1+60)`
- [ ] The shared document scores higher than a document appearing in only one list

---

#### Test: BM25 ranks results by keyword relevance
**Type:** Unit
**Source:** Feature: BM25 Index — criterion 2
**Given:** A BM25 index built from three documents, one containing a specific rare keyword
**When:** A query using that keyword is run against the index
**Then:**
- [ ] The document containing the keyword is ranked first
- [ ] Results are returned in descending relevance order

---

### Graph Nodes (Unit)

#### Test: DocuFetchState can be instantiated with a subset of fields
**Type:** Unit
**Source:** Feature: LangGraph State Schema — criterion 2
**Given:** No precondition
**When:** `DocuFetchState` is instantiated with only `query` provided
**Then:**
- [ ] The instantiation succeeds without error
- [ ] Unspecified fields are absent or defaulted without raising a `KeyError`

---

#### Test: No-results node returns the exact no-results message
**Type:** Unit
**Source:** Feature: No-Results Node — criterion 1
**Given:** A `DocuFetchState` with `is_relevant=False` and `retrieved_chunks=[]`
**When:** The `no_results` node is invoked
**Then:**
- [ ] The returned state contains `answer` (or the last AIMessage) equal to `"I couldn't find relevant information in your documents."`

---

#### Test: No-results node sets sources to an empty list
**Type:** Unit
**Source:** Feature: No-Results Node — criterion 2
**Given:** A `DocuFetchState` with `is_relevant=False`
**When:** The `no_results` node is invoked
**Then:**
- [ ] `state["sources"]` is an empty list

---

#### Test: Relevance check node skips LLM call when retrieved_chunks is empty
**Type:** Unit
**Source:** Feature: Relevance Check Node — criterion 3
**Given:** A `DocuFetchState` with `retrieved_chunks=[]`
**When:** The `relevance_check` node is invoked with a mocked LLM client
**Then:**
- [ ] `is_relevant` is set to `False`
- [ ] The mocked LLM client is never called

---

### CLI (Unit)

#### Test: CLI reuses the same session_id across all queries in a session
**Type:** Unit
**Source:** Feature: Interactive CLI Client — criterion 5 | Issue 9 — criterion 2
**Given:** A CLI session started with a mocked `httpx` client
**When:** Two queries are submitted sequentially
**Then:**
- [ ] Both HTTP requests to `/chat` contain the same `session_id` value
- [ ] The `session_id` is a valid UUID4 format

---

#### Test: CLI prints human-readable error when server is unreachable
**Type:** Unit
**Source:** Feature: Interactive CLI Client — criterion 6 | Issue 9 — criterion 6
**Given:** `httpx` raises a `ConnectError` for all requests
**When:** The user submits a query
**Then:**
- [ ] The CLI prints a message containing the server URL and a readable description of the problem
- [ ] No raw exception traceback is printed
- [ ] The CLI does not crash (remains in the prompt loop or exits cleanly)

---

#### Test: /quit exits the CLI cleanly
**Type:** Unit
**Source:** Feature: Interactive CLI Client — criterion 4 | Issue 9 — criterion 5
**Given:** A running CLI prompt loop
**When:** The user types `/quit`
**Then:**
- [ ] The process exits with code 0
- [ ] No error is printed

---

---

## Integration Tests

### ChromaDB Store

#### Test: Insert text chunk and retrieve by vector query
**Type:** Integration
**Source:** Feature: ChromaDB Store Operations — criterion 1
**Given:** An empty ChromaDB collection (temp directory)
**When:** A text chunk with `filename` and `file_type` metadata is inserted, then a vector query is run with a similar embedding
**Then:**
- [ ] The inserted chunk is returned in the query results
- [ ] The returned chunk's metadata contains the original `filename` and `file_type` values

---

#### Test: Insert image chunk stores file_path in metadata with no content
**Type:** Integration
**Source:** Feature: ChromaDB Store Operations — criterion 2
**Given:** An empty ChromaDB collection
**When:** An image chunk is inserted with `file_path` metadata and no content
**Then:**
- [ ] The chunk is retrievable by vector query
- [ ] The returned chunk's metadata contains the exact `file_path`
- [ ] The returned chunk's document/content field is empty or absent

---

#### Test: Delete by filename removes all associated chunks
**Type:** Integration
**Source:** Feature: ChromaDB Store Operations — criterion 3
**Given:** A ChromaDB collection containing three chunks all with `filename: "report.pdf"`
**When:** Delete is called for `filename: "report.pdf"`
**Then:**
- [ ] A subsequent query returns no chunks with `filename: "report.pdf"`
- [ ] Chunks from other filenames are unaffected

---

#### Test: Vector query returns at most K results with metadata
**Type:** Integration
**Source:** Feature: ChromaDB Store Operations — criterion 4
**Given:** A ChromaDB collection containing 10 chunks
**When:** A vector query is run with `top_k=3`
**Then:**
- [ ] At most 3 chunks are returned
- [ ] Every returned chunk includes its metadata dict

---

### Ingestion Pipeline

#### Test: TXT file is ingested end-to-end into ChromaDB
**Type:** Integration
**Source:** Issue 2 — criteria 1, 3, 4 | Feature: Per-File-Type Document Loaders, Structure-Aware Chunkers
**Given:** A TXT file in the watch folder and a real ChromaDB instance (temp dir)
**When:** The full ingestion pipeline is run for that file
**Then:**
- [ ] At least one chunk exists in ChromaDB for that filename
- [ ] Each chunk's metadata contains `filename` and `file_type: "txt"`
- [ ] Running ingestion again for the same unchanged file produces no duplicate chunks

---

#### Test: PDF file is ingested end-to-end into ChromaDB
**Type:** Integration
**Source:** Issue 2 — criteria 1, 3, 4
**Given:** A PDF file in the watch folder
**When:** The full ingestion pipeline is run
**Then:**
- [ ] At least one chunk exists in ChromaDB for that filename
- [ ] Each chunk's metadata contains `filename` and `file_type: "pdf"`

---

#### Test: Markdown file chunks respect header boundaries in ChromaDB
**Type:** Integration
**Source:** Issue 3 — criteria 1, 2 | Feature: Structure-Aware Chunkers
**Given:** A Markdown file with three `##` sections
**When:** The Markdown ingestion pipeline runs
**Then:**
- [ ] ChromaDB contains exactly three chunks for the file
- [ ] Each chunk's content corresponds to one section only

---

#### Test: Image file produces a single chunk with file_path metadata
**Type:** Integration
**Source:** Issue 4 — criteria 1, 2 | Feature: Structure-Aware Chunkers
**Given:** A JPEG file in the watch folder
**When:** The image ingestion pipeline runs
**Then:**
- [ ] Exactly one chunk exists in ChromaDB for that filename
- [ ] The chunk's metadata contains `file_path` and `file_type: "image"`
- [ ] The chunk has no content field (or an empty one)

---

#### Test: Ingesting a modified file replaces old chunks
**Type:** Integration
**Source:** Feature: File Change Detection — criterion 2 | Issue 5 — criterion 2
**Given:** A TXT file that has been ingested, then its content changes (new hash)
**When:** The scanner detects the modification and the ingestion pipeline re-runs for that file
**Then:**
- [ ] The old chunks (pre-modification) are absent from ChromaDB
- [ ] New chunks (post-modification content) are present in ChromaDB
- [ ] No duplicate chunks for that filename exist

---

### BM25 and Hybrid Retrieval

#### Test: BM25 index contains no image chunks
**Type:** Integration
**Source:** Feature: BM25 Index — criterion 3 | Feature: Hybrid Retriever with RRF Fusion — criterion 4
**Given:** A ChromaDB collection with both text and image chunks ingested
**When:** The BM25 index is built from ChromaDB text chunks
**Then:**
- [ ] A BM25 query for any term never returns an image chunk
- [ ] The BM25 index document count equals the number of text chunks only

---

#### Test: BM25 index is rebuilt after ingestion and includes new documents
**Type:** Integration
**Source:** Feature: BM25 Index — criterion 4
**Given:** A BM25 index built from an initial set of documents
**When:** A new document is ingested and the index is rebuilt
**Then:**
- [ ] A BM25 keyword query matching the new document's content returns that document

---

#### Test: Hybrid retrieval returns at most 3 fused chunks
**Type:** Integration
**Source:** Feature: Hybrid Retriever with RRF Fusion — criterion 2
**Given:** A ChromaDB collection with 10+ ingested text chunks
**When:** The hybrid retriever is called with a query
**Then:**
- [ ] At most 3 chunks are returned
- [ ] All returned chunks have a `filename` in their metadata

---

#### Test: Document ranking high in both retrievers appears in top results
**Type:** Integration
**Source:** Feature: Hybrid Retriever with RRF Fusion — criterion 3
**Given:** Two documents ingested: one whose content exactly matches the query keyword AND semantic meaning, one that only semantically relates
**When:** The hybrid retriever is called with that keyword query
**Then:**
- [ ] The document with both keyword and semantic relevance is ranked first in the fused output

---

### RAG Pipeline (End-to-End)

#### Test: Query matching an ingested document returns an answer with source citation
**Type:** Integration
**Source:** Feature: LangGraph Graph Assembly — criterion 1 | PRD User Story 8, 9
**Given:** A TXT document with specific content is ingested; the LangGraph graph is compiled
**When:** The graph is invoked with a query that directly asks about that content
**Then:**
- [ ] The returned answer is between 2 and 4 sentences
- [ ] `sources` contains the filename of the ingested document
- [ ] The answer text includes a `[source: filename]` citation

---

#### Test: Query with no matching document returns the no-results message
**Type:** Integration
**Source:** Feature: LangGraph Graph Assembly — criterion 2 | PRD User Story 10
**Given:** A document about topic A is ingested; the LangGraph graph is compiled
**When:** The graph is invoked with a query about a completely unrelated topic B
**Then:**
- [ ] The returned answer is exactly `"I couldn't find relevant information in your documents."`
- [ ] `sources` is an empty list

---

#### Test: Two-turn conversation — second answer is contextually aware of first
**Type:** Integration
**Source:** Feature: LangGraph Graph Assembly — criterion 3 | PRD User Story 13
**Given:** An ingested document and a compiled graph; session state initialized with one prior exchange
**When:** The graph is invoked with a follow-up question that only makes sense given the prior turn
**Then:**
- [ ] The answer reflects awareness of the prior question (does not treat it as a standalone query)
- [ ] `messages` contains entries from both turns

---

#### Test: Session history is trimmed when it exceeds 20 messages
**Type:** Integration
**Source:** Feature: LangGraph Graph Assembly — criterion 4 | PRD User Story 13
**Given:** A `DocuFetchState` with a `messages` list of 22 entries
**When:** The graph is invoked (triggering the history trim step)
**Then:**
- [ ] The LLM is called with at most 20 messages in the context
- [ ] The oldest messages (entries 1 and 2) are absent from the trimmed list

---

---

## API / Contract Tests

### GET /health

#### Test: Health endpoint returns 200 with expected schema
**Type:** API
**Source:** Feature: GET /health Endpoint — criterion 1
**Given:** The FastAPI app is running (via TestClient)
**When:** `GET /health` is called
**Then:**
- [ ] HTTP status is 200
- [ ] Response body contains `"status": "ok"`
- [ ] Response body contains the key `"initial_ingestion_complete"` with a boolean value

---

#### Test: initial_ingestion_complete is false before startup ingestion
**Type:** API
**Source:** Feature: GET /health Endpoint — criterion 2
**Given:** The FastAPI app started with the scheduler disabled or not yet completed
**When:** `GET /health` is called immediately
**Then:**
- [ ] `"initial_ingestion_complete"` is `false`

---

#### Test: initial_ingestion_complete is true after startup ingestion completes
**Type:** API
**Source:** Feature: GET /health Endpoint — criterion 3
**Given:** The FastAPI app started and the startup ingestion run has completed
**When:** `GET /health` is called
**Then:**
- [ ] `"initial_ingestion_complete"` is `true`

---

### POST /ingest

#### Test: Manual ingest endpoint returns 200 with confirmation
**Type:** API
**Source:** Feature: POST /ingest Endpoint — criterion 1 | Issue 2 — criterion 1
**Given:** The FastAPI app is running
**When:** `POST /ingest` is called
**Then:**
- [ ] HTTP status is 200
- [ ] Response body contains a non-empty confirmation message string

---

#### Test: After POST /ingest, newly added files are queryable
**Type:** API
**Source:** Feature: POST /ingest Endpoint — criterion 3 | Issue 2 — criterion 4
**Given:** A new TXT file is placed in `WATCH_FOLDER` after server startup
**When:** `POST /ingest` is called, then `POST /chat` is called with a query matching the new file's content
**Then:**
- [ ] The `/chat` response `sources` list includes the new file's filename

---

### GET /ingest/status

#### Test: Status endpoint returns expected schema
**Type:** API
**Source:** Feature: GET /ingest/status Endpoint — criterion 1
**Given:** The FastAPI app is running
**When:** `GET /ingest/status` is called
**Then:**
- [ ] HTTP status is 200
- [ ] Response body contains `doc_count` (int), `last_run_at` (string or null), `last_error` (string or null)

---

#### Test: doc_count reflects the number of ingested documents
**Type:** API
**Source:** Feature: GET /ingest/status Endpoint — criterion 2
**Given:** Two documents have been ingested
**When:** `GET /ingest/status` is called
**Then:**
- [ ] `doc_count` equals 2

---

#### Test: last_run_at is null before any ingestion run
**Type:** API
**Source:** Feature: GET /ingest/status Endpoint — criterion 3
**Given:** The FastAPI app started with no ingestion run triggered
**When:** `GET /ingest/status` is called
**Then:**
- [ ] `last_run_at` is `null`

---

#### Test: last_error is null after a successful run
**Type:** API
**Source:** Feature: GET /ingest/status Endpoint — criterion 4
**Given:** An ingestion run completed without errors
**When:** `GET /ingest/status` is called
**Then:**
- [ ] `last_error` is `null`

---

### POST /chat

#### Test: Chat endpoint returns expected response schema
**Type:** API
**Source:** Feature: POST /chat Endpoint — criterion 1 | Issue 8 — criterion 1
**Given:** At least one document is ingested; a valid UUID session_id is prepared
**When:** `POST /chat` is called with `{ "query": "...", "session_id": "<uuid>" }`
**Then:**
- [ ] HTTP status is 200
- [ ] Response body contains `"answer"` (non-empty string), `"sources"` (list), `"session_id"` (the same UUID sent)

---

#### Test: sources contains filename strings (not paths or chunk IDs)
**Type:** API
**Source:** Feature: POST /chat Endpoint — criterion 1 | PRD: Source citation format
**Given:** A document named `policy.pdf` is ingested and its content matches the query
**When:** `POST /chat` is called
**Then:**
- [ ] `"sources"` contains `"policy.pdf"` (filename only, not a full path)
- [ ] No entry in `"sources"` contains a directory separator

---

#### Test: Two requests with the same session_id share conversation context
**Type:** API
**Source:** Feature: POST /chat Endpoint — criterion 2 | Issue 8 — criterion 2
**Given:** A document is ingested; a UUID session_id is chosen
**When:** First `POST /chat` asks about the document; second `POST /chat` with the same session_id asks a follow-up using a pronoun ("What else does it say?")
**Then:**
- [ ] The second response is coherent given the first (not a generic "I don't understand")

---

#### Test: Two requests with different session_ids have independent contexts
**Type:** API
**Source:** Feature: POST /chat Endpoint — criterion 3 | Issue 8 — criterion 3
**Given:** Two distinct UUID session_ids
**When:** Session A asks a question, then Session B asks an unrelated question
**Then:**
- [ ] Session B's response contains no reference to Session A's conversation
- [ ] `app.state.sessions` contains two separate history entries

---

#### Test: Chat returns no-results message for a query with no matching document
**Type:** API
**Source:** PRD User Story 10 | Feature: No-Results Node
**Given:** A document about topic A is ingested
**When:** `POST /chat` is called with a query about an unrelated topic B
**Then:**
- [ ] `"answer"` equals `"I couldn't find relevant information in your documents."`
- [ ] `"sources"` is an empty list
