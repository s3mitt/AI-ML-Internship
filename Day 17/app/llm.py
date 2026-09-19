from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

SYSTEM_PROMPT = (
    "You are a question-answering assistant. Answer the user's question using "
    "ONLY the provided context excerpts. If the answer is not contained in the "
    "context, say you don't have enough information in the uploaded documents. "
    "Be concise and cite which excerpt you used when helpful."
)


def generate_answer(question: str, sources: list[dict]) -> str:
    if not sources:
        return "I couldn't find any relevant content in the uploaded documents to answer that."

    if ANTHROPIC_API_KEY:
        return _generate_with_claude(question, sources)
    return _generate_extractive(sources)


def _generate_with_claude(question: str, sources: list[dict]) -> str:
    import anthropic

    context = "\n\n".join(
        f"[Excerpt {i+1} | {s['filename']} | chunk {s['chunk_index']}]\n{s['text']}"
        for i, s in enumerate(sources)
    )
    # timeout is required: an unbounded call here can hang a request indefinitely
    # (found during robustness testing -- see TESTING_REPORT.docx section 5.2)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, timeout=30.0, max_retries=1)
    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                }
            ],
        )
        return "".join(block.text for block in response.content if block.type == "text").strip()
    except Exception as e:
        # Degrade gracefully rather than 500 the whole /ask endpoint
        return (
            "The language model call failed, so here is the most relevant excerpt "
            f"instead: \"{sources[0]['text'][:500]}\" (error: {e})"
        )


def _generate_extractive(sources: list[dict]) -> str:
    top = sources[0]
    return (
        "[No ANTHROPIC_API_KEY configured -- returning the most relevant excerpt "
        f"instead of a generated answer]\n\nFrom '{top['filename']}': {top['text']}"
    )
