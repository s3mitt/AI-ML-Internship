"""
Central configuration for the RAG API.
All tunable limits live here so robustness testing can target them directly.
"""
import os

# --- File upload limits -----------------------------------------------
MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_FILE_SIZE_BYTES", 20 * 1024 * 1024))  # 20 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# --- Chunking -----------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))       # characters per chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))  # characters of overlap
MAX_CHUNKS_PER_DOC = int(os.getenv("MAX_CHUNKS_PER_DOC", 2000))  # safety cap

# --- Retrieval ------------------------------------------------------------
TOP_K = int(os.getenv("TOP_K", 4))

# --- Embedding model ------------------------------------------------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# --- LLM (Anthropic) --------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

# --- Storage --------------------------------------------------------------
DATA_DIR = os.getenv("DATA_DIR", "./data")
