# 📚 RAG Chatbot - Junior Developer Rehberi

Bu rehber, projedeki her dosyayı satır satır açıklayarak, bir junior yazılımcının tüm mimariyi ve kodları anlamasını hedefler.

---

## 📖 İçindekiler

1. [Giriş ve Temel Kavramlar](#-giriş-ve-temel-kavramlar)
2. [main.py - Uygulama Giriş Noktası](#-mainpy---uygulama-giriş-noktası)
3. [Core Modülü](#-core-modülü)
   - [config.py](#configpy---yapılandırma)
   - [security.py](#securitypy---güvenlik)
   - [dependencies.py](#dependenciespy---dependency-injection)
   - [exceptions.py](#exceptionspy---özel-hatalar)
   - [redis.py](#redispy---redis-yönetimi)
4. [Database Modülü](#-database-modülü)
5. [Models Modülü](#-models-modülü)
6. [Schemas Modülü](#-schemas-modülü)
7. [Repositories Modülü](#-repositories-modülü)
8. [Services Modülü](#-services-modülü)
9. [Agents Modülü (LangGraph)](#-agents-modülü-langgraph)
10. [API Modülü](#-api-modülü)
11. [Docker Dosyaları](#-docker-dosyaları)

---

## 🎓 Giriş ve Temel Kavramlar

### Bu Projede Kullanılan Temel Kavramlar

Koda geçmeden önce, bu projede kullanılan temel kavramları anlayalım:

#### 1. FastAPI Nedir?
FastAPI, Python ile hızlı API'ler oluşturmak için kullanılan modern bir web framework'üdür.

```python
# Basit bir FastAPI örneği
from fastapi import FastAPI

app = FastAPI()

@app.get("/merhaba")
def merhaba():
    return {"mesaj": "Merhaba Dünya!"}
```

#### 2. Async/Await Nedir?
Asenkron programlama, bir işlemin tamamlanmasını beklerken başka işler yapabilmemizi sağlar.

```python
# Senkron (normal) kod - bekler
def veri_cek():
    sonuc = veritabani_sorgusu()  # 5 saniye bekler
    return sonuc

# Asenkron kod - beklerken başka iş yapabilir
async def veri_cek():
    sonuc = await veritabani_sorgusu()  # Beklerken CPU başka iş yapabilir
    return sonuc
```

#### 3. ORM (Object-Relational Mapping) Nedir?
Veritabanı tablolarını Python sınıfları olarak temsil etmemizi sağlar.

```python
# SQL yerine:
# SELECT * FROM users WHERE id = 1

# Python ile:
user = await session.get(User, 1)
```

#### 4. JWT (JSON Web Token) Nedir?
Kullanıcı kimliğini doğrulamak için kullanılan şifreli bir token.

```
eyJhbGciOiJIUzI1NiIs...  ← Bu bir JWT token
```

#### 5. Dependency Injection Nedir?
Bir fonksiyonun ihtiyaç duyduğu şeylerin otomatik olarak sağlanması.

```python
# Dependency Injection olmadan:
def kullanici_getir():
    db = Database()  # Her seferinde manuel oluşturuyoruz
    return db.query(...)

# Dependency Injection ile:
def kullanici_getir(db: Database = Depends(get_db)):
    return db.query(...)  # db otomatik sağlanıyor
```

#### 6. Repository Pattern Nedir?
Veritabanı işlemlerini ayrı bir katmanda toplamak.

```python
# Repository olmadan (kötü):
@app.get("/user/{id}")
def get_user(id: int, db: Session):
    return db.query(User).filter(User.id == id).first()

# Repository ile (iyi):
@app.get("/user/{id}")
def get_user(id: int, user_repo: UserRepository):
    return user_repo.get_by_id(id)
```

#### 7. LangGraph Nedir?
AI agent'ları için workflow (iş akışı) oluşturmamızı sağlayan bir kütüphane.

```
Kullanıcı Mesajı → [Node 1] → [Node 2] → [Node 3] → AI Yanıtı
```

---

## 🚀 main.py - Uygulama Giriş Noktası

Bu dosya, tüm uygulamanın başladığı yerdir. Adım adım inceleyelim:

```python
"""
FastAPI Application Entry Point

Bu dosya:
1. FastAPI app instance'ı oluşturur
2. Middleware'leri ekler
3. Router'ları bağlar
4. Startup/shutdown event'lerini yönetir
"""
```

**📝 Açıklama:** Dosyanın başındaki bu yorum bloğu (docstring), dosyanın ne yaptığını açıklar. Her Python dosyasının başına böyle açıklamalar yazmak iyi bir pratiktir.

---

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.redis import close_redis
from app.db.database import engine, Base
```

**📝 Açıklama - Import'lar:**

| Import | Ne İşe Yarar |
|--------|--------------|
| `asynccontextmanager` | Async context manager oluşturmak için (with bloğu) |
| `FastAPI` | Web framework'ümüz |
| `CORSMiddleware` | Farklı domain'lerden gelen isteklere izin vermek için |
| `api_router` | Tüm API endpoint'lerimizi içeren router |
| `settings` | Ortam değişkenlerimiz |
| `close_redis` | Redis bağlantısını kapatmak için |
| `engine, Base` | Veritabanı engine ve base model |

---

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle yönetimi."""
    # ===== STARTUP =====
    print("🚀 Application starting...")
    
    # Database tablolarını oluştur (yoksa)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables ready")
    
    yield  # ← Uygulama burada çalışır
    
    # ===== SHUTDOWN =====
    print("👋 Application shutting down...")
    await close_redis()
    print("✅ Redis connection closed")
    await engine.dispose()
    print("✅ Cleanup completed")
```

**📝 Açıklama - Lifespan (Yaşam Döngüsü):**

Bu fonksiyon, uygulamanın başlangıç ve bitiş anlarını yönetir.

```
STARTUP (yield'den önce)     RUNNING (yield)     SHUTDOWN (yield'den sonra)
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐      ┌───────────────┐      ┌─────────────────┐
│ DB tabloları    │      │  Uygulama     │      │ Redis kapat     │
│ oluştur         │  →   │  çalışıyor    │  →   │ DB engine kapat │
└─────────────────┘      └───────────────┘      └─────────────────┘
```

**`yield` nedir?**
```python
# yield, fonksiyonu ikiye böler:
# yield'den ÖNCE: Startup kodu
# yield'den SONRA: Shutdown kodu

async def lifespan(app):
    print("Başlangıç")  # Uygulama açılırken çalışır
    yield
    print("Bitiş")      # Uygulama kapanırken çalışır
```

---

```python
# FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    description="LangGraph tabanlı RAG Chatbot API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
```

**📝 Açıklama - App Oluşturma:**

| Parametre | Açıklama | Zorunlu mu? |
|-----------|----------|-------------|
| `title` | Swagger UI ve ReDoc'ta görünen başlık | Hayır (default: "FastAPI") |
| `description` | API açıklaması (dokümantasyonda görünür) | Hayır |
| `version` | API versiyonu (dokümantasyonda görünür) | Hayır |
| `lifespan` | Başlangıç/bitiş yöneticisi | Hayır (ama önerilir) |
| `docs_url` | Swagger UI adresi | Hayır (default: "/docs") |
| `redoc_url` | ReDoc adresi | Hayır (default: "/redoc") |
| `openapi_url` | OpenAPI JSON schema adresi | Hayır (default: "/openapi.json") |

---

### 📖 Detaylı Açıklamalar

#### 1. `docs_url="/docs"` - Swagger UI

**Swagger UI Nedir?**
Swagger UI, API'nizi interaktif bir arayüzde test etmenizi sağlayan bir web arayüzüdür.

**Nasıl Kullanılır?**
```
1. Uygulamayı başlat: uvicorn main:app --reload
2. Tarayıcıda aç: http://localhost:8000/docs
3. Endpoint'leri gör, test et, "Try it out" butonuna tıkla
```

**Ne İşe Yarar?**
- ✅ Tüm endpoint'leri görselleştirir
- ✅ Request/Response örneklerini gösterir
- ✅ Doğrudan tarayıcıdan API test edebilirsiniz
- ✅ "Authorize" butonu ile JWT token ekleyebilirsiniz
- ✅ Schema validasyonlarını gösterir

**Örnek Görünüm:**
```
┌─────────────────────────────────────────┐
│  RAG Chatbot API              [Authorize]│
├─────────────────────────────────────────┤
│  POST /api/v1/auth/signup                │
│  ┌───────────────────────────────────┐  │
│  │ Request body                      │  │
│  │ {                                 │  │
│  │   "email": "test@example.com",   │  │
│  │   "password": "password123"       │  │
│  │ }                                 │  │
│  │ [Try it out]                      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Devre Dışı Bırakmak:**
```python
# Swagger UI'ı kapatmak için:
app = FastAPI(docs_url=None)  # Artık /docs çalışmaz
```

---

#### 2. `redoc_url="/redoc"` - ReDoc

**ReDoc Nedir?**
ReDoc, API dokümantasyonunu daha okunabilir ve temiz bir şekilde gösteren alternatif bir arayüzdür.

**Swagger UI vs ReDoc:**

| Özellik | Swagger UI | ReDoc |
|---------|------------|-------|
| **Görünüm** | İnteraktif, test edilebilir | Sadece dokümantasyon |
| **Kullanım** | API test etmek için | Dokümantasyon okumak için |
| **"Try it out"** | ✅ Var | ❌ Yok |
| **Tasarım** | Daha karmaşık | Daha temiz ve okunabilir |
| **Hedef Kitle** | Geliştiriciler (test için) | Dokümantasyon okuyucuları |

**Nasıl Kullanılır?**
```
1. Tarayıcıda aç: http://localhost:8000/redoc
2. Tüm endpoint'leri, schema'ları ve örnekleri gör
3. Sol menüden hızlıca gezin
```

**Ne Zaman Kullanılır?**
- 📖 API dokümantasyonunu okumak için
- 📋 Endpoint'leri ve schema'ları incelemek için
- 🎨 Daha temiz ve profesyonel görünüm için
- 📱 Mobil cihazlarda daha iyi görünür

**Örnek Görünüm:**
```
┌─────────────────────────────────────────┐
│  RAG Chatbot API                        │
│  Version: 1.0.0                         │
├─────────────────────────────────────────┤
│  Authentication                         │
│  ├── POST /api/v1/auth/signup           │
│  │   Register new user                  │
│  │   Request: UserCreate               │
│  │   Response: UserOut                  │
│  │                                      │
│  └── POST /api/v1/auth/login            │
│      Login and get token                │
│      Request: OAuth2PasswordRequestForm │
│      Response: Token                    │
└─────────────────────────────────────────┘
```

**Devre Dışı Bırakmak:**
```python
# ReDoc'ı kapatmak için:
app = FastAPI(redoc_url=None)  # Artık /redoc çalışmaz
```

---

#### 3. `openapi_url="/openapi.json"` - OpenAPI Schema

**OpenAPI Nedir?**
OpenAPI (eski adı Swagger), RESTful API'leri tanımlamak için kullanılan bir spesifikasyondur. JSON veya YAML formatında API'nizin tüm detaylarını içerir.

**OpenAPI JSON Ne İçerir?**
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "RAG Chatbot API",
    "version": "1.0.0"
  },
  "paths": {
    "/api/v1/auth/signup": {
      "post": {
        "summary": "Register new user",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/UserCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "User created",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UserOut"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "UserCreate": {
        "type": "object",
        "properties": {
          "email": {"type": "string", "format": "email"},
          "password": {"type": "string", "minLength": 8}
        }
      }
    }
  }
}
```

**Nerede Kullanılır?**

1. **Frontend Geliştirme:**
   ```javascript
   // Frontend'de API client oluşturmak için
   import { OpenAPIClient } from 'openapi-client';
   
   const client = await OpenAPIClient.fromURL('http://localhost:8000/openapi.json');
   // Artık tüm endpoint'ler type-safe olarak kullanılabilir
   ```

2. **API Client Generation:**
   ```bash
   # openapi-generator ile client kodu üret
   openapi-generator generate \
     -i http://localhost:8000/openapi.json \
     -g typescript-axios \
     -o ./frontend/src/api
   ```

3. **Postman Import:**
   ```
   Postman → Import → Link
   URL: http://localhost:8000/openapi.json
   → Tüm endpoint'ler otomatik import edilir
   ```

4. **API Testing Tools:**
   - Insomnia
   - Bruno
   - HTTPie
   - Bu araçlar OpenAPI schema'yı okuyup endpoint'leri otomatik oluşturur

5. **Dokümantasyon Araçları:**
   - Swagger UI (kendi schema'sını okur)
   - ReDoc (kendi schema'sını okur)
   - Stoplight Elements
   - Scalar API Reference

**Nasıl Erişilir?**
```bash
# Tarayıcıda:
http://localhost:8000/openapi.json

# cURL ile:
curl http://localhost:8000/openapi.json

# Python ile:
import requests
schema = requests.get("http://localhost:8000/openapi.json").json()
```

**Örnek Kullanım Senaryoları:**

**Senaryo 1: Frontend TypeScript Client**
```typescript
// openapi-typescript ile type-safe client
import openapi from './openapi.json';

type UserCreate = openapi.components.schemas.UserCreate;
type UserOut = openapi.components.schemas.UserOut;

async function signup(data: UserCreate): Promise<UserOut> {
  const response = await fetch('/api/v1/auth/signup', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  return response.json();
}
```

**Senaryo 2: API Mocking**
```python
# Prism ile mock server oluştur
prism mock http://localhost:8000/openapi.json
# → Frontend geliştirirken backend'e ihtiyaç yok
```

**Senaryo 3: API Validation**
```python
# openapi-spec-validator ile schema doğrulama
from openapi_spec_validator import validate_spec

with open('openapi.json') as f:
    spec = json.load(f)
    validate_spec(spec)  # Schema geçerli mi kontrol et
```

**Devre Dışı Bırakmak:**
```python
# OpenAPI schema'yı kapatmak için:
app = FastAPI(openapi_url=None)  # Artık /openapi.json çalışmaz
# ⚠️ DİKKAT: Bu durumda Swagger UI ve ReDoc da çalışmaz!
```

---

### 🤔 Bunlar Gerekli mi?

**Kısa Cevap:** Hayır, zorunlu değiller ama **kesinlikle önerilirler**.

**Detaylı Açıklama:**

| Özellik | Gerekli mi? | Neden? |
|---------|-------------|--------|
| **Swagger UI** | ❌ Hayır | ✅ Ama çok faydalı - API test etmek için |
| **ReDoc** | ❌ Hayır | ✅ Ama çok faydalı - Temiz dokümantasyon için |
| **OpenAPI JSON** | ❌ Hayır | ✅ Ama çok faydalı - Frontend/client generation için |

**Ne Zaman Kapatılabilir?**

1. **Production'da Güvenlik İçin:**
   ```python
   # Production'da dokümantasyonu kapat
   app = FastAPI(
       docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
       redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
       openapi_url=None if settings.ENVIRONMENT == "production" else "/openapi.json"
   )
   ```

2. **Minimal API İçin:**
   ```python
   # Sadece endpoint'ler, dokümantasyon yok
   app = FastAPI(
       docs_url=None,
       redoc_url=None,
       openapi_url=None
   )
   ```

3. **Custom Dokümantasyon İçin:**
   ```python
   # Kendi dokümantasyon sisteminiz varsa
   app = FastAPI(
       docs_url=None,
       redoc_url=None,
       # openapi_url="/custom-api-spec.json"  # Custom endpoint
   )
   ```

**Önerilen Yaklaşım:**
```python
# Development'ta açık, production'da kapalı
app = FastAPI(
    title=settings.APP_NAME,
    description="LangGraph tabanlı RAG Chatbot API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None
)
```

---

### 📊 Özet Tablo

| Özellik | URL | Ne İşe Yarar | Kim Kullanır |
|---------|-----|---------------|--------------|
| **Swagger UI** | `/docs` | İnteraktif API test arayüzü | Geliştiriciler, QA |
| **ReDoc** | `/redoc` | Temiz dokümantasyon görünümü | Dokümantasyon okuyucuları |
| **OpenAPI JSON** | `/openapi.json` | API schema (machine-readable) | Frontend, tools, CI/CD |

**Hepsi Birlikte:**
```
OpenAPI JSON (schema)
        │
        ├──→ Swagger UI okur → /docs (interaktif test)
        │
        └──→ ReDoc okur → /redoc (temiz dokümantasyon)
```

**Sonuç:** Üçü de aynı OpenAPI schema'yı kullanır, sadece farklı şekillerde gösterirler!

---

```python
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Hangi domain'lerden istek kabul edilsin
    allow_credentials=True,         # Cookie gönderilsin mi
    allow_methods=["*"],           # Hangi HTTP metodları (GET, POST, vs.)
    allow_headers=["*"],           # Hangi header'lar
)
```

**📝 Açıklama - CORS Nedir?**

Tarayıcılar güvenlik için farklı domain'lerden gelen istekleri engeller. CORS, bu kısıtlamayı gevşetir.

```
Frontend (localhost:3000)  →  Backend (localhost:8000)
         │                           │
         └── CORS izni gerekli ──────┘
```

> ⚠️ **Güvenlik Notu:** Production'da `allow_origins=["*"]` yerine spesifik domain'ler belirtin.

---

```python
# API Router'ı bağla
app.include_router(api_router, prefix="/api/v1")
```

**📝 Açıklama:**
Tüm API endpoint'lerimiz `/api/v1` prefix'i ile başlar:
- `/api/v1/auth/login`
- `/api/v1/chat`
- `/api/v1/chat/conversations`

---

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }
```

**📝 Açıklama - Health Check:**
Kubernetes, load balancer gibi sistemler bu endpoint'i kullanarak uygulamanın çalışıp çalışmadığını kontrol eder.

---

## 🔧 Core Modülü

Core modülü, uygulamanın temel yapı taşlarını içerir.

### config.py - Yapılandırma

```python
"""
Application Configuration

Tüm environment variable'lar ve ayarlar burada tanımlanır.
Pydantic Settings ile type-safe ve validated.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
```

**📝 Açıklama - Import'lar:**

| Import | Ne İşe Yarar |
|--------|--------------|
| `BaseSettings` | Ortam değişkenlerini okumak için Pydantic sınıfı |
| `SettingsConfigDict` | Settings yapılandırması |
| `lru_cache` | Fonksiyon sonucunu cache'lemek için |

---

```python
class Settings(BaseSettings):
    """
    Application settings.
    
    Değerler şu sırayla okunur:
    1. Environment variables
    2. .env dosyası
    3. Default değerler
    """
    
    # ===== APP SETTINGS =====
    APP_NAME: str = "RAG Chatbot"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
```

**📝 Açıklama - Settings Sınıfı:**

Pydantic Settings, ortam değişkenlerini otomatik olarak okur ve doğrular.

```python
# .env dosyasında:
APP_NAME=My App

# Veya terminal'de:
export APP_NAME="My App"

# Python'da otomatik okunur:
settings.APP_NAME  # → "My App"
```

**Type Annotation'lar:**
```python
APP_NAME: str = "RAG Chatbot"
#        │          │
#        │          └── Default değer (ortam değişkeni yoksa)
#        └── Beklenen tip (string)
```

---

```python
    # ===== DATABASE =====
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
```

**📝 Açıklama - Veritabanı Ayarları:**

| Ayar | Açıklama |
|------|----------|
| `DATABASE_URL` | Veritabanı bağlantı adresi (zorunlu, default yok) |
| `DB_POOL_SIZE` | Havuzda tutulacak bağlantı sayısı |
| `DB_MAX_OVERFLOW` | Taşma durumunda ek bağlantı sayısı |

**Connection Pool Nedir?**
```
Normal (yavaş):
Her istek → Yeni bağlantı aç → Sorgu → Bağlantı kapat

Pool ile (hızlı):
Her istek → Havuzdan bağlantı al → Sorgu → Havuza geri ver
```

---

```python
    # ===== AUTHENTICATION =====
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
```

**📝 Açıklama - Auth Ayarları:**

| Ayar | Açıklama |
|------|----------|
| `SECRET_KEY` | JWT token'ları imzalamak için gizli anahtar |
| `ALGORITHM` | Şifreleme algoritması (HS256 = HMAC-SHA256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token geçerlilik süresi |

> 🔒 **Güvenlik:** `SECRET_KEY` çok gizli tutulmalı ve tahmin edilemez olmalı!

---

```python
    # ===== OPENAI =====
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
```

**📝 Açıklama - OpenAI Ayarları:**

| Ayar | Açıklama |
|------|----------|
| `OPENAI_API_KEY` | OpenAI API anahtarı |
| `OPENAI_MODEL` | Kullanılacak model |
| `OPENAI_TEMPERATURE` | Yaratıcılık seviyesi (0=deterministik, 1=yaratıcı) |
| `OPENAI_MAX_TOKENS` | Maksimum yanıt uzunluğu |

**Temperature Nedir?**
```
temperature = 0.0 → Her zaman aynı yanıt (matematiksel sorular için)
temperature = 0.7 → Dengeli (genel kullanım)
temperature = 1.0 → Çok yaratıcı (hikaye yazımı için)
```

---

```python
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
```

**📝 Açıklama - Model Config:**

| Ayar | Açıklama |
|------|----------|
| `env_file` | .env dosyasının adı |
| `env_file_encoding` | Dosya kodlaması |
| `case_sensitive` | Büyük/küçük harf duyarlı |
| `extra="ignore"` | Bilinmeyen değişkenleri görmezden gel |

---

```python
    @property
    def is_production(self) -> bool:
        """Production environment check."""
        return self.ENVIRONMENT == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Sync database URL (Alembic için)."""
        return self.DATABASE_URL.replace("+asyncpg", "")
```

**📝 Açıklama - Property'ler:**

`@property` decorator'ı, bir metodu attribute gibi kullanmamızı sağlar:

```python
# Metod olarak çağırmak yerine:
settings.is_production()  # ❌

# Attribute gibi erişiriz:
settings.is_production  # ✅
```

---

```python
@lru_cache()
def get_settings() -> Settings:
    """Settings singleton."""
    return Settings()


settings = get_settings()
```

**📝 Açıklama - Singleton Pattern:**

`@lru_cache()` fonksiyonun sonucunu cache'ler, böylece Settings sadece bir kez oluşturulur:

```python
# lru_cache olmadan:
get_settings()  # Yeni Settings oluşturur
get_settings()  # Yeni Settings oluşturur (tekrar okur)

# lru_cache ile:
get_settings()  # Settings oluşturur ve cache'ler
get_settings()  # Cache'den döner (hızlı)
```

---

### security.py - Güvenlik

```python
"""
Security Utilities

JWT token yönetimi ve password hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings
```

**📝 Açıklama - Import'lar:**

| Import | Ne İşe Yarar |
|--------|--------------|
| `datetime, timedelta` | Zaman işlemleri |
| `jose.jwt` | JWT token oluşturma/okuma |
| `passlib.CryptContext` | Şifre hash'leme |

---

```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
```

**📝 Açıklama - Password Context:**

Bcrypt, şifreleri güvenli şekilde hash'lemek için kullanılan bir algoritma.

```
Kullanıcı şifresi: "password123"
                    │
                    ▼
Bcrypt hash:  "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X..."
```

**Neden hash'leme?**
- Veritabanı sızıntısında şifreler görülmez
- Şifreler geri döndürülemez (tek yönlü)
- Her hash farklıdır (salt kullanılır)

---

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Plain text password'ü hash ile karşılaştır."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Password'ü hash'le."""
    return pwd_context.hash(password)
```

**📝 Açıklama - Şifre Fonksiyonları:**

```python
# Kullanıcı kayıt olurken:
hashed = get_password_hash("password123")
# → "$2b$12$LQv3c1yqBWVHxkd0LHAkCO..."

# Kullanıcı giriş yaparken:
is_valid = verify_password("password123", hashed)
# → True
```

---

```python
def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None
) -> str:
    """JWT access token oluştur."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(subject),    # Subject (kullanıcı ID)
        "exp": expire,          # Expiration (son kullanma)
        "iat": datetime.now(timezone.utc),  # Issued at (oluşturulma)
        "type": "access"        # Token tipi
    }
    
    if extra_claims:
        to_encode.update(extra_claims)
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
```

**📝 Açıklama - Token Oluşturma:**

JWT Token'ın yapısı:
```
eyJhbGciOiJIUzI1NiIs.eyJzdWIiOiIxIiwiZXhwIjox.SflKxwRJSMeKKF2QT4fwpM
    │                    │                          │
    │                    │                          └── Signature (imza)
    │                    └── Payload (veri)
    └── Header (algoritma bilgisi)
```

Payload içeriği:
```json
{
    "sub": "1",                    // Kullanıcı ID
    "exp": 1733400000,             // Bitiş zamanı
    "iat": 1733398200,             // Oluşturma zamanı
    "type": "access"               // Token tipi
}
```

---

```python
def decode_access_token(token: str) -> Optional[dict]:
    """JWT token'ı decode et."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

**📝 Açıklama - Token Çözme:**

```python
# Başarılı decode:
payload = decode_access_token("eyJhbGc...")
# → {"sub": "1", "exp": 1733400000, ...}

# Geçersiz/süresi dolmuş token:
payload = decode_access_token("invalid_token")
# → None
```

---

### dependencies.py - Dependency Injection

```python
"""
FastAPI Dependencies

Dependency Injection pattern ile service ve resource yönetimi.
"""

from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_maker
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
```

---

```python
# HTTPBearer - Swagger UI'da direkt JWT token girişi sağlar
http_bearer = HTTPBearer(
    scheme_name="JWT Token",
    description="JWT token'ı buraya girin (ey... ile başlayan)"
)
```

**📝 Açıklama - HTTPBearer:**

Bu, Swagger UI'da direkt JWT token girişi sağlar:

```
┌─────────────────────────────────────────────────┐
│  Authorize                               🔓    │
├─────────────────────────────────────────────────┤
│  JWT Token (http, Bearer)                       │
│                                                 │
│  Value: [eyJhbGciOiJIUzI1NiIs...            ]  │
│                                                 │
│  [Authorize]  [Close]                          │
└─────────────────────────────────────────────────┘
```

Token header'a şöyle eklenir:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

```python
async def get_db() -> Generator[AsyncSession, None, None]:
    """Database session dependency."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**📝 Açıklama - Database Session:**

Bu fonksiyon her request için:
1. Yeni session açar
2. Session'ı `yield` ile verir
3. İşlem başarılı → `commit` (kaydet)
4. Hata olursa → `rollback` (geri al)
5. Her durumda → `close` (kapat)

```
Request başlangıcı      Request işleme       Request sonu
        │                    │                    │
        ▼                    ▼                    ▼
   Session aç     →    yield session    →   commit/rollback + close
```

---

```python
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Current authenticated user dependency."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Token'ı credentials'dan al
    token = credentials.credentials
    
    # 2. Token'ı decode et
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 3. User ID'yi al
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 4. Kullanıcıyı veritabanından getir
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
    
    # 5. Kullanıcı aktif mi kontrol et
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user
```

**📝 Açıklama - Kullanıcı Doğrulama Akışı:**

```
Token geldi: "eyJhbGc..."
         │
         ▼
┌─────────────────────┐
│ 1. Token decode et  │
│    payload al       │
└─────────┬───────────┘
          │ payload = {"sub": "1", ...}
          ▼
┌─────────────────────┐
│ 2. User ID'yi al    │
│    sub = "1"        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 3. DB'den user getir│
│    SELECT * FROM    │
│    users WHERE id=1 │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 4. Aktiflik kontrol │
│    is_active=True?  │
└─────────┬───────────┘
          │
          ▼
      User objesi
```

---

```python
# Type aliases for cleaner code
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

**📝 Açıklama - Type Alias'lar:**

Kod tekrarını azaltmak için alias'lar kullanırız:

```python
# Alias olmadan (uzun):
async def my_func(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)]
):
    ...

# Alias ile (kısa ve temiz):
async def my_func(db: DbSession, user: CurrentUser):
    ...
```

---

### exceptions.py - Özel Hatalar

```python
"""
Custom Exceptions

Uygulama genelinde kullanılan exception'lar.
"""

from typing import Any, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for all app exceptions."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )
```

**📝 Açıklama - Base Exception:**

Tüm özel exception'larımız bu sınıftan türer. `HTTPException`'ı extend eder.

---

```python
class NotFoundException(AppException):
    """Resource not found."""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{identifier}' not found"
        )
```

**📝 Açıklama - NotFoundException:**

```python
# Kullanımı:
raise NotFoundException("User", 123)
# → HTTP 404: "User with id '123' not found"

raise NotFoundException("Conversation", "abc-123")
# → HTTP 404: "Conversation with id 'abc-123' not found"
```

---

```python
class AlreadyExistsException(AppException):
    """Resource already exists."""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field} '{value}' already exists"
        )
```

**📝 Açıklama - AlreadyExistsException:**

```python
# Kullanımı:
raise AlreadyExistsException("User", "email", "test@example.com")
# → HTTP 409: "User with email 'test@example.com' already exists"
```

---

### redis.py - Redis Yönetimi

```python
"""
Redis Connection Manager

Redis bağlantısını ve LangGraph checkpointer'ını yönetir.
Mesaj geçmişi Redis'te saklanır (kalıcı).
"""

from typing import Optional, Union
import redis.asyncio as redis
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver

from app.core.config import settings


# Redis client singleton
_redis_client: Optional[redis.Redis] = None

# Checkpointer singleton
_checkpointer: Optional[Union[RedisSaver, MemorySaver]] = None
```

**📝 Açıklama - Singleton Pattern:**

Singleton, bir sınıftan sadece bir instance olmasını garantiler:

```python
_redis_client = None  # Global değişken
_checkpointer = None  # Global checkpointer

# İlk çağrıda oluştur, sonrakilerde aynısını döndür
```

---

```python
async def get_redis_client() -> redis.Redis:
    """Redis client singleton."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    return _redis_client
```

**📝 Açıklama - Redis Client:**

```python
# İlk çağrı: client oluşturulur
client = await get_redis_client()

# Sonraki çağrılar: aynı client döner
client = await get_redis_client()  # Yeni oluşturmaz
```

---

```python
def get_checkpointer_sync() -> Union[RedisSaver, MemorySaver]:
    """
    LangGraph checkpointer (sync version).
    
    RedisSaver kullanarak mesaj geçmişi Redis'te saklanır.
    Sunucu yeniden başlasa bile mesajlar kaybolmaz.
    """
    global _checkpointer
    
    if _checkpointer is None:
        try:
            _checkpointer = RedisSaver.from_conn_string(settings.REDIS_URL)
            print("✅ RedisSaver initialized - Messages will be stored in Redis")
        except Exception as e:
            print(f"⚠️ RedisSaver failed, falling back to MemorySaver: {e}")
            _checkpointer = MemorySaver()
    
    return _checkpointer
```

**📝 Açıklama - RedisSaver vs MemorySaver:**

```
┌─────────────────────────────────────────┐
│  RedisSaver (Şu an kullanılan)          │
│                                         │
│  ✅ Mesajlar Redis'te saklanır          │
│  ✅ Sunucu kapanınca kaybolmaz          │
│  ✅ Kalıcı (disk'e yazılır)             │
│  ✅ Birden fazla sunucuda çalışır       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  MemorySaver (Fallback)                 │
│                                         │
│  ⚠️ Mesajlar RAM'de saklanır            │
│  ❌ Sunucu kapanınca kaybolur           │
│  ❌ Sadece tek sunucuda çalışır         │
└─────────────────────────────────────────┘
```

**📝 Açıklama - Checkpointer:**

Checkpointer, LangGraph'ın konuşma geçmişini saklamasını sağlar:

```
Conversation 1: [Mesaj1, Mesaj2, Mesaj3]  ← thread_id="conv-1"
Conversation 2: [Mesaj1, Mesaj2]          ← thread_id="conv-2"
```

---

## 🗄 Database Modülü

### database.py

```python
"""
Database Configuration

SQLAlchemy async engine ve session factory.
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
```

---

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,           # SQL sorgularını logla
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,            # Bağlantı sağlıklı mı kontrol et
)
```

**📝 Açıklama - Engine:**

Engine, veritabanına bağlanmak için kullanılan ana nesnedir.

| Parametre | Açıklama |
|-----------|----------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:port/db` |
| `echo` | SQL sorgularını göster (debug için) |
| `pool_size` | Havuzdaki bağlantı sayısı |
| `max_overflow` | Taşma durumunda ek bağlantı |
| `pool_pre_ping` | Bağlantı öncesi sağlık kontrolü |

---

```python
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
```

**📝 Açıklama - Session Factory:**

Session, veritabanı işlemleri için kullanılır:

```python
async with async_session_maker() as session:
    # Sorgu yap
    result = await session.execute(query)
    
    # Kaydet
    await session.commit()
```

| Parametre | Açıklama |
|-----------|----------|
| `expire_on_commit=False` | Commit sonrası objeleri geçersiz kılma |
| `autocommit=False` | Otomatik commit yapma |
| `autoflush=False` | Otomatik flush yapma |

---

```python
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass
```

**📝 Açıklama - Base Model:**

Tüm model sınıflarımız bu sınıftan türer:

```python
class User(Base):       # Base'den türer
    __tablename__ = "users"
    ...

class Conversation(Base):  # Base'den türer
    __tablename__ = "conversations"
    ...
```

---

## 📊 Models Modülü

### user.py - User Model

```python
"""
User Model

SQLAlchemy ORM model for users table.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation
```

**📝 Açıklama - TYPE_CHECKING:**

Circular import sorununu çözmek için kullanılır:

```python
# Circular import problemi:
# user.py → conversation.py → user.py → ...

# TYPE_CHECKING çözümü:
if TYPE_CHECKING:
    from app.models.conversation import Conversation
# Bu import sadece type checker için, runtime'da çalışmaz
```

---

```python
class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
```

**📝 Açıklama - Tablo ve ID:**

| Özellik | Açıklama |
|---------|----------|
| `__tablename__` | SQL tablo adı |
| `Mapped[int]` | Python tipi |
| `primary_key=True` | Birincil anahtar |
| `index=True` | Index oluştur (hızlı arama için) |

---

```python
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
```

**📝 Açıklama - String Kolonlar:**

| Parametre | Açıklama |
|-----------|----------|
| `String(255)` | VARCHAR(255) |
| `unique=True` | Tekrar edemez |
| `nullable=False` | NULL olamaz |

---

```python
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
```

**📝 Açıklama - Opsiyonel Kolon:**

`Optional[str]` ve `nullable=True` birlikte kullanılır:
```python
Mapped[str]          → nullable=False (zorunlu)
Mapped[Optional[str]] → nullable=True (opsiyonel)
```

---

```python
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
```

**📝 Açıklama - Boolean Kolonlar:**

| Kolon | Default | Açıklama |
|-------|---------|----------|
| `is_active` | True | Kullanıcı aktif mi? |
| `is_superuser` | False | Admin mi? |

---

```python
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

**📝 Açıklama - Zaman Kolonları:**

| Parametre | Açıklama |
|-----------|----------|
| `DateTime(timezone=True)` | Timezone bilgisi ile |
| `server_default=func.now()` | DB'de NOW() fonksiyonu |
| `onupdate=func.now()` | Update'te otomatik güncelle |

---

```python
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
```

**📝 Açıklama - Relationship:**

User ve Conversation arasındaki ilişki:

```
User (1) ──────< Conversation (N)
  │                    │
  │                    ├── conv_1
  └── conversations ──┼── conv_2
                      └── conv_3
```

| Parametre | Açıklama |
|-----------|----------|
| `back_populates="user"` | Karşı taraftaki ilişki adı |
| `cascade="all, delete-orphan"` | User silinince conv'lar da silinir |

---

```python
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
```

**📝 Açıklama - __repr__:**

Debug için okunabilir string döndürür:
```python
user = User(id=1, email="test@example.com")
print(user)
# → <User(id=1, email='test@example.com')>
```

---

### conversation.py - Conversation Model

```python
class Conversation(Base):
    """Conversation metadata model."""
    
    __tablename__ = "conversations"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True
    )
```

**📝 Açıklama - UUID Primary Key:**

Integer yerine UUID kullanmanın avantajları:
- Tahmin edilemez (güvenlik)
- Dağıtık sistemlerde çakışma olmaz
- URL'de kullanılabilir

```
Integer ID: /conversations/1, /conversations/2  ← Tahmin edilebilir
UUID:       /conversations/abc-123-def-456      ← Tahmin edilemez
```

---

```python
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
```

**📝 Açıklama - Foreign Key:**

| Parametre | Açıklama |
|-----------|----------|
| `ForeignKey("users.id")` | users tablosunun id kolonuna referans |
| `ondelete="CASCADE"` | User silinince conv'lar da silinir |
| `index=True` | User'a göre arama hızlandırılır |

---

## 📋 Schemas Modülü

Pydantic şemaları, API request/response validasyonu için kullanılır.

### user.py

```python
"""
User Schemas

Pydantic models for user API validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
```

**📝 Açıklama - Request Schema:**

| Field | Tip | Validation |
|-------|-----|------------|
| `email` | EmailStr | Geçerli email formatı |
| `password` | str | Minimum 8 karakter |
| `full_name` | Optional[str] | Opsiyonel |

**`Field(...)` Nedir?**
```python
password: str = Field(..., min_length=8)
#               │      │      │
#               │      │      └── Minimum 8 karakter
#               │      └── ... = zorunlu alan
#               └── Field ile validasyon ekle
```

---

```python
class UserOut(BaseModel):
    """User response schema."""
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**📝 Açıklama - Response Schema:**

`from_attributes = True`, ORM modelini Pydantic modeline dönüştürür:

```python
# SQLAlchemy User objesi
user = User(id=1, email="test@example.com", ...)

# Pydantic UserOut'a dönüşüm
UserOut.model_validate(user)
# → UserOut(id=1, email="test@example.com", ...)
```

---

### chat.py

```python
class ChatMessageRequest(BaseModel):
    """Chat mesajı gönderme request'i."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message content"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID. If null, creates new conversation."
    )
```

**📝 Açıklama - Chat Request:**

| Field | Validation | Açıklama |
|-------|------------|----------|
| `message` | 1-10000 karakter | Kullanıcı mesajı |
| `conversation_id` | Opsiyonel | Null ise yeni conv başlar |

---

```python
class MessageSchema(BaseModel):
    """Tek bir mesajı temsil eder."""
    role: Literal["human", "assistant"] = Field(
        ...,
        description="Message sender role"
    )
    content: str = Field(
        ...,
        description="Message content"
    )
    timestamp: datetime = Field(
        ...,
        description="Message timestamp"
    )
```

**📝 Açıklama - Literal Type:**

`Literal` sadece belirli değerlere izin verir:
```python
role: Literal["human", "assistant"]

role = "human"      # ✅ Geçerli
role = "assistant"  # ✅ Geçerli
role = "bot"        # ❌ Hata!
```

---

## 📁 Repositories Modülü

### base.py - Generic Repository

```python
"""
Base Repository

Generic CRUD operations for repositories.
"""

from typing import TypeVar, Generic, Optional, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)
```

**📝 Açıklama - TypeVar ve Generic:**

TypeVar, generic tip oluşturur:
```python
ModelType = TypeVar("ModelType", bound=Base)
# ModelType, Base'den türeyen herhangi bir tip olabilir
# User, Conversation, Product, vs.
```

---

```python
class BaseRepository(Generic[ModelType]):
    """Generic base repository with CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model
```

**📝 Açıklama - Generic Class:**

```python
# BaseRepository[User] → ModelType = User
# BaseRepository[Conversation] → ModelType = Conversation

class UserRepository(BaseRepository[User]):
    pass

class ConversationRepository(BaseRepository[Conversation]):
    pass
```

---

```python
    async def get_by_id(self, id: int | str) -> Optional[ModelType]:
        """Get record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
```

**📝 Açıklama - SELECT Sorgusu:**

```python
# Python kodu:
select(User).where(User.id == 1)

# SQL karşılığı:
# SELECT * FROM users WHERE id = 1
```

`scalar_one_or_none()`:
- Kayıt varsa → Kayıt döner
- Kayıt yoksa → None döner
- Birden fazla → Hata fırlatır

---

```python
    async def create(self, obj: ModelType) -> ModelType:
        """Create new record."""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
```

**📝 Açıklama - CREATE İşlemi:**

```python
# 1. add(): Session'a ekle (henüz DB'ye gitmedi)
self.db.add(user)

# 2. flush(): DB'ye gönder (henüz commit değil)
await self.db.flush()

# 3. refresh(): ID gibi otomatik değerleri al
await self.db.refresh(user)
# Artık user.id doldu
```

---

### user_repository.py

```python
class UserRepository(BaseRepository[User]):
    """User database operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
```

**📝 Açıklama - Repository Kullanımı:**

```python
# Repository oluştur
user_repo = UserRepository(db)

# CRUD işlemleri
user = await user_repo.get_by_id(1)
user = await user_repo.get_by_email("test@example.com")
exists = await user_repo.exists_by_email("test@example.com")
```

---

```python
    async def get_by_email(self, email: str) -> Optional[User]:
        """Email ile user getir."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

**📝 Açıklama:**
```sql
-- SQL karşılığı:
SELECT * FROM users WHERE email = 'test@example.com'
```

---

## ⚙️ Services Modülü

### chat_service.py

Service katmanı, business logic'i içerir.

```python
"""
Chat Service

Chat ile ilgili tüm business logic burada.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.agents.state import AgentState
from app.agents.graph import get_compiled_graph
from app.schemas.chat import (
    ChatMessageResponse,
    ConversationSchema,
    MessageSchema
)
from app.core.exceptions import NotFoundException
```

---

```python
class ChatService:
    """Chat service layer."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.graph = get_compiled_graph(with_memory=True)
        self.conversation_repo = ConversationRepository(db)
```

**📝 Açıklama - Service Yapısı:**

```
ChatService
    │
    ├── db                 → Database session
    ├── graph              → LangGraph compiled graph
    └── conversation_repo  → Conversation CRUD işlemleri
```

---

```python
    async def send_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None
    ) -> ChatMessageResponse:
        """Mesaj gönder ve cevap al."""
        
        # Conversation al veya oluştur
        if conversation_id:
            conversation = await self._get_conversation(
                conversation_id, user_id
            )
        else:
            conversation = await self._create_conversation(user_id)
```

**📝 Açıklama - Mesaj Gönderme (1/4):**

İlk adım, conversation'ı belirlemek:

```
conversation_id var mı?
        │
        ├── Evet → Mevcut conversation'ı getir
        │          (sahiplik kontrolü ile)
        │
        └── Hayır → Yeni conversation oluştur
```

---

```python
        # Initial state hazırla
        initial_state = AgentState(
            messages=[],
            user_id=str(user_id),
            thread_id=conversation.id,
            last_question=message,
            last_answer="",
            context=None,
            error=None
        )
```

**📝 Açıklama - Mesaj Gönderme (2/4):**

LangGraph için başlangıç state'i:

| Field | Değer | Açıklama |
|-------|-------|----------|
| `messages` | `[]` | Geçmiş mesajlar (graph dolduracak) |
| `user_id` | "1" | Kullanıcı ID |
| `thread_id` | "conv-uuid" | Konuşma ID |
| `last_question` | "Merhaba" | Kullanıcı mesajı |
| `last_answer` | "" | AI yanıtı (graph dolduracak) |

---

```python
        # Config: thread_id ile state izole edilir
        config = {
            "configurable": {
                "thread_id": conversation.id
            }
        }
        
        # Graph invoke et
        result = self.graph.invoke(initial_state, config)
```

**📝 Açıklama - Mesaj Gönderme (3/4):**

`thread_id` her konuşmayı izole eder:

```
thread_id="conv-1" → [Mesaj1, Mesaj2, Mesaj3]
thread_id="conv-2" → [Mesaj1, Mesaj2]
thread_id="conv-3" → [Mesaj1]
```

---

```python
        # Conversation metadata güncelle
        await self._update_conversation_timestamp(conversation)
        
        # İlk mesajdan title oluştur
        if not conversation.title:
            conversation.title = message[:50] + ("..." if len(message) > 50 else "")
            await self.conversation_repo.update(conversation)
        
        return ChatMessageResponse(
            response=result["last_answer"],
            conversation_id=conversation.id
        )
```

**📝 Açıklama - Mesaj Gönderme (4/4):**

Son adımlar:
1. `last_message_at` timestamp'i güncelle
2. Başlık yoksa ilk mesajdan oluştur (max 50 karakter)
3. Response döndür

---

## 🤖 Agents Modülü (LangGraph)

Bu modül, AI sohbet akışını yönetir.

### state.py - Agent State

```python
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
```

**📝 Açıklama - add_messages Reducer:**

`add_messages` özel bir reducer'dır. Mesajları üzerine yazmak yerine ekler:

```python
# Normal davranış (üzerine yazar):
state["messages"] = [msg1]
state["messages"] = [msg2]
# Sonuç: [msg2]

# add_messages reducer (ekler):
state["messages"] = [msg1]
state["messages"] = [msg2]
# Sonuç: [msg1, msg2]
```

---

```python
    # Identifiers
    user_id: str
    thread_id: str
    
    # Current turn data
    last_question: str
    last_answer: str
    
    # Optional fields
    context: Optional[str]  # RAG retrieved context
    error: Optional[str]    # Error message
```

**📝 Açıklama - State Alanları:**

```
AgentState
    │
    ├── messages[]      → Tüm mesaj geçmişi
    │
    ├── user_id        → Kullanıcı kimliği
    ├── thread_id      → Konuşma kimliği
    │
    ├── last_question  → Son kullanıcı sorusu
    ├── last_answer    → Son AI yanıtı
    │
    ├── context        → RAG'dan gelen context (opsiyonel)
    └── error          → Hata mesajı (opsiyonel)
```

---

### nodes.py - Graph Node'ları

```python
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
```

**📝 Açıklama - Lazy Initialization:**

LLM sadece ilk kullanımda oluşturulur (bellek tasarrufu):

```python
# Uygulama başlangıcında:
_llm = None  # Henüz oluşturulmadı

# İlk mesajda:
llm = get_llm()  # Şimdi oluşturuldu

# Sonraki mesajlarda:
llm = get_llm()  # Aynı instance döner
```

---

```python
def add_user_message(state: AgentState) -> dict:
    """Kullanıcı mesajını state'e ekle."""
    user_message = HumanMessage(content=state["last_question"])
    return {
        "messages": [user_message]
    }
```

**📝 Açıklama - Node 1: add_user_message:**

Bu node, kullanıcı mesajını state'e ekler:

```
Giriş State:
{
    last_question: "Python nedir?",
    messages: []
}

Çıkış:
{
    messages: [HumanMessage("Python nedir?")]
}
```

---

```python
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
```

**📝 Açıklama - Node 2: generate_response:**

Bu node, OpenAI API'yi çağırır:

```
Mesajlar LLM'e gönderilir:
┌─────────────────────────────────────────┐
│ 1. SystemMessage (prompt)               │
│    "You are a helpful AI assistant..."  │
├─────────────────────────────────────────┤
│ 2. Context (opsiyonel, RAG için)        │
│    "Relevant context: ..."              │
├─────────────────────────────────────────┤
│ 3. Mesaj geçmişi                        │
│    HumanMessage("Merhaba")              │
│    AIMessage("Merhaba! Nasıl...")       │
│    HumanMessage("Python nedir?")        │
└─────────────────────────────────────────┘
                    │
                    ▼
              OpenAI API
                    │
                    ▼
        AIMessage("Python, yüksek...")
```

---

```python
def add_ai_message(state: AgentState) -> dict:
    """AI cevabını state'e ekle."""
    ai_message = AIMessage(content=state["last_answer"])
    return {
        "messages": [ai_message]
    }
```

**📝 Açıklama - Node 3: add_ai_message:**

AI yanıtını mesaj geçmişine ekler:

```
Giriş:
{
    last_answer: "Python, yüksek seviyeli...",
    messages: [HumanMessage("Python nedir?")]
}

Çıkış:
{
    messages: [AIMessage("Python, yüksek seviyeli...")]
}
# add_messages reducer ile birleşir:
# messages: [HumanMessage(...), AIMessage(...)]
```

---

### graph.py - Graph Tanımı

```python
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
from app.core.redis import get_checkpointer
```

---

```python
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
```

**📝 Açıklama - Graph Yapısı:**

```
                     START
                       │
                       ▼
            ┌──────────────────┐
            │ add_user_message │  ← Node 1: Kullanıcı mesajını ekle
            └────────┬─────────┘
                     │ Edge
                     ▼
            ┌──────────────────┐
            │ generate_response│  ← Node 2: OpenAI'dan yanıt al
            └────────┬─────────┘
                     │ Edge
                     ▼
            ┌──────────────────┐
            │  add_ai_message  │  ← Node 3: AI yanıtını ekle
            └────────┬─────────┘
                     │ Edge
                     ▼
                    END
```

**Graph Bileşenleri:**

| Bileşen | Açıklama |
|---------|----------|
| `Node` | Bir işlem adımı (fonksiyon) |
| `Edge` | Node'lar arası bağlantı |
| `Entry Point` | Graph'ın başlangıç noktası |
| `END` | Graph'ın bitiş noktası |

---

```python
def compile_graph(
    graph: StateGraph,
    checkpointer: Optional[any] = None
) -> CompiledGraph:
    """Graph'ı compile et."""
    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()
```

**📝 Açıklama - Compile:**

Compile, graph'ı çalıştırılabilir hale getirir:

```python
# Build: Graph yapısını tanımla
graph = build_graph()

# Compile: Çalıştırılabilir hale getir
compiled = graph.compile(checkpointer=checkpointer)

# Invoke: Çalıştır
result = compiled.invoke(state, config)
```

---

```python
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
            checkpointer = get_checkpointer()
            _compiled_graph = compile_graph(graph, checkpointer)
        else:
            _compiled_graph = compile_graph(graph)
    
    return _compiled_graph
```

**📝 Açıklama - Singleton Graph:**

Graph bir kez oluşturulur ve tekrar kullanılır:

```python
# İlk çağrı: Graph oluşturulur
graph = get_compiled_graph()

# Sonraki çağrılar: Aynı graph döner
graph = get_compiled_graph()  # Yeniden oluşturmaz
```

---

### prompts.py - System Prompt'ları

```python
"""
Agent Prompts

System prompts ve template'ler.
"""

SYSTEM_PROMPT = """You are a helpful AI assistant. Your goal is to provide accurate, 
helpful, and friendly responses to user questions.

Guidelines:
1. Be concise but thorough
2. If you don't know something, say so honestly
3. Provide examples when helpful
4. Format responses with markdown when appropriate
5. Be respectful and professional

Current conversation context:
- You are chatting with a user through a web interface
- Keep responses focused and relevant
- Ask clarifying questions if needed
"""
```

**📝 Açıklama - System Prompt:**

System prompt, AI'ın davranışını belirler:

```
System Prompt (gizli talimatlar)
        │
        ▼
┌───────────────────────────────┐
│ "Sen yardımcı bir asistansın" │
│ "Kısa ve öz ol"               │
│ "Bilmiyorsan söyle"           │
└───────────────────────────────┘
        │
        ▼
    AI Yanıtı
```

---

## 🌐 API Modülü

### router.py - Ana Router

```python
"""
Main API Router

Tüm route'ları birleştirir.
"""

from fastapi import APIRouter

from app.api.routes import auth, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
```

**📝 Açıklama - Router Yapısı:**

```
/api/v1
    │
    ├── /auth (auth.router)
    │   ├── POST /signup
    │   ├── POST /login
    │   └── GET  /me
    │
    └── /chat (chat.router)
        ├── POST /
        ├── GET  /conversations
        ├── GET  /conversations/{id}
        └── DELETE /conversations/{id}
```

---

### routes/auth.py - Auth Endpoint'leri

```python
"""
Authentication Routes

Auth ile ilgili HTTP endpoint'leri.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.core.exceptions import AlreadyExistsException, UnauthorizedException


router = APIRouter()
```

---

```python
@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account"
)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserOut:
    """Yeni kullanıcı kaydı."""
    user_repo = UserRepository(db)
    
    # Email kontrolü
    if await user_repo.exists_by_email(user_data.email):
        raise AlreadyExistsException("User", "email", user_data.email)
    
    # Yeni kullanıcı oluştur
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    
    created_user = await user_repo.create(new_user)
    return created_user
```

**📝 Açıklama - Signup Endpoint:**

```
POST /api/v1/auth/signup

Request:
{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
}

İşlem Akışı:
1. Email var mı kontrol et → Varsa 409 hatası
2. Şifreyi hash'le
3. User oluştur
4. Kaydet ve döndür

Response (201):
{
    "id": 1,
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": true,
    "created_at": "2025-12-05T10:00:00Z"
}
```

---

```python
@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Login and get access token"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Giriş yap ve token al."""
    user_repo = UserRepository(db)
    
    # Kullanıcıyı bul
    user = await user_repo.get_by_email(form_data.username)
    
    # Şifre kontrolü
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedException("Incorrect email or password")
    
    if not user.is_active:
        raise UnauthorizedException("Inactive user")
    
    # Token üret - user.id kullan (email değil)
    access_token = create_access_token(subject=user.id)
    
    return Token(access_token=access_token, token_type="bearer")
```

**📝 Açıklama - Login Endpoint:**

```
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=test@example.com&password=password123

İşlem Akışı:
1. Email ile kullanıcıyı bul
2. Şifreyi doğrula
3. Aktiflik kontrolü
4. JWT token oluştur

Response (200):
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Neden OAuth2PasswordRequestForm?**
```python
# Normal JSON body yerine form data kullanılır
# Swagger UI'daki "Authorize" butonu ile uyumlu
form_data: OAuth2PasswordRequestForm = Depends()
# → username ve password alanları otomatik okunur
```

---

### routes/chat.py - Chat Endpoint'leri

```python
"""
Chat API Routes

Chat ile ilgili HTTP endpoint'leri.
"""

from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    ConversationListResponse,
    MessageSchema
)


router = APIRouter()


# Type aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_chat_service(db: DbSession) -> ChatService:
    """ChatService dependency."""
    return ChatService(db=db)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
```

**📝 Açıklama - Dependency Chain:**

```
Request geldi (Authorization header ile)
        │
        ▼
┌─────────────────────────────┐
│ get_current_user            │ → Token'dan user al
└───────────────┬─────────────┘
                │
                ▼
┌─────────────────────────────┐
│ get_db                      │ → Database session al
└───────────────┬─────────────┘
                │
                ▼
┌─────────────────────────────┐
│ get_chat_service            │ → ChatService oluştur
└───────────────┬─────────────┘
                │
                ▼
        Endpoint çalışır
```

---

```python
@router.post(
    "",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Send a message and receive AI response"
)
async def send_message(
    request: ChatMessageRequest,
    current_user: CurrentUser,
    chat_service: ChatServiceDep
) -> ChatMessageResponse:
    """Mesaj gönder ve cevap al."""
    return await chat_service.send_message(
        user_id=current_user.id,
        message=request.message,
        conversation_id=request.conversation_id
    )
```

**📝 Açıklama - Send Message Endpoint:**

```
POST /api/v1/chat
Authorization: Bearer <token>

Request:
{
    "message": "Python nedir?",
    "conversation_id": null  // veya mevcut conv ID
}

Response:
{
    "response": "Python, yüksek seviyeli bir programlama dilidir...",
    "conversation_id": "abc-123-def-456"
}
```

---

## 🐳 Docker Dosyaları

### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# C tabanlı kütüphaneler (asyncpg, crypto) için gerekli araçlar
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Güvenlik için root olmayan kullanıcı oluştur
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**📝 Açıklama - Dockerfile Satır Satır:**

| Satır | Açıklama |
|-------|----------|
| `FROM python:3.13-slim` | Base image (küçük Python) |
| `WORKDIR /app` | Çalışma dizini |
| `RUN apt-get...` | Sistem bağımlılıkları |
| `COPY requirements.txt .` | Önce requirements kopyala |
| `RUN pip install...` | Python paketleri kur |
| `COPY . .` | Tüm kodu kopyala |
| `RUN useradd...` | Güvenlik için yeni kullanıcı |
| `USER appuser` | O kullanıcıya geç |
| `CMD [...]` | Başlangıç komutu |

**Neden bu sıra?**
```
Docker layer cache sayesinde:
1. requirements.txt değişmediyse pip install tekrar çalışmaz
2. Sadece kod değiştiğinde hızlı build
```

---

### docker-compose.yml

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=sifre123
      - POSTGRES_DB=rag_chatbot
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:sifre123@db:5432/rag_chatbot
      - SECRET_KEY=SECRET_KEY
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgres_data:
  redis_data:
```

**📝 Açıklama - Docker Compose:**

```
┌─────────────────────────────────────────────────────┐
│              Docker Network                          │
│                                                     │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│  │   db    │   │  redis  │   │   web   │          │
│  │ (5432)  │◄──│ (6379)  │◄──│ (8000)  │          │
│  └─────────┘   └─────────┘   └─────────┘          │
│       │             │             │                │
└───────┼─────────────┼─────────────┼────────────────┘
        │             │             │
        ▼             ▼             ▼
   localhost:5432 localhost:6379 localhost:8000
```

| Servis | Port | Açıklama |
|--------|------|----------|
| `db` | 5432 | PostgreSQL veritabanı |
| `redis` | 6379 | Redis (mesaj geçmişi) |
| `web` | 8000 | FastAPI uygulaması |

**Redis komut satırı açıklaması:**
```yaml
command: redis-server --appendonly yes
```
`--appendonly yes` parametresi, Redis'in verilerini diske yazmasını sağlar. Bu sayede Redis yeniden başlasa bile mesaj geçmişi kaybolmaz.

**depends_on ile healthcheck:**
```yaml
depends_on:
  db:
    condition: service_healthy
  redis:
    condition: service_healthy
```
Web servisi, hem db'nin hem de redis'in "healthy" olmasını bekler.

---

## 🎯 Özet

### Katmanlı Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
│                    (Frontend/Postman)                        │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP Request
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER                               │
│                    (routes/*.py)                             │
│                                                              │
│  • HTTP endpoint'leri tanımlar                               │
│  • Request validation (Pydantic)                             │
│  • Response serialization                                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                             │
│                   (services/*.py)                            │
│                                                              │
│  • Business logic                                            │
│  • LangGraph orchestration                                   │
│  • Transaction management                                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  REPOSITORY LAYER                            │
│                 (repositories/*.py)                          │
│                                                              │
│  • Database CRUD işlemleri                                   │
│  • Query building                                            │
│  • Data access abstraction                                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                               │
│                   (models/*.py)                              │
│                                                              │
│  • SQLAlchemy ORM modelleri                                  │
│  • Table definitions                                         │
│  • Relationships                                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE                                │
│                     (PostgreSQL)                             │
└─────────────────────────────────────────────────────────────┘
```

### Öğrenilmesi Gereken Ana Konseptler

| Konsept | Dosya | Açıklama |
|---------|-------|----------|
| FastAPI Basics | `main.py` | App oluşturma, middleware, router |
| Pydantic | `schemas/*.py` | Validation ve serialization |
| SQLAlchemy | `models/*.py`, `db/` | ORM ve async database |
| JWT Auth | `core/security.py` | Token based authentication |
| Dependency Injection | `core/dependencies.py` | DI pattern |
| Repository Pattern | `repositories/*.py` | Data access layer |
| Service Layer | `services/*.py` | Business logic |
| LangGraph | `agents/*.py` | AI workflow |
| Docker | `Dockerfile`, `docker-compose.yml` | Containerization |

---

## 📚 Önerilen Öğrenme Sırası

1. **Temel Python** - async/await, type hints, decorators
2. **FastAPI** - Endpoints, dependencies, middleware
3. **Pydantic** - Validation, serialization
4. **SQLAlchemy** - ORM, relationships, async
5. **JWT** - Authentication flow
6. **Design Patterns** - Repository, Service, Singleton
7. **LangGraph** - State management, nodes, edges
8. **Docker** - Images, containers, compose

---

**Bu rehber, projeyi adım adım anlamanızı sağlamak için hazırlanmıştır. Her bölümü dikkatlice okuyun ve kodu çalıştırarak deneyim kazanın!**

