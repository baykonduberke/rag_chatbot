# RAG Chatbot API

LangGraph tabanlı, FastAPI ile geliştirilmiş akıllı yorum analizi ve sohbet uygulaması. Semantic search (RAG) ile yorum içeriklerini analiz eder, SQL sorgularıyla istatistiksel veriler sunar.

## 📑 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Mimari Yapı](#-mimari-yapı)
- [Teknolojiler](#-teknolojiler)
- [Kurulum](#-kurulum)
- [Veri Yükleme](#-veri-yükleme)
- [API Referansı](#-api-referansı)
- [Modüller](#-modüller)
- [Veritabanı Şeması](#-veritabanı-şeması)
- [LangGraph Akışı](#-langgraph-akışı)
- [Güvenlik](#-güvenlik)
- [Docker](#-docker)

---

## 🎯 Proje Hakkında

Bu proje, kullanıcı yorumlarını (reviews) analiz eden ve yapay zeka destekli sohbet arayüzü sunan bir REST API'dir.

**Temel Kullanım Senaryoları:**
- 📊 **İstatistiksel Sorgular**: "Kaç olumsuz yorum var?", "Nike'ın olumlu yorum oranı nedir?"
- 🔍 **Semantic Search**: "Kargo gecikmelerinden şikayet eden yorumları bul"
- 💬 **İçerik Analizi**: "Olumsuz yorumlarda müşteriler neyden şikayet ediyor?"
- 🗂️ **Yorum Yönetimi**: CRUD işlemleri ile yorum ekleme, güncelleme, silme

---

## ✨ Özellikler

### 🤖 Akıllı Soru Yönlendirme (3-Yönlü Router)
| Mod | Kullanım | Örnek |
|-----|----------|-------|
| **chitchat** | Genel sohbet | "Merhaba", "Nasılsın?" |
| **sql_only** | Sayısal sorgular | "Kaç yorum var?", "En fazla yorum alan kategori?" |
| **sql_then_rag** | İçerik analizi | "Şikayet konularını özetle", "Hakaret içeren yorumlar" |

### 📦 Temel Özellikler
- **Kullanıcı Yönetimi**: Kayıt, giriş ve JWT tabanlı kimlik doğrulama
- **Sohbet Sistemi**: Kullanıcı başına izole edilmiş sohbet oturumları
- **Hafıza Yönetimi**: Redis AsyncRedisSaver ile konuşma geçmişi
- **RAG Desteği**: Redis Vector Store ile semantic search
- **Yorum Analizi**: Sentiment analizi (Olumlu/Olumsuz) 
- **Async Mimari**: Tam asenkron veritabanı ve HTTP işlemleri

---

## 🏗 Mimari Yapı

```
rag_chatbot/
├── main.py                     # FastAPI uygulama giriş noktası
├── requirements.txt            # Python bağımlılıkları
├── Dockerfile                  # Docker image tanımı
├── docker-compose.yml          # Docker compose (app + postgres + redis)
├── alembic.ini                 # Alembic konfigürasyonu
├── load_comments.py            # Excel'den yorum yükleme scripti
├── create_embeddings.py        # Embedding oluşturma scripti
│
├── alembic/                    # Database migrations
│   └── versions/               # Migration dosyaları
│
└── app/
    ├── __init__.py
    │
    ├── agents/                 # LangGraph agent modülü
    │   ├── graph.py            # Graph builder ve compiler
    │   ├── nodes.py            # Graph node fonksiyonları (8 node)
    │   ├── prompts.py          # System prompt'ları
    │   └── state.py            # Agent state tanımı
    │
    ├── api/                    # HTTP API katmanı
    │   ├── router.py           # Ana router
    │   └── routes/
    │       ├── auth.py         # Kimlik doğrulama endpoint'leri
    │       ├── chat.py         # Sohbet endpoint'leri
    │       └── comments.py     # Yorum CRUD endpoint'leri
    │
    ├── core/                   # Temel yapılandırmalar
    │   ├── config.py           # Ortam değişkenleri
    │   ├── dependencies.py     # FastAPI dependency injection
    │   ├── exceptions.py       # Özel exception sınıfları
    │   ├── redis.py            # Redis bağlantı yönetimi
    │   └── security.py         # JWT ve şifreleme
    │
    ├── db/                     # Veritabanı katmanı
    │   └── database.py         # SQLAlchemy engine ve session
    │
    ├── models/                 # SQLAlchemy ORM modelleri
    │   ├── user.py             # User modeli
    │   ├── conversation.py     # Conversation modeli
    │   └── comment.py          # Comment modeli (sentiment analizi)
    │
    ├── repositories/           # Veritabanı işlemleri
    │   ├── base.py             # Generic CRUD repository
    │   ├── user_repository.py  # User CRUD işlemleri
    │   ├── conversation_repository.py  # Conversation CRUD
    │   └── comment_repository.py       # Comment CRUD
    │
    ├── schemas/                # Pydantic şemaları
    │   ├── user.py             # User request/response
    │   ├── chat.py             # Chat request/response
    │   └── comment.py          # Comment request/response
    │
    └── services/               # Business logic katmanı
        ├── chat_service.py     # Sohbet iş mantığı
        └── vector_store.py     # Redis Vector Store (RAG)
```

### Katmanlı Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Routes)                        │
│         auth.py | chat.py | comments.py                      │
├─────────────────────────────────────────────────────────────┤
│                  Service Layer                               │
│         chat_service.py | vector_store.py                    │
├─────────────────────────────────────────────────────────────┤
│                Repository Layer                              │
│         user_repository | conversation_repository            │
│         comment_repository                                   │
├─────────────────────────────────────────────────────────────┤
│                  Model Layer                                 │
│         User | Conversation | Comment                        │
├─────────────────────────────────────────────────────────────┤
│                 Agent Layer (LangGraph)                      │
│         3-yönlü router → SQL → RAG → Response               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠 Teknolojiler

| Kategori | Teknoloji | Versiyon | Açıklama |
|----------|-----------|----------|----------|
| **Web Framework** | FastAPI | 0.121.2 | Modern async Python web framework |
| **ORM** | SQLAlchemy | 2.0.44 | Async SQLAlchemy ORM |
| **Migrations** | Alembic | 1.17.2 | Database migrations |
| **Veritabanı** | PostgreSQL | 16 | İlişkisel veritabanı |
| **Cache/Vector** | Redis Stack | Latest | Vector Store + Checkpointer |
| **AI Framework** | LangGraph | 1.0.3 | Agent workflow orchestration |
| **LLM** | OpenAI GPT | GPT-4o | Dil modeli |
| **Embeddings** | OpenAI | text-embedding-3-small | 1536-dim embeddings |
| **Vector Search** | RedisVL | 0.12.1 | Redis Vector Library |
| **LangChain** | langchain-openai | 1.0.3 | OpenAI entegrasyonu |
| **Validasyon** | Pydantic | 2.12.4 | Data validation |
| **Auth** | python-jose | 3.5.0 | JWT token |
| **Şifreleme** | passlib + bcrypt | - | Password hashing |
| **Excel** | pandas | - | Excel dosyası işleme |
| **Async HTTP** | httpx | 0.28.1 | Async HTTP client |

---

## ⚙ Kurulum

### Ön Gereksinimler

- Python 3.13+
- PostgreSQL 16+
- Redis Stack 7+ (RedisJSON modülü gerekli)
- Docker & Docker Compose (önerilen)

### 1. Ortam Değişkenleri

Proje kökünde `.env` dosyası oluşturun:

```env
# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_NAME=RAG Chatbot
DEBUG=false
ENVIRONMENT=development

# =============================================================================
# DATABASE
# =============================================================================
DATABASE_URL=postgresql+asyncpg://postgres:sifre123@localhost:5432/rag_chatbot
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# =============================================================================
# AUTHENTICATION
# =============================================================================
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# REDIS
# =============================================================================
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# OPENAI
# =============================================================================
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# =============================================================================
# RATE LIMITING
# =============================================================================
RATE_LIMIT_PER_MINUTE=60

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL=INFO
```

### 2. Docker ile Kurulum (Önerilen)

```bash
# Repository klonla
git clone <repo-url>
cd rag_chatbot

# .env dosyasını oluştur (OPENAI_API_KEY ekle)
cp .env.example .env

# Tüm servisleri başlat (app + postgres + redis)
docker compose up -d

# Logları takip et
docker compose logs -f web
```

### 3. Manuel Kurulum

```bash
# Repository klonla
git clone <repo-url>
cd rag_chatbot

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# PostgreSQL veritabanını oluştur
createdb rag_chatbot

# Redis Stack'i başlat (lokal geliştirme için)
docker run -d -p 6379:6379 redis/redis-stack-server:latest

# Database migrations (opsiyonel - uygulama auto-create yapar)
alembic upgrade head

# Uygulamayı başlat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📥 Veri Yükleme

### 1. Excel'den Yorum Yükleme

Yorumları `comments_test.xlsx` dosyasından veritabanına yüklemek için:

```bash
python load_comments.py
```

**Excel Formatı:**
| Kolon | Açıklama |
|-------|----------|
| Firma/Marka | Şirket adı (Nike, Adidas vb.) |
| Ürün Kategorisi | Spor Ayakkabı, Kozmetik, Elektronik vb. |
| Kategori | Performans, Paketleme, Satıcı, Kargo Hızı |
| Sentiment | Olumlu/Olumsuz |
| Yorum Metni | Yorum içeriği |

### 2. Embedding Oluşturma (RAG için)

Semantic search için yorumların embedding'lerini oluşturmak için:

```bash
python create_embeddings.py
```

Bu script:
1. Redis Vector Index oluşturur (`comments_idx`)
2. Tüm yorumları OpenAI `text-embedding-3-small` modeli ile embedding'e çevirir
3. Redis'te `comment:{id}` formatında saklar

**Not:** Embedding oluşturma OpenAI API kullanır ve ücretlidir.

---

## 📚 API Referansı

Base URL: `http://localhost:8000/api/v1`

### Kimlik Doğrulama (Authentication)

#### POST `/auth/signup` - Kullanıcı Kaydı

```json
// Request
{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
}

// Response (201 Created)
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-12-05T10:30:00Z"
}
```

#### POST `/auth/login` - Giriş

```
// Request (form-data)
username: user@example.com
password: securepassword123

// Response (200 OK)
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

---

### Sohbet (Chat)

> ⚠️ Tüm chat endpoint'leri JWT token gerektirir.
> Header: `Authorization: Bearer <token>`

#### POST `/chat` - Mesaj Gönder

AI'a mesaj gönderir. Soru tipine göre otomatik yönlendirme yapılır.

```json
// Request
{
    "message": "Olumsuz yorum sayısı kaç?",
    "conversation_id": null
}

// Response (200 OK)
{
    "response": "Veritabanında toplam 245 olumsuz yorum bulunmaktadır.",
    "conversation_id": "abc-123-def-456"
}
```

**Örnek Sorular:**

| Soru | Yönlendirme | Açıklama |
|------|-------------|----------|
| "Merhaba" | chitchat | Genel sohbet |
| "Kaç yorum var?" | sql_only | SQL COUNT sorgusu |
| "Nike yorumlarını listele" | sql_only | SQL SELECT sorgusu |
| "Şikayet konularını özetle" | sql_then_rag | SQL + Semantic search |
| "Hakaret içeren yorumlar" | sql_then_rag | İçerik analizi |

#### GET `/chat/conversations` - Konuşmaları Listele

```json
// Response (200 OK)
{
    "conversations": [
        {
            "id": "abc-123-def-456",
            "title": "Olumsuz yorum sayısı",
            "created_at": "2025-12-05T10:30:00Z",
            "last_message_at": "2025-12-05T10:35:00Z",
            "message_count": 4
        }
    ],
    "total": 1
}
```

#### GET `/chat/conversations/{conversation_id}` - Konuşma Geçmişi

#### DELETE `/chat/conversations/{conversation_id}` - Konuşma Sil

---

### Yorumlar (Comments)

#### POST `/comments` - Yorum Oluştur

```json
// Request
{
    "content": "Ürün kalitesi çok iyi, teşekkürler!",
    "company": "Nike",
    "category": "Performans",
    "product_category": "Spor Ayakkabı",
    "sentiment_result": "POSITIVE"
}

// Response (201 Created)
{
    "id": 1,
    "content": "Ürün kalitesi çok iyi, teşekkürler!",
    "company": "Nike",
    "category": "Performans",
    "product_category": "Spor Ayakkabı",
    "sentiment_result": "Olumlu",
    "created_at": "2025-12-05T10:30:00Z",
    "updated_at": "2025-12-05T10:30:00Z"
}
```

#### GET `/comments` - Yorumları Listele

**Query Parameters:**
- `limit` (int, default: 50): Sayfa başına sonuç
- `offset` (int, default: 0): Atlama sayısı
- `company` (string, optional): Şirket filtresi
- `category` (string, optional): Kategori filtresi
- `sentiment` (string, optional): POSITIVE veya NEGATIVE

```json
// Response (200 OK)
{
    "comments": [
        {
            "id": 1,
            "content": "Ürün kalitesi çok iyi!",
            "company": "Nike",
            "category": "Performans",
            "product_category": "Spor Ayakkabı",
            "sentiment_result": "Olumlu",
            "created_at": "2025-12-05T10:30:00Z",
            "updated_at": "2025-12-05T10:30:00Z"
        }
    ],
    "total": 150
}
```

#### GET `/comments/{comment_id}` - Tek Yorum Getir

#### PUT `/comments/{comment_id}` - Yorum Güncelle

#### DELETE `/comments/{comment_id}` - Yorum Sil

---

### Sistem Endpoint'leri

#### GET `/health` - Sağlık Kontrolü

```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

#### GET `/` - Root

```json
{
    "message": "RAG Chatbot API",
    "docs": "/docs",
    "health": "/health"
}
```

---

## 📦 Modüller

### 1. Agents Modülü (`app/agents/`)

LangGraph ile AI agent implementasyonu.

#### state.py - Agent State

```python
class AgentState(TypedDict):
    # Message history
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]
    
    # Identifiers
    user_id: str
    thread_id: str
    
    # Current turn
    last_question: str
    last_answer: str
    
    # Agent routing
    agent_type: Optional[Literal["chitchat", "sql_only", "sql_then_rag"]]
    
    # SQL fields
    sql_query: Optional[str]
    sql_results: Optional[str]
    sql_results_for_rag: Optional[list[dict]]
    
    # RAG fields
    rag_results: Optional[list[dict]]
    
    # Error
    error: Optional[str]
```

#### nodes.py - Graph Node'ları

| Node | Fonksiyon | Açıklama |
|------|-----------|----------|
| `add_user_message` | User mesajını state'e ekler | HumanMessage oluşturur |
| `route_question` | Soruyu sınıflandırır | chitchat/sql_only/sql_then_rag |
| `chitchat_response` | Basit sohbet cevabı | Genel konuşma |
| `generate_sql` | SQL sorgusu üretir | PostgreSQL SELECT |
| `execute_sql` | SQL çalıştırır | Veritabanı sorgusu |
| `interpret_sql_results` | SQL sonuçlarını yorumlar | Sayısal sonuçlar |
| `rag_search` | Semantic search yapar | Redis Vector Store |
| `analyze_rag_results` | RAG sonuçlarını analiz eder | İçerik analizi |
| `add_ai_message` | AI cevabını state'e ekler | AIMessage oluşturur |

#### prompts.py - System Prompt'ları

| Prompt | Kullanım |
|--------|----------|
| `ROUTER_PROMPT` | 3-yönlü soru sınıflandırma |
| `CHITCHAT_PROMPT` | Basit sohbet |
| `SQL_GENERATION_PROMPT` | PostgreSQL sorgu üretimi |
| `SQL_INTERPRETATION_PROMPT` | SQL sonuç yorumlama |
| `RAG_ANALYSIS_PROMPT` | Semantic search sonuç analizi |

---

### 2. Services Modülü (`app/services/`)

#### vector_store.py - Redis Vector Store

```python
# Embedding modeli
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 1536-dim

# Index şeması
INDEX_SCHEMA = {
    "index": {"name": "comments_idx", "prefix": "comment:"},
    "fields": [
        {"name": "id", "type": "tag"},
        {"name": "content", "type": "text"},
        {"name": "company", "type": "tag"},
        {"name": "embedding", "type": "vector", "attrs": {"dims": 1536, "algorithm": "flat"}}
    ]
}

# Semantic search
results = await search_similar_comments(
    query="kargo gecikmesi şikayeti",
    top_k=20,
    sentiment_filter="NEGATIVE"  # Opsiyonel
)
```

**Fonksiyonlar:**

| Fonksiyon | Açıklama |
|-----------|----------|
| `create_index()` | Redis Vector Index oluşturur |
| `add_comment_embedding()` | Tek yorumu embedding'e çevirir |
| `search_similar_comments()` | Semantic search yapar |
| `get_embedding_count()` | Toplam embedding sayısı |

---

### 3. Models Modülü (`app/models/`)

#### Comment Model

```python
class SentimentType(PyEnum):
    POSITIVE = "Olumlu"
    NEGATIVE = "Olumsuz"

class Comment(Base):
    __tablename__ = "comments"
    
    id: Mapped[int]                     # Primary key
    content: Mapped[str]                # Yorum içeriği (Text)
    company: Mapped[str]                # Şirket/marka adı
    category: Mapped[str]               # Yorum kategorisi
    product_category: Mapped[str]       # Ürün kategorisi
    sentiment_result: Mapped[SentimentType]  # Olumlu/Olumsuz
    created_at: Mapped[datetime]        # Oluşturulma tarihi
    updated_at: Mapped[datetime]        # Güncellenme tarihi
```

---

## 🗃 Veritabanı Şeması

### ER Diyagramı

```
┌────────────────────┐       ┌────────────────────────┐
│       users        │       │     conversations      │
├────────────────────┤       ├────────────────────────┤
│ id (PK)            │◄──────│ user_id (FK)           │
│ email              │       │ id (PK, UUID)          │
│ hashed_password    │       │ title                  │
│ full_name          │       │ summary                │
│ is_active          │       │ created_at             │
│ is_superuser       │       │ last_message_at        │
│ created_at         │       └────────────────────────┘
│ updated_at         │
└────────────────────┘

┌────────────────────────────┐
│         comments           │
├────────────────────────────┤
│ id (PK)                    │
│ content (TEXT)             │
│ company                    │
│ category                   │
│ product_category           │
│ sentiment_result (ENUM)    │
│ created_at                 │
│ updated_at                 │
└────────────────────────────┘
```

### SQL Schema

```sql
-- Comments tablosu
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    company VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    product_category VARCHAR(255) NOT NULL,
    sentiment_result VARCHAR(50) NOT NULL,  -- 'POSITIVE' veya 'NEGATIVE'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_comments_id ON comments(id);
```

---

## 🔄 LangGraph Akışı

### Graph Görselleştirmesi

```
                    ┌─────────────────┐
                    │     START       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ add_user_message│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  route_question │
                    │   (3-yönlü)     │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │  chitchat  │    │ sql_only   │    │sql_then_rag│
    │  response  │    │            │    │            │
    └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
          │                 │                 │
          │           ┌─────▼──────┐    ┌─────▼──────┐
          │           │generate_sql│    │generate_sql│
          │           └─────┬──────┘    └─────┬──────┘
          │                 │                 │
          │           ┌─────▼──────┐    ┌─────▼──────┐
          │           │ execute_sql│    │ execute_sql│
          │           └─────┬──────┘    └─────┬──────┘
          │                 │                 │
          │           ┌─────▼──────┐    ┌─────▼──────┐
          │           │ interpret  │    │ rag_search │
          │           │ results    │    └─────┬──────┘
          │           └─────┬──────┘          │
          │                 │           ┌─────▼──────┐
          │                 │           │  analyze   │
          │                 │           │ rag_results│
          │                 │           └─────┬──────┘
          │                 │                 │
          └────────────────┼─────────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │  add_ai_message │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      END        │
                    └─────────────────┘
```

### Routing Mantığı

```python
# route_question node'u soruyu sınıflandırır
def route_by_agent_type(state: AgentState) -> str:
    return state.get("agent_type", "chitchat")

# Conditional edges
graph.add_conditional_edges(
    "route_question",
    route_by_agent_type,
    {
        "chitchat": "chitchat_response",
        "sql_only": "generate_sql",
        "sql_then_rag": "generate_sql"
    }
)
```

---

## 🔒 Güvenlik

### Kimlik Doğrulama Akışı

```
┌─────────┐       ┌─────────┐       ┌─────────┐
│  Client │       │   API   │       │   DB    │
└────┬────┘       └────┬────┘       └────┬────┘
     │ POST /login     │                 │
     │────────────────►│                 │
     │                 │ verify_password │
     │                 │ create_token    │
     │◄────────────────│                 │
     │ {access_token}  │                 │
     │                 │                 │
     │ GET /chat       │                 │
     │ Bearer <token>  │                 │
     │────────────────►│                 │
     │                 │ decode_token    │
     │◄────────────────│                 │
     │ {response}      │                 │
```

### Güvenlik Özellikleri

| Özellik | Implementasyon |
|---------|----------------|
| Password Hashing | bcrypt (passlib) |
| Token | JWT (HS256) |
| Token Expiry | 30 dakika (yapılandırılabilir) |
| User Isolation | Her conversation user_id ile izole |
| CORS | Yapılandırılabilir origins |

---

## 🐳 Docker

### Docker Compose Servisleri

| Servis | Image | Port | Açıklama |
|--------|-------|------|----------|
| `db` | postgres:16-alpine | 5432 | PostgreSQL veritabanı |
| `redis` | redis/redis-stack-server:latest | 6379 | Redis Stack (Vector Store + Checkpointer) |
| `web` | Build from Dockerfile | 8000 | FastAPI uygulaması |

### Komutlar

```bash
# Tüm servisleri başlat
docker compose up -d

# Servisleri durdur
docker compose down

# Logları görüntüle
docker compose logs -f

# Veritabanını sıfırla (Redis dahil)
docker compose down -v
docker compose up -d

# Sadece web servisini yeniden başlat
docker compose restart web
```

---

## 🧪 API Test Örnekleri

### cURL ile Test

```bash
# 1. Kullanıcı kaydı
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# 2. Giriş
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# 3. SQL sorgusu (sayısal)
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"message": "Kaç olumsuz yorum var?"}'

# 4. RAG sorgusu (içerik analizi)
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"message": "Kargo gecikmelerinden şikayet eden yorumları bul"}'

# 5. Yorum listele
curl -X GET "http://localhost:8000/api/v1/comments?limit=10&sentiment=NEGATIVE" \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### Python ile Test

```python
import httpx

base_url = "http://localhost:8000/api/v1"

# Login
response = httpx.post(
    f"{base_url}/auth/login",
    data={"username": "test@example.com", "password": "password123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# SQL sorgusu
response = httpx.post(
    f"{base_url}/chat",
    headers=headers,
    json={"message": "Nike'ın olumlu yorum sayısı kaç?"}
)
print(response.json())

# RAG sorgusu
response = httpx.post(
    f"{base_url}/chat",
    headers=headers,
    json={"message": "Ürün kalitesinden şikayet eden yorumları özetle"}
)
print(response.json())
```

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit'leyin (`git commit -m 'Add amazing feature'`)
4. Push'layın (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

**Geliştirici**: RAG Chatbot Team  
**Versiyon**: 1.0.0  
**Son Güncelleme**: Aralık 2025
