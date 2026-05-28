# Workspace Data & State Audit Report

Bu rapor, proje dizinindeki verilerin, CSV yapılarının, veri dağılımlarının ve JSON durum dosyalarının fiziksel analizlerini içermektedir.

## 1. Dosya Keşfi ve Boyut Analizi

| Dosya Adı | Tür | Boyut (Byte) | Satır/Kayıt Sayısı |
|---|---|---|---|
| massive_crisis_data.csv | CSV | 1,800,738 | 2486 |
| tweets_15temmuz.csv | CSV | 6,299 | 29 |
| tweets_data.csv | CSV | 13,045 | 51 |
| tweets_deprem.csv | CSV | 188,559 | 596 |
| tweets_sarachane.csv | CSV | 208,520 | 687 |
| winvoker-turkish-sentiment-analysis-dataset-train.csv | CSV | 76,138,381 | 443554 |
| scraper_state.json | JSON | 26,092 | 50 |
| state_15temmuz.json | JSON | 3,354 | 61 |
| state_bogazici_2021.json | JSON | 7,530 | 133 |
| state_corlu_2018.json | JSON | 1,541 | 27 |
| state_deprem.json | JSON | 61,689 | 1106 |
| state_maden_2024.json | JSON | 46,623 | 831 |
| state_sarachane.json | JSON | 36,376 | 642 |
| state_yangin_2021.json | JSON | 16,657 | 296 |

**Gözlem:** Dosya boyutları ve satır sayıları başarılı bir şekilde indekslenmiştir.

## 2. CSV Veri Yapısı ve Sütun Doğrulama

### Sütun Yapıları:

- **massive_crisis_data.csv**: `category, user_handle, url, text, date, extracted_locations, profile_location`
- **tweets_15temmuz.csv**: `url, user_handle, text, date, extracted_locations, profile_location`
- **tweets_data.csv**: `url, user_handle, text, date, extracted_locations, profile_location`
- **tweets_deprem.csv**: `url, user_handle, text, date, extracted_locations, profile_location`
- **tweets_sarachane.csv**: `url, user_handle, text, date, extracted_locations, profile_location`
- **winvoker-turkish-sentiment-analysis-dataset-train.csv**: `text, label, dataset`

**Gözlem:** `massive_crisis_data.csv` dosyasındaki toplam veri satırı: 2473. Tespit edilen yapısal bozuk/kaymış satır (bad lines) sayısı: 779.
 Bu durum, tırnak işareti ('"') uyuşmazlıkları veya yeni satır karakteri (\n) taşıyan metinlerin düzgün kaçış karakteriyle ayrılmamasından kaynaklanıyor olabilir.

## 3. Kategori Dağılımı ve Sınıf Dengesi

| Kategori | Veri Sayısı |
|---|---|
| Bilinmeyen_Kategori | 443202 |
| sarachane | 686 |
| deprem | 595 |
| 15temmuz | 28 |

**Gözlem:** Verilerin kategorik sınıflarında dengesizlikler mevcut. Makine öğrenmesi modelleri için veri artırımı (augmentation) veya alt örneklem (undersampling) gerekebilir.

## 4. Veri Kalitesi ve Tekerrür (Duplicate) Analizi

- **Toplam İncelenen Kayıt (Tüm CSV'ler):** 444511
- **Benzersiz URL/Kayıt Sayısı:** 786
- **Dublike (Mükerrer) Kayıt Sayısı:** 573
- **Tekerrür Oranı:** %0.13

**Gözlem:** Scraper, görevler kesintiye uğradığında veya farklı görevlerde aynı tweetler denk geldiğinde mükerrer çekim yapmış olabilir.

## 5. Konum ve NER Doluluk Analizi

- **Extracted Locations (Semantic Geolocation) Dolu Kayıt:** 349 (%0.08)
- **Geçerli Profile Location (Location Deception Testi) Dolu Kayıt:** 0 (%0.00)

**Gözlem:** Tweet metinlerinden konum çıkarılabilen verilerin oranı oldukça belirleyici. Profil konumlarında varsayılan 'Bilinmiyor' metni dışındaki gerçek lokasyon verisi oranı da kriz anında koordinat/yardım tespiti (NER - Named Entity Recognition) çalışmaları için önemli bir kalite metriği teşkil ediyor.

## 6. JSON Durum (State) Dosyası Kontrolü ve Senkronizasyon Analizi

| State Dosyası | Kaydedilen Tweet / Scraped ID Sayısı | Durum |
|---|---|---|
| scraper_state.json | 50 | Hafıza senkronizasyonu yapılmış. |
| state_15temmuz.json | 61 | Hafıza senkronizasyonu yapılmış. |
| state_bogazici_2021.json | 133 | Hafıza senkronizasyonu yapılmış. |
| state_corlu_2018.json | 27 | Hafıza senkronizasyonu yapılmış. |
| state_deprem.json | 1106 | Hafıza senkronizasyonu yapılmış. |
| state_maden_2024.json | 831 | Hafıza senkronizasyonu yapılmış. |
| state_sarachane.json | 642 | Hafıza senkronizasyonu yapılmış. |
| state_yangin_2021.json | 296 | Hafıza senkronizasyonu yapılmış. |

**Gözlem:** JSON tabanlı state tracking yapısı görevler arası hafıza kaybını engellemek için kullanılmış. Scraper_state ile CSV'deki veri sayıları genellikle paralellik göstermelidir.

---
*Otomatik Audit Raporu - Antigravity IDE*