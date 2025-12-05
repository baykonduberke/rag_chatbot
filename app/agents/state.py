"""
Agent State Definition

LangGraph'ın state management'ı için TypedDict.
"""

from typing import TypedDict, Annotated, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """
    LangGraph Agent State.
    
    Bu state, graph'ın her node'u arasında taşınır.
    """
    
    # Message history with special reducer
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]
    
    # Identifiers
    user_id: str
    thread_id: str
    
    # Current turn data
    last_question: str
    last_answer: str
    
    # Optional fields
    context: Optional[str]  # RAG retrieved context
    error: Optional[str]    # Error message

