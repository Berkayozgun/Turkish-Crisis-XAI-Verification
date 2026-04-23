# Turkish Crisis XAI & Semantic Location Verification

**Kara Kutuyu Kırmak ve Konum Yanıltmacasını Aşmak: Türkçe Kriz Tweetleri İçin Morfoloji Duyarlı Açıklanabilir Yapay Zeka ve Anlamsal Konum Doğrulama Sistemi**

[cite_start]Bu proje, sosyal medyadaki kriz anlarını tespit ederken karşılaşılan **dilbilimsel (morfolojik)** ve **davranışsal (konum yanıltmacası)** engelleri aşmak için geliştirilmiş uçtan uca bir anomali tespit mimarisidir[cite: 1, 3, 4].

## 🚀 Proje Özeti
[cite_start]Sistem, 32.000 satırlık gerçek dünya tweet verisi üzerinde [cite: 20] BERTurk mimarisini kullanarak kriz anlarını sınıflandırır. [cite_start]Standart modellerin aksine, Türkçenin eklemeli yapısına duyarlı bir **Açıklanabilir Yapay Zeka (XAI)** katmanı ve metin içeriğinden gerçek konumu doğrulayan bir **NER (Varlık İsmi Tanıma)** modülü sunar[cite: 14, 16, 18, 19].

## 🛠️ Teknik Yığın (Tech Stack)
| Bileşen | Teknoloji |
| :--- | :--- |
| **Dil Modeli** | [cite_start]BERTurk (Fine-tuned), HAN [cite: 22, 23] |
| **Backend** | [cite_start]FastAPI (Asynchronous) [cite: 24] |
| **Frontend** | [cite_start]Next.js (Dashboard & Visualizations) [cite: 27] |
| **Açıklanabilirlik** | [cite_start]SHAP, LIME (Morphology-aware) [cite: 14, 16] |
| [cite_start]**Konum Analizi** | spaCy / Stanza (Custom NER) [cite: 19, 25] |

## 🧠 Akademik Özgünlük (Novelty)
- [cite_start]**Morfoloji Duyarlı XAI:** Altınok (2025) tarafından saptanan "aşırı bölütleme" sorununu aşarak, model kararlarını anlamsız heceler yerine anlamlı kelime köklerine dayandırır[cite: 10, 16, 17].
- [cite_start]**Anlamsal Konum Doğrulama:** Yang (2016) tarafından belirtilen "Location Deception" (Konum Yanıltmacası) problemini, kullanıcı meta verilerine güvenmek yerine doğrudan tweet metni içindeki yer isimlerini (NER) kullanarak çözer[cite: 8, 9, 18, 19, 20].

## 📊 Değerlendirme Metrikleri
[cite_start]Proje başarısı, klasik F1 skorunun ötesinde, Türkçeye özgü şu akademik metriklerle ölçülmektedir[cite: 29, 30]:
- [cite_start]Boundary micro-F1 [cite: 31]
- [cite_start]Over/Under-segmentation Indices [cite: 31]
- [cite_start]Lemma Integrity [cite: 31]

## 📜 Kaynakça
Bu proje kapsamında **Altınok (2025)**, **Yang (2016)**, **Schweter (2020)** ve **Devlin vd. (2019)[cite_start]** gibi temel literatür kaynakları referans alınmıştır[cite: 36, 41, 51, 56].

---
*Bu proje [Trakya Üniversitesi] Bilgisayar Mühendisliği Yüksek Lisans Programı kapsamında geliştirilmektedir.*
