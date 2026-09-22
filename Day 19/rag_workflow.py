"""
LangGraph Practical Workflow
User -> Question -> Retriever -> LLM -> Answer -> Memory

Adds on top of the base design:
  - Conditional routing   (retriever found nothing -> fallback / clarify)
  - A loop                (LLM call retried on transient failure, bounded)
  - State management      (single shared State dict threaded through the graph)
  - Memory                (conversation history persisted via a checkpointer)
  - Error handling         (dedicated error node + graceful fallback answer)

This file is meant to run as-is (with a fake retriever/LLM) so the graph
shape and control flow can be tested without any API keys. Swap
`fake_retrieve` and `fake_llm_call` for real implementations
(e.g. a vector store retriever and a `ChatAnthropic` / `ChatOpenAI` call).
"""

from __future__ import annotations

import random
from typing import List, Optional, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


# ---------------------------------------------------------------------------
# 1. STATE
# ---------------------------------------------------------------------------
# The State is the single object that flows between every node. Each node
# reads what it needs from it and returns a partial dict that LangGraph
# merges back in. This is what "state management" means in LangGraph.

class GraphState(TypedDict, total=False):
    question: str                  # the user's raw question
    documents: List[str]           # docs pulled back by the retriever
    answer: str                    # final answer text
    error: Optional[str]           # last error message, if any
    retry_count: int               # how many times we've retried the LLM call
    route: str                     # scratch field used by conditional edges


MAX_RETRIES = 2


# ---------------------------------------------------------------------------
# 2. NODES
# ---------------------------------------------------------------------------

def question_node(state: GraphState) -> dict:
    """Entry node: normalizes the incoming user question."""
    question = state["question"].strip()
    return {"question": question, "retry_count": 0, "error": None}


def fake_retrieve(question: str) -> List[str]:
    """Stand-in for a real vector-store / search retriever."""
    if "unicorn" in question.lower():
        return []  # simulate a query with no relevant hits
    return [
        f"Document snippet 1 relevant to: {question}",
        f"Document snippet 2 relevant to: {question}",
    ]


def retriever_node(state: GraphState) -> dict:
    try:
        docs = fake_retrieve(state["question"])
        return {"documents": docs, "error": None}
    except Exception as exc:  # network/timeout/index error, etc.
        return {"documents": [], "error": f"retriever_error: {exc}"}


def route_after_retrieval(state: GraphState) -> str:
    """Conditional edge: decide where to go after retrieval."""
    if state.get("error"):
        return "handle_error"
    if not state.get("documents"):
        return "no_documents"
    return "call_llm"


def no_documents_node(state: GraphState) -> dict:
    """Fallback path when retrieval legitimately finds nothing."""
    answer = (
        "I couldn't find anything in the knowledge base for that question. "
        "Could you rephrase it or provide more detail?"
    )
    return {"answer": answer, "route": "no_documents"}


def fake_llm_call(question: str, documents: List[str]) -> str:
    """Stand-in for a real LLM call. Randomly fails ~30% of the time to
    exercise the retry loop -- replace with a real model call."""
    if random.random() < 0.3:
        raise RuntimeError("simulated transient LLM API error")
    context = " | ".join(documents)
    return f"Answer to '{question}' based on context: {context}"


def llm_node(state: GraphState) -> dict:
    try:
        answer = fake_llm_call(state["question"], state["documents"])
        return {"answer": answer, "error": None}
    except Exception as exc:
        return {
            "error": f"llm_error: {exc}",
            "retry_count": state.get("retry_count", 0) + 1,
        }


def route_after_llm(state: GraphState) -> str:
    """Conditional edge + loop: retry the LLM node up to MAX_RETRIES times,
    otherwise fall through to the error handler."""
    if not state.get("error"):
        return "answer"
    if state.get("retry_count", 0) <= MAX_RETRIES:
        return "retry"
    return "handle_error"


def error_handler_node(state: GraphState) -> dict:
    """Centralized error handling: log/observe the error and produce a
    safe, user-facing fallback answer instead of crashing the graph."""
    error_msg = state.get("error", "unknown_error")
    # In production: send to logging/alerting here.
    fallback = (
        "Sorry, I ran into a problem answering that just now "
        f"({error_msg}). Please try again in a moment."
    )
    return {"answer": fallback}


def answer_node(state: GraphState) -> dict:
    """Pass-through node kept for symmetry with the original design
    (User -> Question -> Retriever -> LLM -> Answer -> Memory)."""
    return {"answer": state["answer"]}


def memory_node(state: GraphState) -> dict:
    """Persisting is handled by the checkpointer (see below); this node is
    where you'd additionally write to a long-term store (e.g. a summary
    memory, vector store of past turns, etc.) if you have one."""
    return {}


# ---------------------------------------------------------------------------
# 3. GRAPH ASSEMBLY
# ---------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("question", question_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("no_documents", no_documents_node)
    graph.add_node("llm", llm_node)
    graph.add_node("error_handler", error_handler_node)
    graph.add_node("answer", answer_node)
    graph.add_node("memory", memory_node)

    graph.add_edge(START, "question")
    graph.add_edge("question", "retriever")

    # Conditional routing after retrieval
    graph.add_conditional_edges(
        "retriever",
        route_after_retrieval,
        {
            "call_llm": "llm",
            "no_documents": "no_documents",
            "handle_error": "error_handler",
        },
    )

    # Conditional routing + loop after the LLM call
    graph.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "answer": "answer",
            "retry": "llm",              # <-- the loop: re-enter the same node
            "handle_error": "error_handler",
        },
    )

    graph.add_edge("no_documents", "memory")
    graph.add_edge("error_handler", "memory")
    graph.add_edge("answer", "memory")
    graph.add_edge("memory", END)

    checkpointer = MemorySaver()  # gives every thread_id its own persisted history
    return graph.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# 4. DEMO RUN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = build_graph()
    config = {"configurable": {"thread_id": "demo-session-1"}}

    for q in ["What is LangGraph?", "Tell me about a unicorn startup"]:
        result = app.invoke({"question": q}, config=config)
        print(f"Q: {q}\nA: {result['answer']}\n")