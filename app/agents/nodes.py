"""
Agent Node Functions

Her node, graph'ta bir adımı temsil eder.
"""

from typing import Literal, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from sqlalchemy import text

from app.agents.state import AgentState
from app.agents.prompts import (
    CHITCHAT_PROMPT,
    ROUTER_PROMPT,
    SQL_SCHEMA,
    SQL_GENERATION_PROMPT,
    SQL_INTERPRETATION_PROMPT,
    # ANALYZE_COMMENTS_PROMPT,  # Kullanılmıyor - RAG_ANALYSIS_PROMPT kullanılıyor
    RAG_ANALYSIS_PROMPT
)
from app.core.config import settings
from app.db.database import async_session_maker
from app.services.vector_store import search_similar_comments


_llm: Optional[ChatOpenAI] = None


def format_conversation_history(messages: list, max_messages: int = 6) -> str:
    """Konuşma geçmişini prompt için formatla."""
    if not messages:
        return "(Henüz konuşma geçmişi yok)"
    
    # Son N mesajı al
    recent_messages = messages[-max_messages:]
    
    history_lines = []
    for msg in recent_messages:
        role = "Kullanıcı" if msg.type == "human" else "Asistan"
        # Çok uzun mesajları kısalt
        content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
        history_lines.append(f"{role}: {content}")
    
    return "\n".join(history_lines) if history_lines else "(Henüz konuşma geçmişi yok)"


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


async def add_user_message(state: AgentState) -> dict:
    """Kullanıcı mesajını ekle."""
    return {"messages": [HumanMessage(content=state["last_question"])]}


async def route_question(state: AgentState) -> dict:
    """Soruyu sınıflandır."""
    # Konuşma geçmişini formatla
    history = format_conversation_history(state.get("messages", []))
    
    prompt = ROUTER_PROMPT.format(
        question=state["last_question"],
        history=history
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])
    
    agent_type = response.content.strip().lower()
    if agent_type not in ["chitchat", "sql_only", "sql_then_rag"]:
        agent_type = "chitchat"
    
    print(f"🔍 [route_question] Question: {state['last_question'][:50]}...")
    print(f"🔍 [route_question] History messages: {len(state.get('messages', []))}")
    print(f"🔍 [route_question] Selected agent: {agent_type}")
    
    return {"agent_type": agent_type}


async def chitchat_response(state: AgentState) -> dict:
    """Basit sohbet cevabı."""
    messages = [
        SystemMessage(content=CHITCHAT_PROMPT),
        HumanMessage(content=state["last_question"])
    ]
    response = await get_llm().ainvoke(messages)
    return {"last_answer": response.content}


async def generate_sql(state: AgentState) -> dict:
    """SQL üret."""
    # Konuşma geçmişini formatla
    history = format_conversation_history(state.get("messages", []))
    
    prompt = SQL_GENERATION_PROMPT.format(
        schema=SQL_SCHEMA,
        question=state["last_question"],
        history=history
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])
    
    sql = response.content.strip()
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[1].rsplit("```", 1)[0]
    
    print(f"🔍 [generate_sql] Generated SQL: {sql[:100]}...")
    
    return {"sql_query": sql.strip()}


async def execute_sql(state: AgentState) -> dict:
    """SQL çalıştır."""
    sql = state.get("sql_query", "")
    
    print(f"🔍 [execute_sql] SQL: {sql[:100]}...")
    print(f"🔍 [execute_sql] Agent type: {state.get('agent_type')}")
    
    if not sql.strip().upper().startswith("SELECT"):
        return {"sql_results": "Hata: Sadece SELECT izinli", "error": "Invalid query"}
    
    try:
        async with async_session_maker() as session:
            result = await session.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())
            
            if not rows:
                print("🔍 [execute_sql] No rows found")
                return {"sql_results": "Sonuç bulunamadı", "sql_results_for_rag": []}
            
            results = [dict(zip(columns, row)) for row in rows]
            print(f"🔍 [execute_sql] Found {len(results)} results")
            return {"sql_results": str(results), "sql_results_for_rag": results}
    except Exception as e:
        print(f"🔍 [execute_sql] Error: {e}")
        return {"sql_results": f"SQL Hatası: {e}", "sql_results_for_rag": [], "error": str(e)}


async def interpret_sql_results(state: AgentState) -> dict:
    """SQL sonuçlarını yorumla."""
    prompt = SQL_INTERPRETATION_PROMPT.format(
        question=state["last_question"],
        sql_query=state.get("sql_query", ""),
        results=state.get("sql_results", "")
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])
    return {"last_answer": response.content}


async def rag_search(state: AgentState) -> dict:
    """RAG ile semantic search yap."""
    question = state["last_question"]
    sql_results = state.get("sql_results_for_rag", [])
    
    print(f"🔍 [rag_search] Question: {question[:50]}...")
    print(f"🔍 [rag_search] SQL results count: {len(sql_results) if sql_results else 0}")
    
    # Sentiment filter belirle (SQL sonuçlarından)
    sentiment_filter = None
    if sql_results:
        # İlk sonuçtan sentiment'i al
        first_sentiment = sql_results[0].get("sentiment_result", "")
        if first_sentiment in ["Olumlu", "Olumsuz", "POSITIVE", "NEGATIVE"]:
            sentiment_filter = first_sentiment
    
    try:
        # Semantic search yap
        rag_results = await search_similar_comments(
            query=question,
            top_k=500,
            sentiment_filter=sentiment_filter
        )
        
        print(f"🔍 [rag_search] RAG results count: {len(rag_results)}")
        
        if not rag_results:
            return {"rag_results": [], "last_answer": "İlgili yorum bulunamadı."}
        
        return {"rag_results": rag_results}
    except Exception as e:
        print(f"🔍 [rag_search] Error: {e}")
        # Fallback: SQL sonuçlarını kullan
        return {"rag_results": sql_results if sql_results else []}


async def analyze_rag_results(state: AgentState) -> dict:
    """RAG sonuçlarını analiz et."""
    results = state.get("rag_results", [])
    
    print(f"🔍 [analyze_rag_results] Results count: {len(results) if results else 0}")
    
    if not results:
        return {"last_answer": "Analiz için yorum bulunamadı."}
    
    # Yorumları formatla (maksimum 500 yorum)
    comments_text = ""
    for i, row in enumerate(results[:500], 1):
        content = row.get("content", "")
        company = row.get("company", "")
        sentiment = row.get("sentiment_result", "")
        score = row.get("score", "")
        
        score_str = f" [benzerlik: {1-float(score):.2f}]" if score else ""
        comments_text += f"{i}. [{company}] ({sentiment}){score_str}: {content}\n\n"
    
    prompt = RAG_ANALYSIS_PROMPT.format(
        question=state["last_question"],
        comments=comments_text
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])
    return {"last_answer": response.content}


async def add_ai_message(state: AgentState) -> dict:
    """AI cevabını ekle."""
    return {"messages": [AIMessage(content=state["last_answer"])]}


async def handle_error(state: AgentState) -> dict:
    """Hata yönetimi."""
    return {
        "last_answer": f"Bir hata oluştu: {state.get('error', 'Bilinmeyen hata')}",
        "messages": [AIMessage(content="Hata oluştu")]
    }


def route_by_agent_type(state: AgentState) -> str:
    """Agent tipine göre yönlendir."""
    return state.get("agent_type", "chitchat")


def route_after_sql(state: AgentState) -> str:
    """SQL sonrası yönlendirme."""
    if state.get("agent_type") == "sql_then_rag":
        return "rag"
    return "interpret"
