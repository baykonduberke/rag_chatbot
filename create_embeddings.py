"""
Yorumları embedding'e çevirip Redis Vector Store'a kaydet.

Kullanım:
    python create_embeddings.py
"""

import asyncio
from sqlalchemy import select, text

from app.db.database import async_session_maker
from app.models.comment import Comment
from app.services.vector_store import (
    create_index,
    add_comment_embedding,
    get_embedding_count
)


async def load_all_comments():
    """Tüm yorumları veritabanından çek ve embedding'e çevir."""
    
    print("="*50)
    print("📥 Embedding Oluşturma Scripti")
    print("="*50)
    
    # Index oluştur
    print("\n🔧 Redis Vector Index oluşturuluyor...")
    await create_index()
    
    # Mevcut embedding sayısını kontrol et
    existing_count = await get_embedding_count()
    print(f"📊 Mevcut embedding sayısı: {existing_count}")
    
    if existing_count > 0:
        resp = input(f"⚠️ {existing_count} embedding var. Tekrar oluşturmak istiyor musunuz? (e/h): ")
        if resp.lower() != "e":
            print("İptal.")
            return
    
    # Yorumları çek
    print("\n📖 Yorumlar yükleniyor...")
    async with async_session_maker() as session:
        result = await session.execute(select(Comment))
        comments = list(result.scalars().all())
    
    print(f"📊 Toplam yorum: {len(comments)}")
    
    # Embedding oluştur
    print("\n🔄 Embedding'ler oluşturuluyor...")
    success_count = 0
    error_count = 0
    
    for i, comment in enumerate(comments, 1):
        try:
            await add_comment_embedding(
                comment_id=comment.id,
                content=comment.content,
                company=comment.company,
                category=comment.category,
                product_category=comment.product_category,
                sentiment_result=comment.sentiment_result.value
            )
            success_count += 1
            
            if success_count % 50 == 0:
                print(f"✅ {success_count}/{len(comments)} embedding oluşturuldu...")
                
        except Exception as e:
            print(f"❌ Yorum {comment.id} hatası: {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Başarılı: {success_count}")
    print(f"❌ Hatalı: {error_count}")
    
    # Son durumu göster
    final_count = await get_embedding_count()
    print(f"📊 Toplam embedding: {final_count}")


if __name__ == "__main__":
    asyncio.run(load_all_comments())

