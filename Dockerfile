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

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]