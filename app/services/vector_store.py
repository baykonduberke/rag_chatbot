"""
Vector Store Service

Redis Vector Store ile semantic search.
Yorumları embedding'e çevirip Redis'te saklar.
"""

from typing import Optional, List
import json
from langchain_openai import OpenAIEmbeddings
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
import redis.asyncio as redis

from app.core.config import settings


# Embedding model singleton
_embeddings: Optional[OpenAIEmbeddings] = None

# Redis client singleton
_redis_client: Optional[redis.Redis] = None

# Index name
INDEX_NAME = "comments_idx"

# Index schema
INDEX_SCHEMA = {
    "index": {
        "name": INDEX_NAME,
        "prefix": "comment:",
        "storage_type": "hash"
    },
    "fields": [
        {"name": "id", "type": "tag"},
        {"name": "content", "type": "text"},
        {"name": "company", "type": "tag"},
        {"name": "category", "type": "tag"},
        {"name": "product_category", "type": "tag"},
        {"name": "sentiment_result", "type": "tag"},
        {
            "name": "embedding",
            "type": "vector",
            "attrs": {
                "dims": 1536,
                "distance_metric": "cosine",
                "algorithm": "flat"
            }
        }
    ]
}


def get_embeddings() -> OpenAIEmbeddings:
    """OpenAI Embeddings singleton."""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
    return _embeddings


async def get_redis_client() -> redis.Redis:
    """Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
        )
    return _redis_client


async def create_index() -> None:
    """Redis Vector Index oluştur."""
    client = await get_redis_client()
    
    try:
        # Mevcut index'i kontrol et
        await client.execute_command("FT.INFO", INDEX_NAME)
        print(f"✅ Index '{INDEX_NAME}' already exists")
    except redis.ResponseError:
        # Index yoksa oluştur
        index = SearchIndex.from_dict(INDEX_SCHEMA)
        index.connect(settings.REDIS_URL)
        index.create(overwrite=False)
        print(f"✅ Index '{INDEX_NAME}' created")


async def add_comment_embedding(
    comment_id: int,
    content: str,
    company: str,
    category: str,
    product_category: str,
    sentiment_result: str
) -> None:
    """Tek bir yorumu embedding'e çevirip Redis'e kaydet."""
    client = await get_redis_client()
    embeddings = get_embeddings()
    
    # Embedding oluştur
    embedding = await embeddings.aembed_query(content)
    
    # Redis'e kaydet
    key = f"comment:{comment_id}"
    data = {
        "id": str(comment_id),
        "content": content,
        "company": company,
        "category": category,
        "product_category": product_category,
        "sentiment_result": sentiment_result,
        "embedding": bytes(json.dumps(embedding), "utf-8")
    }
    
    await client.hset(key, mapping=data)


async def search_similar_comments(
    query: str,
    top_k: int = 20,
    sentiment_filter: Optional[str] = None
) -> List[dict]:
    """Semantic search ile benzer yorumları bul."""
    client = await get_redis_client()
    embeddings = get_embeddings()
    
    # Query embedding oluştur
    query_embedding = await embeddings.aembed_query(query)
    
    # Filter oluştur
    filter_str = ""
    if sentiment_filter:
        filter_str = f"@sentiment_result:{{{sentiment_filter}}}"
    
    # Vector query
    query_obj = VectorQuery(
        vector=query_embedding,
        vector_field_name="embedding",
        return_fields=["id", "content", "company", "category", "product_category", "sentiment_result"],
        num_results=top_k,
        filter_expression=filter_str if filter_str else None
    )
    
    # Search
    index = SearchIndex.from_dict(INDEX_SCHEMA)
    index.connect(settings.REDIS_URL)
    
    results = index.query(query_obj)
    
    # Format results
    comments = []
    for doc in results:
        comments.append({
            "id": doc.get("id", ""),
            "content": doc.get("content", ""),
            "company": doc.get("company", ""),
            "category": doc.get("category", ""),
            "product_category": doc.get("product_category", ""),
            "sentiment_result": doc.get("sentiment_result", ""),
            "score": doc.get("vector_distance", 0)
        })
    
    return comments


async def get_embedding_count() -> int:
    """Redis'teki embedding sayısını getir."""
    client = await get_redis_client()
    keys = await client.keys("comment:*")
    return len(keys)

