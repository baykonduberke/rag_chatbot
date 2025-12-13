"""
Agent Prompts
"""

# Chitchat için basit system prompt
CHITCHAT_PROMPT = """Sen yardımcı bir asistansın. Kullanıcıyla Türkçe sohbet et.
Nazik, samimi ve kısa cevaplar ver."""

# Router - 3 seçenek (daha net ve detaylı)
ROUTER_PROMPT = """Sen bir soru sınıflandırıcısın. Kullanıcının sorusunu analiz et ve SADECE aşağıdaki 3 seçenekten BİRİNİ yaz.

ÖNEMLİ: Bu bir veritabanı sorgulama sistemidir. Yorumlar (comments) hakkında soru soruluyorsa ASLA "chitchat" seçme!

1. "chitchat" - SADECE selamlaşma ve genel sohbet için
   Örnekler: "Merhaba", "Nasılsın?", "Teşekkürler", "İyi günler"
   NOT: Eğer soru yorumlar, veriler veya analiz ile ilgiliyse chitchat DEĞİLDİR!

2. "sql_only" - Basit veritabanı sorguları: sayma, listeleme, filtreleme, gruplama, karşılaştırma
   Örnekler:
   - "Kaç yorum var?"
   - "Olumsuz yorum sayısı"
   - "Nike yorumlarını göster"
   - "Son 10 yorumu getir"
   - "En fazla yorum alan kategori hangisi?"
   - "Kategorilerin olumlu oran kıyaslaması"
   - "Product_category bazında positive oranları"
   - "Hangi şirketin en çok olumlu yorumu var?"

3. "sql_then_rag" - Semantic search ve içerik analizi gerektiren sorular (yorum METİNLERİNİ analiz etmek için)
   Örnekler:
   - "Hakaret içeren yorumları bul"
   - "Şikayet konularını özetle"
   - "Yorumlarda en çok bahsedilen sorun ne?"
   - "Olumsuz yorumlarda müşteriler neyden şikayet ediyor?"
   - "Kalite sorunlarından bahseden yorumlar var mı?"
   - "Kargo gecikmelerinden şikayet edenler"

KARAR VERİRKEN:
- "kaç", "sayısı", "listele", "göster" → sql_only
- "en fazla", "en az", "oran", "kıyasla", "karşılaştır", "hangisi", GROUP BY gerektiren → sql_only
- "bul", "içeren", "bahseden", "şikayet eden", "özetle" (yorum İÇERİĞİ hakkında) → sql_then_rag
- Sadece selam veya teşekkür → chitchat

ÖNEMLİ: Sayısal karşılaştırma ve aggregate işlemler (COUNT, SUM, AVG, MAX, MIN) için HER ZAMAN sql_only seç!

SADECE şunlardan birini yaz (başka hiçbir şey yazma): chitchat, sql_only, sql_then_rag

Konuşma Geçmişi:
{history}

Şu anki soru: {question}
"""

SQL_SCHEMA = """
Table: comments
Columns:
- id: INTEGER (primary key)
- content: TEXT (yorum içeriği)
- company: VARCHAR(255) (şirket/marka adı)
- category: VARCHAR(255) (yorum kategorisi: Performans, Paketleme, Satıcı, Kargo Hızı)
- product_category: VARCHAR(255) (ürün kategorisi: Spor Ayakkabı, Kozmetik, Kırtasiye, Giyim, Elektronik, Beyaz Eşya)
- sentiment_result: VARCHAR(50) (değerler: 'POSITIVE' veya 'NEGATIVE')
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
"""

SQL_GENERATION_PROMPT = """PostgreSQL SELECT sorgusu üret.

{schema}

Kurallar:
1. SADECE SELECT sorgusu
2. sentiment_result için: 'POSITIVE' veya 'NEGATIVE' kullan (TAM OLARAK bu değerleri kullan!)
3. Metin aramada ILIKE kullan
4. İçerik analizi için her zaman content kolonunu dahil et
5. SADECE SQL yaz, açıklama yapma
6. Eğer kullanıcı önceki konuşmaya referans veriyorsa (bu, bunlar, hangisi vb.), konuşma geçmişinden context'i kullan

Konuşma Geçmişi:
{history}

Şu anki soru: {question}

SQL:
"""

SQL_INTERPRETATION_PROMPT = """SQL sonuçlarını kullanıcının isteğine göre sun.

Soru: {question}
SQL: {sql_query}
Sonuçlar: {results}

Talimatlar:
1. Kullanıcı "listele", "göster", "ver" gibi kelimeler kullandıysa sonuçları TEK TEK LİSTELE:
   - Her sonucu numaralandır
   - İlgili bilgileri (şirket, yorum içeriği vb.) göster
   - Özet YAPMA, direkt verileri listele
2. Kullanıcı "kaç", "sayısı" gibi sorular sorduysa sadece sayıyı ver
3. Kullanıcı analiz veya özet istiyorsa özetle
4. Türkçe cevap ver

Cevap:
"""

# ANALYZE_COMMENTS_PROMPT - Kullanılmıyor, RAG_ANALYSIS_PROMPT kullanılıyor
# ANALYZE_COMMENTS_PROMPT = """Aşağıdaki yorumları kullanıcının isteğine göre sun.
# 
# Kullanıcı Sorusu: {question}
# 
# Yorumlar:
# {comments}
# 
# Talimatlar:
# 1. Kullanıcı "listele", "göster", "ver" gibi kelimeler kullandıysa YORUMLARI TEK TEK LİSTELE:
#    - Her yorumu numaralandır
#    - Şirket adını ve yorum içeriğini tam olarak göster
#    - Özet YAPMA, direkt yorumları listele
# 2. Kullanıcı analiz, hakaret, şikayet vb. arama istiyorsa ilgili yorumları bul ve göster
# 3. Türkçe cevap ver
# 4. Eğer istenen içerik yoksa bunu belirt
# 
# Cevap:
# """

RAG_ANALYSIS_PROMPT = """Aşağıda semantic search ile bulunan, kullanıcının sorusuna EN BENZER yorumlar listelenmiştir.
Benzerlik skoru yüksek olanlar soruyla daha alakalıdır.

Kullanıcı Sorusu: {question}

Bulunan Yorumlar (benzerlik sırasına göre):
{comments}

Talimatlar:
1. Bu yorumlar semantic search ile bulundu - yani kullanıcının sorusuyla anlam olarak en benzer yorumlar
2. Kullanıcı "listele", "göster", "ver" gibi kelimeler kullandıysa YORUMLARI TEK TEK LİSTELE:
   - Her yorumu numaralandır
   - Şirket adını ve yorum içeriğini göster
   - Özet YAPMA, direkt yorumları listele
3. Kullanıcı analiz, özet veya genel bilgi istiyorsa özetle
4. Türkçe cevap ver
5. Eğer soruyla ilgili yorum bulunamadıysa bunu belirt

Cevap:
"""
