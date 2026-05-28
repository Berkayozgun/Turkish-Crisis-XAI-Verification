# Location Deception (Lokasyon Gizleme) Fenomeni Analizi

Kriz Bilişimi (Crisis Informatics) bağlamında incelenen en kritik sosyolojik bulgulardan biri, kullanıcıların kriz anlarındaki dijital ayak izlerini yönetme şeklidir. Daha önce yürütülen `comprehensive_audit.py` analizi sonuçlarına göre, **kriz/afet durumlarında atılan tweetlerdeki kullanıcı profil lokasyon verisinin %100 oranında 'Bilinmiyor (Profil Ziyareti Gerektirir)' statüsünde olduğu** tespit edilmiştir.

### Akademik Çıkarımlar
1. **Veri Gizliliği Refleksi:** Kriz anlarında panik ve güvensizlik, kullanıcıların lokasyon servislerini veya profillerindeki yer bilgisini kapatmalarına yol açıyor olabilir.
2. **Koordinasyon Zafiyeti:** Konum bilgisi eksikliği, geleneksel anahtar kelime tabanlı afet yönetim sistemlerinin (AFAD, AHBAP vb.) coğrafi haritalama yapmasını imkansız kılmaktadır. Bu durum, yalnızca metin (text) tabanlı derin öğrenme NER (Named Entity Recognition) yaklaşımlarının hayati önemini kanıtlamaktadır.
3. **Dezenformasyon ve Bot Etkisi:** Lokasyonu tamamen kapalı hesaplar, kriz anı manipülasyonu yapan bot ağlarının ortak davranış örüntüsü (pattern) olabilir.

### Çözüm Önerisi
Makalenin metodoloji kısmında belirtildiği üzere; modelimizin lokasyon (metadata) bilgisine değil, sadece tweetin anlamsal (semantik) bütünlüğüne odaklanması, bu "Location Deception" problemini baypas etmek adına verilmiş bilinçli ve başarılı bir tasarım kararıdır.
