"""
LangGraph Graph Definition

Graph builder ve compiler.
"""

from typing import Optional, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from app.agents.state import AgentState
from app.agents.nodes import (
    add_user_message,
    route_question,
    chitchat_response,
    generate_sql,
    execute_sql,
    interpret_sql_results,
    rag_search,
    analyze_rag_results,
    add_ai_message,
    # handle_error,  # Kullanılmıyor - hiçbir edge bu node'a gitmiyor
    route_by_agent_type,
    route_after_sql
)
from app.core.redis import get_async_checkpointer


CompiledGraph = StateGraph


def build_graph() -> StateGraph:
    """Graph oluştur."""
    graph = StateGraph(AgentState)
    
    # Nodes
    graph.add_node("add_user_message", add_user_message)
    graph.add_node("route_question", route_question)
    graph.add_node("chitchat_response", chitchat_response)
    graph.add_node("generate_sql", generate_sql)
    graph.add_node("execute_sql", execute_sql)
    graph.add_node("interpret_sql_results", interpret_sql_results)
    graph.add_node("rag_search", rag_search)
    graph.add_node("analyze_rag_results", analyze_rag_results)
    graph.add_node("add_ai_message", add_ai_message)
    # graph.add_node("handle_error", handle_error)  # Kullanılmıyor - hiçbir edge bu node'a gitmiyor
    
    # Entry
    graph.set_entry_point("add_user_message")
    
    # Edges
    graph.add_edge("add_user_message", "route_question")
    
    # 3-yönlü routing
    graph.add_conditional_edges(
        "route_question",
        route_by_agent_type,
        {
            "chitchat": "chitchat_response",
            "sql_only": "generate_sql",
            "sql_then_rag": "generate_sql"
        }
    )
    
    # Chitchat path
    graph.add_edge("chitchat_response", "add_ai_message")
    
    # SQL path
    graph.add_edge("generate_sql", "execute_sql")
    
    graph.add_conditional_edges(
        "execute_sql",
        route_after_sql,
        {
            "interpret": "interpret_sql_results",
            "rag": "rag_search"
        }
    )
    
    # SQL only path
    graph.add_edge("interpret_sql_results", "add_ai_message")
    
    # RAG path
    graph.add_edge("rag_search", "analyze_rag_results")
    graph.add_edge("analyze_rag_results", "add_ai_message")
    
    # Final
    graph.add_edge("add_ai_message", END)
    # graph.add_edge("handle_error", END)  # Kullanılmıyor
    
    return graph


def compile_graph(
    graph: StateGraph, 
    checkpointer: Optional[Union[AsyncRedisSaver, MemorySaver]] = None
) -> CompiledGraph:
    """Graph'ı compile et."""
    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# Compiled graphs cache
_compiled_graph_no_memory: Optional[CompiledGraph] = None
_compiled_graph_with_memory: Optional[CompiledGraph] = None


# def get_compiled_graph_sync() -> CompiledGraph:
#     """Compiled graph (checkpointer'sız, sync için)."""
#     global _compiled_graph_no_memory
#     
#     if _compiled_graph_no_memory is None:
#         graph = build_graph()
#         _compiled_graph_no_memory = compile_graph(graph)
#     
#     return _compiled_graph_no_memory


async def get_compiled_graph_async() -> CompiledGraph:
    """Compiled graph with async checkpointer."""
    global _compiled_graph_with_memory
    
    if _compiled_graph_with_memory is None:
        graph = build_graph()
        checkpointer = await get_async_checkpointer()
        _compiled_graph_with_memory = compile_graph(graph, checkpointer)
    
    return _compiled_graph_with_memory


# def reset_graph() -> None:
#     """Graph'ı reset et (testing için)."""
#     global _compiled_graph_no_memory, _compiled_graph_with_memory
#     _compiled_graph_no_memory = None
#     _compiled_graph_with_memory = None
