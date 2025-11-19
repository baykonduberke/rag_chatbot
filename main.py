from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import engine, Base  
from app.api import auth

# Uygulama başlarken tabloları otomatik oluştur
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan, title="My Professional FastAPI Project")

# Router'ı dahil et
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Sistem Calisiyor! (Root main.py)"}