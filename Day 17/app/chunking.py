"""
Simple, dependency-free chunking: fixed-size character windows with overlap,
biased to break on whitespace so words aren't split when possible.
"""
from dataclasses import dataclass

from app.config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNKS_PER_DOC
from app.document_processor import DocumentProcessingError


@dataclass
class Chunk:
    text: str
    chunk_index: int
    char_start: int
    char_end: int


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    if overlap >= chunk_size:
        overlap = chunk_size // 4  # guard against misconfiguration

    chunks: list[Chunk] = []
    start = 0
    text_len = len(text)
    index = 0

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # try to break on the last whitespace before `end` so words stay whole
        if end < text_len:
            break_point = text.rfind(" ", start, end)
            if break_point != -1 and break_point > start:
                end = break_point

        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(text=piece, chunk_index=index, char_start=start, char_end=end))
            index += 1

        if index > MAX_CHUNKS_PER_DOC:
            raise DocumentProcessingError(
                413,
                f"Document produced more than {MAX_CHUNKS_PER_DOC} chunks; "
                "it is too large for this API to index.",
            )

        next_start = end - overlap
        start = next_start if next_start > start else end

    return chunks
