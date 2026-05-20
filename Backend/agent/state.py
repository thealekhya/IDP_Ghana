"""Agent state definition — what the agent tracks through its workflow."""

from typing import Annotated, List, Optional, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State that flows through every node in the LangGraph agent."""

    # Chat history
    messages: Annotated[list, add_messages]

    # Current user query
    query: str

    # Router decision: "sql", "rag", "gap", "anomaly", or "general"
    query_type: Optional[str]

    # SQL path results
    sql_query: Optional[str]
    sql_result: Optional[str]

    # RAG path results
    rag_context: Optional[str]

    # Medical desert / gap analysis results
    gap_result: Optional[str]

    # Anomaly / discrepancy detection results
    anomaly_result: Optional[str]

    # Final output
    final_answer: Optional[str]

    # Source citations for transparency (row-level + step-level)
    citations: Optional[list]
