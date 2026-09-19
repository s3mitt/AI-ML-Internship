# RAG API — Document Q&A Service

Upload a PDF, DOCX, or TXT file; ask questions about it; get answers grounded
in the document's content, with source chunks cited.

## Architecture

```
Upload → Validate → Extract text → Chunk → TF-IDF index → stored in memory
Ask     → Embed question → cosine-similarity search → top-k chunks → LLM answer
```

| Stage | Implementation |
|---|---|
| API framework | FastAPI |
| Text extraction | pypdf (PDF), python-docx (DOCX), built-in decode (TXT) |
| Chunking | Fixed-size character windows (800 chars, 150 overlap), word-boundary aware |
| Vector store | In-memory TF-IDF (scikit-learn) + cosine similarity |
| Answer generation | Anthropic Claude (falls back to extractive excerpt if no API key) |

## Project layout

```
app/
  main.py                FastAPI app and route handlers
  config.py               all tunable limits (file size, chunk size, top_k, etc.)
  models.py                Pydantic request/response schemas
  document_processor.py    upload validation + text extraction
  chunking.py               chunking logic
  vector_store.py            in-memory TF-IDF index and search
  llm.py                     answer generation (Claude or extractive fallback)
requirements.txt
test_files/                 sample files used for robustness testing
screenshots/                captured request/response evidence
TESTING_REPORT.docx          full robustness testing report
```

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000/docs for interactive Swagger UI.

Optional: set `ANTHROPIC_API_KEY` as an environment variable to get real
generated answers instead of the extractive fallback:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/upload` | Upload a PDF/DOCX/TXT file (multipart form field `file`) |
| GET | `/documents` | List all uploaded documents and their metadata |
| GET | `/documents/{doc_id}` | Get one document's metadata |
| DELETE | `/documents/{doc_id}` | Remove a document and its chunks from the index |
| POST | `/ask` | `{"question": "...", "doc_id": "optional", "top_k": optional}` |
| GET | `/health` | Liveness check |

### Example

```bash
curl -X POST http://localhost:8000/upload -F "file=@report.pdf"

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the summary of the report?"}'
```

## Configurable limits (`app/config.py`)

- `MAX_FILE_SIZE_BYTES` — default 20 MB
- `ALLOWED_EXTENSIONS` — `.pdf`, `.txt`, `.docx`
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — default 800 / 150 characters
- `MAX_CHUNKS_PER_DOC` — default 2000, a safety cap against runaway indexing
- `TOP_K` — default 4 chunks retrieved per question

## Known limitations

See `TESTING_REPORT.docx` for the full write-up. In short: state is in-memory
only (resets on restart), OCR is not performed on scanned/image-only PDFs,
TF-IDF retrieval is lexical rather than semantic, and the outbound LLM call
currently has no timeout.
