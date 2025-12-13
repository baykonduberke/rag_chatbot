"""
Agent State Definition

LangGraph'ın state management'ı için TypedDict.
"""

from typing import TypedDict, Annotated, Optional, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """
    LangGraph Agent State.
    """
    
    # Message history
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]
    
    # Identifiers
    user_id: str
    thread_id: str
    
    # Current turn
    last_question: str
    last_answer: str
    
    # Error
    error: Optional[str]
    
    # Agent routing: chitchat, sql_only, sql_then_rag
    agent_type: Optional[Literal["chitchat", "sql_only", "sql_then_rag"]]
    
    # SQL fields
    sql_query: Optional[str]
    sql_results: Optional[str]
    sql_results_for_rag: Optional[list[dict]]
    
    # RAG fields
    rag_results: Optional[list[dict]]
