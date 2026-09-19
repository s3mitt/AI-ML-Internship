from typing import List, Optional
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    chunk_id: str
    doc_id: str
    filename: str
    chunk_index: int
    char_start: int
    char_end: int


class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    content_type: str
    file_size_bytes: int
    num_chunks: int
    num_characters: int
    uploaded_at: str


class UploadResponse(BaseModel):
    message: str
    document: DocumentMetadata


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    doc_id: Optional[str] = Field(
        default=None, description="Restrict retrieval to a single document id"
    )
    top_k: Optional[int] = Field(default=None, ge=1, le=20)


class SourceChunk(BaseModel):
    chunk_id: str
    doc_id: str
    filename: str
    chunk_index: int
    text: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceChunk]


class ErrorResponse(BaseModel):
    error: str
    detail: str
