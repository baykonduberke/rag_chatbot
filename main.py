"""
FastAPI Application Entry Point

Bu dosya:
1. FastAPI app instance'ı oluşturur
2. Middleware'leri ekler
3. Router'ları bağlar
4. Startup/shutdown event'lerini yönetir
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.redis import close_redis
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle yönetimi."""
    # ===== STARTUP =====
    print("🚀 Application starting...")
    
    # Database tablolarını oluştur (yoksa)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables ready")
    
    yield
    
    # ===== SHUTDOWN =====
    print("👋 Application shutting down...")
    await close_redis()
    print("✅ Redis connection closed")
    await engine.dispose()
    print("✅ Cleanup completed")


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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router'ı bağla
app.include_router(api_router, prefix="/api/v1")


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
