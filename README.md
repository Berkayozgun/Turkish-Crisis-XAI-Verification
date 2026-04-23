# Turkish Crisis XAI & Semantic Location Verification

**Kara Kutuyu Kırmak ve Konum Yanıltmacasını Aşmak: Türkçe Kriz Tweetleri İçin Morfoloji Duyarlı Açıklanabilir Yapay Zeka ve Anlamsal Konum Doğrulama Sistemi**

Bu proje, sosyal medyadaki kriz anlarını tespit ederken karşılaşılan **dilbilimsel (morfolojik)** ve **davranışsal (konum yanıltmacası)** engelleri aşmak için geliştirilmiş uçtan uca bir anomali tespit mimarisidir[cite: 1, 3, 4].

## 🚀 Proje Özeti
Sistem, 32.000 satırlık gerçek dünya tweet verisi üzerinde [cite: 20] BERTurk mimarisini kullanarak kriz anlarını sınıflandırır. Standart modellerin aksine, Türkçenin eklemeli yapısına duyarlı bir **Açıklanabilir Yapay Zeka (XAI)** katmanı ve metin içeriğinden gerçek konumu doğrulayan bir **NER (Varlık İsmi Tanıma)** modülü sunar[cite: 14, 16, 18, 19].

## 🛠️ Teknik Yığın (Tech Stack)
| Bileşen | Teknoloji |
| :--- | :--- |
| **Dil Modeli** | BERTurk (Fine-tuned), HAN [cite: 22, 23] |
| **Backend** | FastAPI (Asynchronous) [cite: 24] |
| **Frontend** | Next.js (Dashboard & Visualizations) [cite: 27] |
| **Açıklanabilirlik** | SHAP, LIME (Morphology-aware) [cite: 14, 16] |
| **Konum Analizi** | spaCy / Stanza (Custom NER) [cite: 19, 25] |

## 🧠 Akademik Özgünlük (Novelty)
- **Morfoloji Duyarlı XAI:** Altınok (2025) tarafından saptanan "aşırı bölütleme" sorununu aşarak, model kararlarını anlamsız heceler yerine anlamlı kelime köklerine dayandırır[cite: 10, 16, 17].
- **Anlamsal Konum Doğrulama:** Yang (2016) tarafından belirtilen "Location Deception" (Konum Yanıltmacası) problemini, kullanıcı meta verilerine güvenmek yerine doğrudan tweet metni içindeki yer isimlerini (NER) kullanarak çözer[cite: 8, 9, 18, 19, 20].

## 📊 Değerlendirme Metrikleri
Proje başarısı, klasik F1 skorunun ötesinde, Türkçeye özgü şu akademik metriklerle ölçülmektedir[cite: 29, 30]:
- Boundary micro-F1 [cite: 31]
- Over/Under-segmentation Indices [cite: 31]
- Lemma Integrity [cite: 31]

## 📜 Kaynakça
Bu proje kapsamında **Altınok (2025)**, **Yang (2016)**, **Schweter (2020)** ve **Devlin vd. (2019)** gibi temel literatür kaynakları referans alınmıştır[cite: 36, 41, 51, 56].

---
*Bu proje [Trakya Üniversitesi] Bilgisayar Mühendisliği Yüksek Lisans Programı kapsamında geliştirilmektedir.*
