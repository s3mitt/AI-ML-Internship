"""
RAG API — upload a document, then ask questions answered from its content.

Endpoints:
  POST   /upload              upload a PDF / DOCX / TXT file
  GET    /documents           list uploaded documents
  GET    /documents/{doc_id}  get one document's metadata
  DELETE /documents/{doc_id}  remove a document and its chunks
  POST   /ask                 ask a question, optionally scoped to one doc_id
  GET    /health               liveness check
"""
import logging
import time

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from app.chunking import chunk_text
from app.document_processor import DocumentProcessingError, extract_text, validate_upload
from app.llm import generate_answer
from app.models import AskRequest, AskResponse, DocumentMetadata, SourceChunk, UploadResponse
from app.vector_store import store
from app.config import TOP_K
from app.ui import INDEX_HTML

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag_api")

app = FastAPI(
    title="RAG API",
    description="Upload documents, ask questions, get answers grounded in the content.",
    version="1.0.0",
)


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    start = time.time()
    raw_bytes = await file.read()

    try:
        ext = validate_upload(file.filename, file.content_type or "", raw_bytes)
        extracted = extract_text(ext, raw_bytes)
        chunks = chunk_text(extracted.text)

        if not chunks:
            raise DocumentProcessingError(422, "Document produced zero usable chunks.")

        metadata = store.add_document(
            filename=file.filename,
            content_type=file.content_type or "unknown",
            file_size_bytes=len(raw_bytes),
            num_characters=len(extracted.text),
            chunks=chunks,
        )
    except DocumentProcessingError as e:
        logger.warning(f"Upload rejected for '{file.filename}': {e.message}")
        raise HTTPException(status_code=e.http_status, detail=e.message)
    except Exception as e:
        logger.exception(f"Unexpected error processing '{file.filename}'")
        raise HTTPException(status_code=500, detail=f"Internal error while processing file: {e}")

    elapsed = time.time() - start
    logger.info(f"Uploaded '{file.filename}' -> {metadata['num_chunks']} chunks in {elapsed:.2f}s")

    return UploadResponse(
        message=f"Document processed into {metadata['num_chunks']} chunks.",
        document=DocumentMetadata(**metadata),
    )


@app.get("/documents", response_model=list[DocumentMetadata])
def list_documents():
    return [DocumentMetadata(**d) for d in store.list_documents()]


@app.get("/documents/{doc_id}", response_model=DocumentMetadata)
def get_document(doc_id: str):
    doc = store.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"No document with id '{doc_id}'.")
    return DocumentMetadata(**doc)


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    deleted = store.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"No document with id '{doc_id}'.")
    return {"message": f"Document '{doc_id}' deleted."}


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    if store.is_empty():
        raise HTTPException(
            status_code=400,
            detail="No documents have been uploaded yet. Upload a document via /upload first.",
        )

    if request.doc_id is not None and store.get_document(request.doc_id) is None:
        raise HTTPException(status_code=404, detail=f"No document with id '{request.doc_id}'.")

    top_k = request.top_k or TOP_K
    results = store.search(request.question, top_k=top_k, doc_id=request.doc_id)
    answer = generate_answer(request.question, results)

    return AskResponse(
        question=request.question,
        answer=answer,
        sources=[SourceChunk(**r) for r in results],
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )
