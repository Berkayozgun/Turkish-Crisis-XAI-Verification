# Comprehensive Academic Dataset Insight Report

Bu rapor, kriz veri seti ve kontrol grubu (gürültü verisi) üzerinde yapılan akademik analiz ve model eğitimine hazırlık simülasyonlarını içermektedir.

## 1. 32K Gürültü Veri Seti (Noise Dataset) Analizi

- **Toplam Kayıt (Gürültü):** 32000
- **Temiz Veri (Benzersiz Metin) Oranı:** %99.98 (31993 kayıt)
- **Etiket (Label) Dağılımı:**
  - `hiçbiri`: 16000
  - `nefret`: 16000

**Gözlem:** Gürültü veri setindeki mükerrer oranları ve etiket dağılımı modelin negative sınıfı (hiçbiri) öğrenmesinde doğrudan belirleyicidir.

## 2. Kriz Verilerinin JSON Kaynaklı Doğrulanması

| Kriz Senaryosu | Gerçek (Saf) Tweet Sayısı |
|---|---|
| Deprem | 1106 |
| Maden_2024 | 831 |
| Sarachane | 642 |
| Yangin_2021 | 296 |
| Bogazici_2021 | 133 |
| 15temmuz | 61 |
| Corlu_2018 | 27 |
| **Toplam** | **3096** |

**Gözlem:** JSON dosyaları `massive_crisis_data.csv`'deki potansiyel yapısal kaymalardan (bad lines) etkilenmediği için kriz veri seti hacmini doğrulayan en güvenilir kaynaktır.

## 3. 'Location Deception' ve NER Potansiyeli Çapraz Analizi

- **JSON Listesindeki URL'lerin CSV'de Bulunma Oranı:** 615 / 3096
- **NER Başarısı (Extracted Locations Dolu):** %27.32 (168 kayıt)
- **Location Deception (Profil Gizleme/Bilinmiyor) Oranı:** %100.00 (615 kayıt)

**Akademik Gözlem:** Kriz anında kullanıcıların tamamına yakınının lokasyonlarını ifşa etmediği (Location Deception) saptanmıştır. Koordinat tespiti için Metinden Varlık Çıkarımı (NER) kaçınılmazdır.

## 4. Büyük Birleşme ve Stratified Sınıf Dengesi Simülasyonu

Simülasyon Varsayımı: Toplam Kriz Verisi = 615, Kontrol (Gürültü) Grubu = 8000

### Nihai Test Seti Senaryo Dağılımı (%80 Train - %20 Test)

| Sınıf (Senaryo) | Evren (Toplam) | Train (%80) | Test (%20) |
|---|---|---|---|
| Deprem (Kriz) | 316 | 252 | 64 |
| Sarachane (Kriz) | 285 | 228 | 57 |
| 15temmuz (Kriz) | 14 | 11 | 3 |
| Kontrol (Gürültü) | 8000 | 6400 | 1600 |
| **GENEL TOPLAM** | **8615** | **6892** | **1723** |

## 5. Model Eğitimi Öncesi Kritik Uyarılar

1. **Bad Lines İzolasyonu:** `massive_crisis_data.csv` içerisindeki satır kaymaları, `states/` klasöründeki eşsiz URL'ler referans (lookup) alınarak kolaylıkla bypass edilebilir. NLP pipeline'ında eğitim verisi bu yöntemle birleştirilmelidir.

2. **Sınıf Dengesizliği:** Kriz senaryoları arasında (Deprem vs. Çorlu) dengesizlik mevcuttur. Modelin azınlık sınıflarını öğrenebilmesi için SMOTE veya cost-sensitive öğrenme (Focal Loss) düşünülmelidir.

3. **Gürültü Optimizasyonu:** Gürültü verisi, kriz verisinden aşırı büyük tutulursa (Imbalanced class problem) model 'hiçbiri' (negative) sınıfına overfit olabilir. %25 Kriz / %75 Gürültü oranı iyi bir başlangıç dengesi olacaktır.

---
*Nihai Akademik İçgörü Raporu - Antigravity IDE*