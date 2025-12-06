"""
LangGraph Graph Definition

Graph builder ve compiler.
"""

from typing import Optional
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.nodes import (
    add_user_message,
    generate_response,
    add_ai_message,
    handle_error
)
from app.core.redis import get_checkpointer_sync


# Type alias for compiled graph
CompiledGraph = StateGraph


def build_graph() -> StateGraph:
    """LangGraph graph'ını oluştur."""
    graph = StateGraph(AgentState)
    
    # Node'ları ekle
    graph.add_node("add_user_message", add_user_message)
    graph.add_node("generate_response", generate_response)
    graph.add_node("add_ai_message", add_ai_message)
    graph.add_node("handle_error", handle_error)
    
    # Entry point
    graph.set_entry_point("add_user_message")
    
    # Edge'leri tanımla
    graph.add_edge("add_user_message", "generate_response")
    graph.add_edge("generate_response", "add_ai_message")
    graph.add_edge("add_ai_message", END)
    graph.add_edge("handle_error", END)
    
    return graph


def compile_graph(
    graph: StateGraph,
    checkpointer: Optional[any] = None
) -> CompiledGraph:
    """Graph'ı compile et."""
    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# Singleton pattern
_compiled_graph: Optional[CompiledGraph] = None


def get_compiled_graph(with_memory: bool = True) -> CompiledGraph:
    """
    Compiled graph singleton.
    
    Args:
        with_memory: True ise checkpointer ile compile et (chat history için)
    """
    global _compiled_graph
    
    if _compiled_graph is None:
        graph = build_graph()
        if with_memory:
            checkpointer = get_checkpointer_sync()
            _compiled_graph = compile_graph(graph, checkpointer)
        else:
            _compiled_graph = compile_graph(graph)
    
    return _compiled_graph


def reset_graph() -> None:
    """Graph'ı reset et (testing için)."""
    global _compiled_graph
    _compiled_graph = None

