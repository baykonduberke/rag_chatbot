"""
Excel'den yorumları veritabanına yükle.

Kullanım:
    python load_comments.py
"""

import asyncio
import pandas as pd
from sqlalchemy import text

from app.db.database import async_session_maker
from app.models.comment import Comment, SentimentType


# Excel dosyası yolu
EXCEL_FILE = "comments_test.xlsx"


def map_sentiment(value: str) -> SentimentType:
    """Sentiment değerini enum'a çevir."""
    value = str(value).strip().lower()
    
    positive_values = ["olumlu", "positive", "pozitif", "1", "pos"]
    negative_values = ["olumsuz", "negative", "negatif", "0", "neg"]
    
    if value in positive_values:
        return SentimentType.POSITIVE
    elif value in negative_values:
        return SentimentType.NEGATIVE
    else:
        print(f"⚠️  Bilinmeyen sentiment: '{value}' -> POSITIVE")
        return SentimentType.POSITIVE


async def load_comments():
    """Excel'den yorumları yükle."""
    
    print(f"📖 Excel okunuyor: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    
    print(f"📋 Kolonlar: {list(df.columns)}")
    print(f"📊 Toplam satır: {len(df)}")
    print(f"\n🔍 İlk 3 satır:\n{df.head(3)}\n")
    
    async with async_session_maker() as session:
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Excel kolonları:
                # 'Firma/Marka', 'Ürün Kategorisi', 'Kategori', 'Sentiment', 'Yorum Metni'
                content = str(row.get("Yorum Metni", "")).strip()
                company = str(row.get("Firma/Marka", "")).strip()
                category = str(row.get("Kategori", "")).strip()
                product_category = str(row.get("Ürün Kategorisi", "")).strip()
                sentiment = str(row.get("Sentiment", "")).strip()
                
                # Boş content atla
                if not content or content == "nan":
                    error_count += 1
                    continue
                
                # Varsayılan değerler
                if not company or company == "nan":
                    company = "Bilinmeyen"
                if not category or category == "nan":
                    category = "Genel"
                if not product_category or product_category == "nan":
                    product_category = "Genel"
                if not sentiment or sentiment == "nan":
                    sentiment = "Olumlu"
                
                comment = Comment(
                    content=content,
                    company=company,
                    category=category,
                    product_category=product_category,
                    sentiment_result=map_sentiment(sentiment)
                )
                
                session.add(comment)
                success_count += 1
                
                if success_count % 50 == 0:
                    await session.commit()
                    print(f"✅ {success_count} yorum eklendi...")
                    
            except Exception as e:
                print(f"❌ Satır {idx + 1}: {e}")
                await session.rollback()
                error_count += 1
        
        await session.commit()
        
        print(f"\n{'='*40}")
        print(f"✅ Başarılı: {success_count}")
        print(f"❌ Hatalı: {error_count}")


async def check_count():
    """Mevcut yorum sayısı."""
    async with async_session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM comments"))
        count = result.scalar()
        print(f"📊 Veritabanındaki yorum: {count}")
        return count


async def main():
    print("="*40)
    print("📥 Yorum Yükleme Scripti")
    print("="*40)
    
    existing = await check_count()
    
    if existing > 0:
        resp = input(f"⚠️  {existing} yorum var. Devam? (e/h): ")
        if resp.lower() != "e":
            print("İptal.")
            return
    
    await load_comments()
    await check_count()


if __name__ == "__main__":
    asyncio.run(main())
