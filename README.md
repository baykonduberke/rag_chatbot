# RAG Chatbot API

LangGraph tabanlı, FastAPI ile geliştirilmiş modern bir yapay zeka sohbet uygulaması.

## 📑 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Mimari Yapı](#-mimari-yapı)
- [Teknolojiler](#-teknolojiler)
- [Kurulum](#-kurulum)
- [API Referansı](#-api-referansı)
- [Modüller](#-modüller)
- [Veritabanı Şeması](#-veritabanı-şeması)
- [LangGraph Akışı](#-langgraph-akışı)
- [Güvenlik](#-güvenlik)
- [Docker](#-docker)

---

## 🎯 Proje Hakkında

Bu proje, kullanıcıların yapay zeka ile sohbet edebileceği bir REST API sunar. Temel özellikleri:

- **Kullanıcı Yönetimi**: Kayıt, giriş ve JWT tabanlı kimlik doğrulama
- **Sohbet Sistemi**: Kullanıcı başına izole edilmiş sohbet oturumları
- **Hafıza Yönetimi**: LangGraph checkpointer ile konuşma geçmişi
- **RAG Desteği**: Retrieval-Augmented Generation altyapısı (genişletilebilir)
- **Async Mimari**: Tam asenkron veritabanı ve HTTP işlemleri

---

## 🏗 Mimari Yapı

```
rag_chatbot/
├── main.py                     # FastAPI uygulama giriş noktası
├── requirements.txt            # Python bağımlılıkları
├── Dockerfile                  # Docker image tanımı
├── docker-compose.yml          # Docker compose (app + postgres + redis)
│
└── app/
    ├── __init__.py
    │
    ├── agents/                 # LangGraph agent modülü
    │   ├── graph.py            # Graph builder ve compiler
    │   ├── nodes.py            # Graph node fonksiyonları
    │   ├── prompts.py          # System prompt'ları
    │   └── state.py            # Agent state tanımı
    │
    ├── api/                    # HTTP API katmanı
    │   ├── router.py           # Ana router
    │   └── routes/
    │       ├── auth.py         # Kimlik doğrulama endpoint'leri
    │       └── chat.py         # Sohbet endpoint'leri
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
    │   └── conversation.py     # Conversation modeli
    │
    ├── repositories/           # Veritabanı işlemleri
    │   ├── base.py             # Generic CRUD repository
    │   ├── user_repository.py  # User CRUD işlemleri
    │   └── conversation_repository.py  # Conversation CRUD
    │
    ├── schemas/                # Pydantic şemaları
    │   ├── user.py             # User request/response
    │   └── chat.py             # Chat request/response
    │
    └── services/               # Business logic katmanı
        └── chat_service.py     # Sohbet iş mantığı
```

### Katmanlı Mimari

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (Routes)                    │
│         HTTP Request/Response işlemleri                  │
├─────────────────────────────────────────────────────────┤
│                  Service Layer                           │
│         Business logic ve orchestration                  │
├─────────────────────────────────────────────────────────┤
│                Repository Layer                          │
│         Veritabanı CRUD işlemleri                        │
├─────────────────────────────────────────────────────────┤
│                  Model Layer                             │
│         SQLAlchemy ORM modelleri                         │
├─────────────────────────────────────────────────────────┤
│                 Agent Layer (LangGraph)                  │
│         AI sohbet akışı ve state yönetimi               │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠 Teknolojiler

| Kategori | Teknoloji | Versiyon | Açıklama |
|----------|-----------|----------|----------|
| **Web Framework** | FastAPI | 0.121.2 | Modern async Python web framework |
| **ORM** | SQLAlchemy | 2.0.44 | Async SQLAlchemy ORM |
| **Veritabanı** | PostgreSQL | 16 | İlişkisel veritabanı |
| **Cache** | Redis Stack | Latest | LangGraph checkpointer (RedisSaver) |
| **AI Framework** | LangGraph | 1.0.3 | Agent workflow orchestration |
| **LLM** | OpenAI GPT | GPT-4o | Dil modeli |
| **LangChain** | langchain-openai | 1.0.3 | OpenAI entegrasyonu |
| **Validasyon** | Pydantic | 2.12.4 | Data validation |
| **Auth** | python-jose | 3.5.0 | JWT token |
| **Şifreleme** | passlib + bcrypt | - | Password hashing |
| **Async HTTP** | httpx | 0.28.1 | Async HTTP client |

---

## ⚙ Kurulum

### Ön Gereksinimler

- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (opsiyonel)

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

### 2. Manuel Kurulum

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

# Uygulamayı başlat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Docker ile Kurulum

```bash
# Tüm servisleri başlat (app + postgres + redis)
docker compose up -d

# Logları takip et
docker compose logs -f web
```

---

## 📚 API Referansı

Base URL: `http://localhost:8000/api/v1`

### Kimlik Doğrulama (Authentication)

#### POST `/auth/signup` - Kullanıcı Kaydı

Yeni kullanıcı oluşturur.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-12-05T10:30:00Z"
}
```

**Olası Hatalar:**
- `409 Conflict`: Email zaten kayıtlı
- `422 Unprocessable Entity`: Validasyon hatası

---

#### POST `/auth/login` - Giriş

JWT access token alır.

**Request Body (form-data):**
```
username: user@example.com
password: securepassword123
```

**Response (200 OK):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Olası Hatalar:**
- `401 Unauthorized`: Yanlış email veya şifre

---

### Sohbet (Chat)

> ⚠️ Tüm chat endpoint'leri JWT token gerektirir.
> Header: `Authorization: Bearer <token>`

#### POST `/chat` - Mesaj Gönder

AI'a mesaj gönderir ve yanıt alır.

**Request Body:**
```json
{
    "message": "Python nedir?",
    "conversation_id": null
}
```

**Response (200 OK):**
```json
{
    "response": "Python, yüksek seviyeli bir programlama dilidir...",
    "conversation_id": "abc-123-def-456"
}
```

**Notlar:**
- `conversation_id: null` → Yeni konuşma başlatır
- `conversation_id: "<id>"` → Mevcut konuşmaya devam eder

---

#### GET `/chat/conversations` - Konuşmaları Listele

Kullanıcının tüm konuşmalarını listeler.

**Query Parameters:**
- `limit` (int, default: 20): Sayfa başına sonuç
- `offset` (int, default: 0): Atlama sayısı

**Response (200 OK):**
```json
{
    "conversations": [
        {
            "id": "abc-123-def-456",
            "title": "Python nedir?",
            "created_at": "2025-12-05T10:30:00Z",
            "last_message_at": "2025-12-05T10:35:00Z",
            "message_count": 4
        }
    ],
    "total": 1
}
```

---

#### GET `/chat/conversations/{conversation_id}` - Konuşma Geçmişi

Belirli bir konuşmanın mesaj geçmişini getirir.

**Path Parameters:**
- `conversation_id` (string): Konuşma ID'si

**Query Parameters:**
- `limit` (int, default: 50): Maksimum mesaj sayısı
- `offset` (int, default: 0): Atlama sayısı

**Response (200 OK):**
```json
{
    "conversation_id": "abc-123-def-456",
    "messages": [
        {
            "role": "human",
            "content": "Python nedir?",
            "timestamp": "2025-12-05T10:30:00Z"
        },
        {
            "role": "assistant",
            "content": "Python, yüksek seviyeli bir programlama dilidir...",
            "timestamp": "2025-12-05T10:30:05Z"
        }
    ],
    "has_more": false
}
```

---

#### DELETE `/chat/conversations/{conversation_id}` - Konuşma Sil

Belirli bir konuşmayı ve tüm mesajlarını siler.

**Response (204 No Content):** Başarılı silme

**Olası Hatalar:**
- `404 Not Found`: Konuşma bulunamadı veya erişim yok

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

### 1. Core Modülü (`app/core/`)

#### config.py - Yapılandırma

Tüm ortam değişkenlerini Pydantic Settings ile yönetir.

```python
class Settings(BaseSettings):
    # App
    APP_NAME: str = "RAG Chatbot"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
```

**Özellikler:**
- `.env` dosyasından otomatik okuma
- Type-safe validasyon
- `@lru_cache` ile singleton pattern

---

#### security.py - Güvenlik

JWT token ve password hashing işlemleri.

**Fonksiyonlar:**

| Fonksiyon | Açıklama |
|-----------|----------|
| `verify_password(plain, hashed)` | Şifreyi doğrular |
| `get_password_hash(password)` | Şifreyi bcrypt ile hashler |
| `create_access_token(subject, expires_delta)` | JWT token oluşturur |
| `decode_access_token(token)` | JWT token'ı decode eder |

**Token Payload:**
```json
{
    "sub": "1",          // User ID
    "exp": 1733400000,   // Expiration timestamp
    "iat": 1733398200,   // Issued at timestamp
    "type": "access"     // Token type
}
```

---

#### dependencies.py - Dependency Injection

FastAPI dependency'leri.

| Dependency | Açıklama |
|------------|----------|
| `get_db()` | Async database session |
| `get_current_user()` | JWT token'dan authenticated user |
| `get_current_active_superuser()` | Superuser kontrolü |

**Authentication:**
```python
# HTTPBearer ile direkt JWT token girişi
from typing import Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

http_bearer = HTTPBearer(
    scheme_name="JWT Token",
    description="JWT token'ı buraya girin (ey... ile başlayan)"
)

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    token = credentials.credentials
    # Token decode ve user getirme...
```

**Type Aliases:**
```python
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

---

#### exceptions.py - Özel Exception'lar

| Exception | HTTP Status | Kullanım |
|-----------|-------------|----------|
| `NotFoundException` | 404 | Kaynak bulunamadı |
| `AlreadyExistsException` | 409 | Duplicate kayıt |
| `UnauthorizedException` | 401 | Auth hatası |
| `ForbiddenException` | 403 | Yetki hatası |
| `ValidationException` | 422 | Validasyon hatası |
| `ExternalServiceException` | 502 | Dış servis hatası |

---

#### redis.py - Redis Yönetimi

Redis bağlantısı ve LangGraph checkpointer. Mesaj geçmişi Redis'te kalıcı olarak saklanır.

```python
# Redis client (async)
await get_redis_client()

# LangGraph checkpointer (RedisSaver - kalıcı)
checkpointer = get_checkpointer_sync()
```

**Özellikler:**
- **RedisSaver**: LangGraph state'ini Redis'te saklar
- **Redis Stack**: RedisJSON modülü ile JSON verilerini destekler
- **setup()**: RediSearch indekslerini otomatik oluşturur
- **Fallback**: Redis bağlantısı başarısızsa MemorySaver kullanılır

**Not:** Redis Stack image'ı (`redis/redis-stack-server`) kullanılmalıdır. Normal Redis (`redis:alpine`) RedisJSON modülünü içermez.

---

### 2. Database Modülü (`app/db/`)

#### database.py

SQLAlchemy async engine ve session factory.

```python
# Engine oluşturma
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base model
class Base(DeclarativeBase):
    pass
```

---

### 3. Models Modülü (`app/models/`)

#### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int]                    # Primary key
    email: Mapped[str]                 # Unique, indexed
    hashed_password: Mapped[str]       # Bcrypt hash
    full_name: Mapped[Optional[str]]   # İsim
    is_active: Mapped[bool]            # Aktiflik durumu
    is_superuser: Mapped[bool]         # Admin yetkisi
    created_at: Mapped[datetime]       # Oluşturulma tarihi
    updated_at: Mapped[datetime]       # Güncellenme tarihi
    
    # Relationships
    conversations: Mapped[list["Conversation"]]
```

#### Conversation Model

```python
class Conversation(Base):
    __tablename__ = "conversations"
    
    id: Mapped[str]                     # UUID primary key
    user_id: Mapped[int]                # Foreign key → users
    title: Mapped[Optional[str]]        # Konuşma başlığı
    summary: Mapped[Optional[str]]      # Özet (RAG için)
    created_at: Mapped[datetime]        # Oluşturulma
    last_message_at: Mapped[datetime]   # Son mesaj zamanı
    
    # Relationships
    user: Mapped["User"]
```

---

### 4. Repository Modülü (`app/repositories/`)

Repository pattern ile veritabanı işlemleri soyutlanır.

#### BaseRepository

```python
class BaseRepository(Generic[ModelType]):
    async def get_by_id(self, id) -> Optional[ModelType]
    async def create(self, obj) -> ModelType
    async def update(self, obj) -> ModelType
    async def delete(self, obj) -> None
```

#### UserRepository

```python
class UserRepository(BaseRepository[User]):
    async def get_by_id(self, user_id: int) -> Optional[User]
    async def get_by_email(self, email: str) -> Optional[User]
    async def exists_by_email(self, email: str) -> bool
```

#### ConversationRepository

```python
class ConversationRepository(BaseRepository[Conversation]):
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]
    async def list_by_user(self, user_id, limit, offset) -> list[Conversation]
    async def count_by_user(self, user_id: int) -> int
```

---

### 5. Schemas Modülü (`app/schemas/`)

Pydantic modelleri API validasyonu ve serialization için.

#### User Schemas

| Schema | Kullanım |
|--------|----------|
| `UserCreate` | Kayıt request |
| `UserUpdate` | Güncelleme request |
| `UserOut` | Response model |
| `Token` | Login response |
| `TokenPayload` | JWT payload |

#### Chat Schemas

| Schema | Kullanım |
|--------|----------|
| `ChatMessageRequest` | Mesaj gönderme request |
| `ChatMessageResponse` | AI yanıtı response |
| `MessageSchema` | Tek mesaj modeli |
| `ConversationSchema` | Konuşma metadata |
| `ConversationListResponse` | Konuşma listesi |
| `ChatHistoryResponse` | Mesaj geçmişi |

---

### 6. Services Modülü (`app/services/`)

#### ChatService

Sohbet business logic'i.

```python
class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.graph = get_compiled_graph(with_memory=True)
        self.conversation_repo = ConversationRepository(db)
    
    async def send_message(
        self, user_id, message, conversation_id
    ) -> ChatMessageResponse
    
    async def get_conversation_history(
        self, conversation_id, user_id, limit, offset
    ) -> list[MessageSchema]
    
    async def list_conversations(
        self, user_id, limit, offset
    ) -> list[ConversationSchema]
    
    async def delete_conversation(
        self, conversation_id, user_id
    ) -> None
```

**`send_message` Akışı:**

```
1. Conversation al veya oluştur
2. AgentState hazırla
3. LangGraph config oluştur (thread_id)
4. Graph invoke et
5. Conversation metadata güncelle
6. Response döndür
```

---

### 7. Agents Modülü (`app/agents/`)

LangGraph ile AI agent implementasyonu.

#### state.py - Agent State

```python
class AgentState(TypedDict):
    # Mesaj geçmişi (LangGraph reducer ile)
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]
    
    # Identifiers
    user_id: str
    thread_id: str
    
    # Mevcut tur verileri
    last_question: str
    last_answer: str
    
    # Opsiyonel
    context: Optional[str]   # RAG context
    error: Optional[str]     # Hata mesajı
```

#### nodes.py - Graph Node'ları

| Node | Fonksiyon | Açıklama |
|------|-----------|----------|
| `add_user_message` | User mesajını state'e ekler | `HumanMessage` oluşturur |
| `generate_response` | LLM yanıtı üretir | OpenAI API çağrısı |
| `add_ai_message` | AI yanıtını state'e ekler | `AIMessage` oluşturur |
| `handle_error` | Hata işleme | Error message döndürür |

**LLM Yapılandırması:**
```python
llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model=settings.OPENAI_MODEL,        # gpt-4o
    temperature=settings.OPENAI_TEMPERATURE,  # 0.7
    max_tokens=settings.OPENAI_MAX_TOKENS     # 2000
)
```

#### graph.py - Graph Tanımı

```python
def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    
    # Node'lar
    graph.add_node("add_user_message", add_user_message)
    graph.add_node("generate_response", generate_response)
    graph.add_node("add_ai_message", add_ai_message)
    graph.add_node("handle_error", handle_error)
    
    # Entry point
    graph.set_entry_point("add_user_message")
    
    # Edge'ler
    graph.add_edge("add_user_message", "generate_response")
    graph.add_edge("generate_response", "add_ai_message")
    graph.add_edge("add_ai_message", END)
    graph.add_edge("handle_error", END)
    
    return graph


def get_compiled_graph(with_memory: bool = True) -> CompiledGraph:
    """Compiled graph singleton."""
    global _compiled_graph
    
    if _compiled_graph is None:
        graph = build_graph()
        if with_memory:
            checkpointer = get_checkpointer_sync()
            _compiled_graph = compile_graph(graph, checkpointer)
        else:
            _compiled_graph = compile_graph(graph)
    
    return _compiled_graph
```

**Import'lar:**
```python
from app.core.redis import get_checkpointer_sync
```

#### prompts.py - System Prompt'ları

```python
SYSTEM_PROMPT = """You are a helpful AI assistant..."""

RAG_CONTEXT_TEMPLATE = """
Based on the following retrieved information...
Retrieved Context: {context}
User Question: {question}
"""

ERROR_PROMPT = """I apologize, but I encountered an issue..."""
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
```

### SQL Schema

```sql
-- Users tablosu
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_users_email ON users(email);

-- Conversations tablosu
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
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
                    │                 │
                    │ User mesajını   │
                    │ state'e ekle    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │generate_response│
                    │                 │
                    │ OpenAI API ile  │
                    │ yanıt üret      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  add_ai_message │
                    │                 │
                    │ AI yanıtını     │
                    │ state'e ekle    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      END        │
                    └─────────────────┘
```

### State Akışı

```
Initial State:
{
    messages: [],
    user_id: "1",
    thread_id: "abc-123",
    last_question: "Python nedir?",
    last_answer: "",
    context: null,
    error: null
}

After add_user_message:
{
    messages: [HumanMessage("Python nedir?")],
    ...
}

After generate_response:
{
    messages: [HumanMessage("Python nedir?")],
    last_answer: "Python, yüksek seviyeli...",
    ...
}

After add_ai_message:
{
    messages: [
        HumanMessage("Python nedir?"),
        AIMessage("Python, yüksek seviyeli...")
    ],
    last_answer: "Python, yüksek seviyeli...",
    ...
}
```

### Checkpointer ile Hafıza

```python
# Her thread_id için ayrı state
config = {
    "configurable": {
        "thread_id": "conversation-uuid"
    }
}

# Graph invoke
result = graph.invoke(state, config)

# State'i geri al
saved_state = graph.get_state(config)
```

---

## 🔒 Güvenlik

### Kimlik Doğrulama Akışı

```
┌─────────┐       ┌─────────┐       ┌─────────┐
│  Client │       │   API   │       │   DB    │
└────┬────┘       └────┬────┘       └────┬────┘
     │                 │                 │
     │ POST /login     │                 │
     │ (email, pass)   │                 │
     │────────────────►│                 │
     │                 │ get user by     │
     │                 │ email           │
     │                 │────────────────►│
     │                 │◄────────────────│
     │                 │                 │
     │                 │ verify_password │
     │                 │ (bcrypt)        │
     │                 │                 │
     │                 │ create_token    │
     │                 │ (JWT)           │
     │                 │                 │
     │◄────────────────│                 │
     │ {access_token}  │                 │
     │                 │                 │
     │ GET /chat       │                 │
     │ Auth: Bearer    │                 │
     │────────────────►│                 │
     │                 │ decode_token    │
     │                 │ get_current_user│
     │                 │────────────────►│
     │                 │◄────────────────│
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

### Password Hashing

```python
# Hash oluşturma
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("password123")

# Doğrulama
is_valid = pwd_context.verify("password123", hashed)
```

---

## 🐳 Docker

### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Güvenlik: root olmayan kullanıcı
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Servisleri

#### docker-compose.yml

| Servis | Image | Port | Açıklama |
|--------|-------|------|----------|
| `db` | postgres:16-alpine | 5432 | PostgreSQL veritabanı |
| `redis` | redis/redis-stack-server:latest | 6379 | Redis Stack (RedisSaver için RedisJSON) |
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

# 3. Mesaj gönder
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"message": "Merhaba, nasılsın?"}'

# 4. Konuşma listesi
curl -X GET "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# 5. Konuşma geçmişi
curl -X GET "http://localhost:8000/api/v1/chat/conversations/<CONVERSATION_ID>" \
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

# Chat
headers = {"Authorization": f"Bearer {token}"}
response = httpx.post(
    f"{base_url}/chat",
    headers=headers,
    json={"message": "Python hakkında bilgi ver"}
)
print(response.json())
```

---

## 📈 Genişletme Önerileri

### 1. RAG Implementasyonu

```python
# nodes.py'ye eklenecek
def retrieve_context(state: AgentState) -> dict:
    """Vector store'dan ilgili dökümanları getir."""
    query = state["last_question"]
    
    # Embedding oluştur
    embeddings = OpenAIEmbeddings()
    query_embedding = embeddings.embed_query(query)
    
    # Vector store'da ara
    results = vector_store.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in results])
    
    return {"context": context}
```

### 2. Streaming Response

```python
# Streaming endpoint
@router.post("/chat/stream")
async def stream_message(
    request: ChatMessageRequest,
    current_user: CurrentUser
):
    async def generate():
        async for chunk in llm.astream(messages):
            yield f"data: {chunk.content}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("60/minute")
async def send_message(...):
    ...
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

