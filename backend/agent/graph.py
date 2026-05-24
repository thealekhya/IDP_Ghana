"""
LangGraph Agent — the main orchestration graph.

This is YOUR key file as Dev A. It wires up:
  classify → route → (sql | rag | gap | anomaly | general) → answer

Usage:
    from agent.graph import ask_agent
    answer = ask_agent("How many hospitals are in Accra?")
"""

from langgraph.graph import StateGraph, END
from backend.agent.state import AgentState
from backend.agent.nodes import (
    classify_query,
    run_sql_query,
    run_rag_search,
    run_gap_analysis,
    run_anomaly_check,
    generate_answer,
)


def _route_query(state: AgentState) -> str:
    """Conditional edge: route to the right node based on classification."""
    qt = state.get("query_type", "general")
    if qt == "sql":
        return "sql"
    elif qt == "rag":
        return "rag"
    elif qt == "gap":
        return "gap"
    elif qt == "anomaly":
        return "anomaly"
    else:
        return "general"


def build_agent():
    """
    Build and compile the LangGraph agent.

    Graph structure:
        ┌──────────┐
        │ classify  │
        └────┬─────┘
             │
        ┌────▼─────┐
        │  route?   │──── sql ────→ run_sql ──────┐
        │           │──── rag ────→ run_rag ──────┤
        │           │──── gap ────→ gap_analysis ──┤
        │           │──── anomaly → anomaly_check ─┤
        │           │──── general ────────────────┤
        └───────────┘                             │
                                           ┌──────▼──────┐
                                           │  generate    │
                                           │   answer     │
                                           └──────┬──────┘
                                                  │
                                                 END
    """
    graph = StateGraph(AgentState)

    # ── Add nodes ──
    graph.add_node("classify", classify_query)
    graph.add_node("sql", run_sql_query)
    graph.add_node("rag", run_rag_search)
    graph.add_node("gap", run_gap_analysis)
    graph.add_node("anomaly", run_anomaly_check)
    graph.add_node("answer", generate_answer)

    # ── Set entry point ──
    graph.set_entry_point("classify")

    # ── Conditional routing after classification ──
    graph.add_conditional_edges(
        "classify",
        _route_query,
        {
            "sql": "sql",
            "rag": "rag",
            "gap": "gap",
            "anomaly": "anomaly",
            "general": "answer",  # General skips straight to answer
        },
    )

    # ── After SQL, RAG, gap, or anomaly analysis, always go to answer ──
    graph.add_edge("sql", "answer")
    graph.add_edge("rag", "answer")
    graph.add_edge("gap", "answer")
    graph.add_edge("anomaly", "answer")

    # ── Answer is the final node ──
    graph.add_edge("answer", END)

    return graph.compile()


# ── Compile the agent once ──
agent = build_agent()


def ask_agent(query: str) -> str:
    """
    The main function everyone calls.

    Dev C calls this from Streamlit.
    Dev B's extraction results feed the data this queries.

    Args:
        query: Natural language question about Ghana healthcare

    Returns:
        A helpful answer string
    """
    result = agent.invoke({
        "query": query,
        "messages": [],
    })
    return result.get("final_answer", "I couldn't generate an answer.")


# ── Quick test ──
if __name__ == "__main__":
    print("=" * 60)
    print("Ghana Healthcare Agent — Interactive Mode")
    print("Type 'quit' to exit")
    print("=" * 60)

    while True:
        q = input("\n🩺 Ask about Ghana healthcare: ").strip()
        if q.lower() in ("quit", "exit", "q"):
            break
        if not q:
            continue

        print("\n⏳ Thinking...")
        answer = ask_agent(q)
        print(f"\n💬 {answer}")
