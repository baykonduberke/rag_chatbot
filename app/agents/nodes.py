"""
Agent Node Functions

Her node, graph'ta bir adımı temsil eder.
"""

from typing import Literal, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT
from app.core.config import settings


# Lazy LLM initialization
_llm: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """LLM instance'ı lazy olarak oluştur."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS
        )
    return _llm


def add_user_message(state: AgentState) -> dict:
    """Kullanıcı mesajını state'e ekle."""
    user_message = HumanMessage(content=state["last_question"])
    return {
        "messages": [user_message]
    }


def generate_response(state: AgentState) -> dict:
    """LLM ile response generate et."""
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    
    # Context varsa ekle (RAG için)
    if state.get("context"):
        context_message = SystemMessage(
            content=f"Relevant context:\n{state['context']}"
        )
        messages = [system_message, context_message] + list(state["messages"])
    else:
        messages = [system_message] + list(state["messages"])
    
    response = get_llm().invoke(messages)
    
    return {
        "last_answer": response.content
    }


def add_ai_message(state: AgentState) -> dict:
    """AI cevabını state'e ekle."""
    ai_message = AIMessage(content=state["last_answer"])
    return {
        "messages": [ai_message]
    }


def handle_error(state: AgentState) -> dict:
    """Error handling node."""
    error_message = state.get("error", "An unexpected error occurred")
    return {
        "last_answer": f"Sorry, I encountered an error: {error_message}",
        "messages": [AIMessage(content=f"Error: {error_message}")]
    }


def should_continue(state: AgentState) -> Literal["continue", "error", "end"]:
    """Graph devam etmeli mi?"""
    if state.get("error"):
        return "error"
    if state.get("last_answer"):
        return "end"
    return "continue"

