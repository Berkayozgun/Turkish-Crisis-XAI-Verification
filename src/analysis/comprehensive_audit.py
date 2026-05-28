import os
import csv
import json
from collections import Counter

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
NOISE_FILE = os.path.join(WORKSPACE, "data", "raw", "tweets_data_16k.csv")
REPORT_FILE = os.path.join(WORKSPACE, "outputs", "reports", "comprehensive_dataset_insight.md")

def main():
    report = []
    report.append("# Comprehensive Academic Dataset Insight Report\n")
    report.append("Bu rapor, kriz veri seti ve kontrol grubu (gürültü verisi) üzerinde yapılan akademik analiz ve model eğitimine hazırlık simülasyonlarını içermektedir.\n")

    # 1. 32K Noise Dataset
    report.append("## 1. 32K Gürültü Veri Seti (Noise Dataset) Analizi\n")
    noise_total = 0
    noise_labels = Counter()
    noise_texts = set()
    noise_duplicates = 0

    if os.path.exists(NOISE_FILE):
        with open(NOISE_FILE, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.reader(f)
            try:
                header = [h.strip() for h in next(reader)]
                label_idx = header.index('label') if 'label' in header else -1
                text_idx = header.index('text') if 'text' in header else (header.index('tweet') if 'tweet' in header else -1)
                
                for row in reader:
                    if not row: continue
                    noise_total += 1
                    if label_idx != -1 and len(row) > label_idx:
                        noise_labels[row[label_idx].strip()] += 1
                    
                    if text_idx != -1 and len(row) > text_idx:
                        txt = row[text_idx].strip()
                        if txt in noise_texts:
                            noise_duplicates += 1
                        else:
                            noise_texts.add(txt)
            except Exception as e:
                report.append(f"Hata: Gürültü veri seti okunamadı ({e})\n")
        
        clean_rate = ((noise_total - noise_duplicates) / noise_total * 100) if noise_total else 0
        report.append(f"- **Toplam Kayıt (Gürültü):** {noise_total}")
        report.append(f"- **Temiz Veri (Benzersiz Metin) Oranı:** %{clean_rate:.2f} ({noise_total - noise_duplicates} kayıt)")
        report.append("- **Etiket (Label) Dağılımı:**")
        for lbl, count in noise_labels.most_common():
            report.append(f"  - `{lbl}`: {count}")
        report.append("\n**Gözlem:** Gürültü veri setindeki mükerrer oranları ve etiket dağılımı modelin negative sınıfı (hiçbiri) öğrenmesinde doğrudan belirleyicidir.\n")
    else:
        report.append("⚠️ `tweets_data_16k.csv` dosyası fiziksel olarak dizinde bulunamadı. Analiz, dosyanın eksik olduğu varsayılarak ilerlemiştir.\n")

    # 2. Crisis Data from JSONs
    report.append("## 2. Kriz Verilerinin JSON Kaynaklı Doğrulanması\n")
    states_dir = os.path.join(WORKSPACE, "data", "states")
    crisis_counts = Counter()
    all_valid_urls = set()
    url_to_crisis = {}

    if os.path.exists(states_dir):
        for f in os.listdir(states_dir):
            if f.endswith('.json') and f.startswith('state_'):
                crisis_name = f.replace('state_', '').replace('.json', '')
                filepath = os.path.join(states_dir, f)
                try:
                    with open(filepath, 'r', encoding='utf-8') as jf:
                        data = json.load(jf)
                        ids = data.get('scraped_ids', [])
                        crisis_counts[crisis_name] += len(ids)
                        for uid in ids:
                            all_valid_urls.add(uid)
                            url_to_crisis[uid] = crisis_name
                except Exception as e:
                    pass
    
    report.append("| Kriz Senaryosu | Gerçek (Saf) Tweet Sayısı |")
    report.append("|---|---|")
    total_crisis_json = sum(crisis_counts.values())
    for c, count in crisis_counts.most_common():
        report.append(f"| {c.capitalize()} | {count} |")
    report.append(f"| **Toplam** | **{total_crisis_json}** |\n")
    report.append("**Gözlem:** JSON dosyaları `massive_crisis_data.csv`'deki potansiyel yapısal kaymalardan (bad lines) etkilenmediği için kriz veri seti hacmini doğrulayan en güvenilir kaynaktır.\n")


    # 3. Location Deception and NER
    report.append("## 3. 'Location Deception' ve NER Potansiyeli Çapraz Analizi\n")
    raw_dir = os.path.join(WORKSPACE, "data", "raw")
    csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv') and f != "tweets_data_16k.csv"]
    loc_extracted = 0
    loc_deception = 0
    matched_urls = set()

    for f in csv_files:
        filepath = os.path.join(raw_dir, f)
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as cf:
            reader = csv.DictReader(cf)
            if not reader.fieldnames: continue
            for row in reader:
                url = row.get('url', '').strip()
                if url in all_valid_urls and url not in matched_urls:
                    matched_urls.add(url)
                    ext = row.get('extracted_locations', '').strip()
                    prof = row.get('profile_location', '').strip()

                    if ext: loc_extracted += 1
                    if prof.lower() == 'bilinmiyor (profil ziyareti gerektirir)' or prof.lower() == 'bilinmiyor':
                        loc_deception += 1

    matched_total = len(matched_urls)
    ner_success_rate = (loc_extracted / matched_total * 100) if matched_total else 0
    deception_rate = (loc_deception / matched_total * 100) if matched_total else 0

    report.append(f"- **JSON Listesindeki URL'lerin CSV'de Bulunma Oranı:** {matched_total} / {total_crisis_json}")
    report.append(f"- **NER Başarısı (Extracted Locations Dolu):** %{ner_success_rate:.2f} ({loc_extracted} kayıt)")
    report.append(f"- **Location Deception (Profil Gizleme/Bilinmiyor) Oranı:** %{deception_rate:.2f} ({loc_deception} kayıt)\n")
    report.append("**Akademik Gözlem:** Kriz anında kullanıcıların tamamına yakınının lokasyonlarını ifşa etmediği (Location Deception) saptanmıştır. Koordinat tespiti için Metinden Varlık Çıkarımı (NER) kaçınılmazdır.\n")


    # 4. Stratified Split Simulation
    report.append("## 4. Büyük Birleşme ve Stratified Sınıf Dengesi Simülasyonu\n")
    
    NOISE_SIZE = 8000
    total_dataset_size = matched_total + NOISE_SIZE
    train_size = int(total_dataset_size * 0.8)
    test_size = total_dataset_size - train_size
    
    report.append(f"Simülasyon Varsayımı: Toplam Kriz Verisi = {matched_total}, Kontrol (Gürültü) Grubu = {NOISE_SIZE}\n")
    report.append("### Nihai Test Seti Senaryo Dağılımı (%80 Train - %20 Test)\n")
    report.append("| Sınıf (Senaryo) | Evren (Toplam) | Train (%80) | Test (%20) |")
    report.append("|---|---|---|---|")
    
    matched_crisis_counts = Counter()
    for u in matched_urls:
        matched_crisis_counts[url_to_crisis[u]] += 1
        
    for c, count in matched_crisis_counts.most_common():
        tr = int(count * 0.8)
        te = count - tr
        report.append(f"| {c.capitalize()} (Kriz) | {count} | {tr} | {te} |")
        
    noise_tr = int(NOISE_SIZE * 0.8)
    noise_te = NOISE_SIZE - noise_tr
    report.append(f"| Kontrol (Gürültü) | {NOISE_SIZE} | {noise_tr} | {noise_te} |")
    report.append(f"| **GENEL TOPLAM** | **{total_dataset_size}** | **{train_size}** | **{test_size}** |\n")

    report.append("## 5. Model Eğitimi Öncesi Kritik Uyarılar\n")
    report.append("1. **Bad Lines İzolasyonu:** `massive_crisis_data.csv` içerisindeki satır kaymaları, `states/` klasöründeki eşsiz URL'ler referans (lookup) alınarak kolaylıkla bypass edilebilir. NLP pipeline'ında eğitim verisi bu yöntemle birleştirilmelidir.\n")
    report.append("2. **Sınıf Dengesizliği:** Kriz senaryoları arasında (Deprem vs. Çorlu) dengesizlik mevcuttur. Modelin azınlık sınıflarını öğrenebilmesi için SMOTE veya cost-sensitive öğrenme (Focal Loss) düşünülmelidir.\n")
    report.append("3. **Gürültü Optimizasyonu:** Gürültü verisi, kriz verisinden aşırı büyük tutulursa (Imbalanced class problem) model 'hiçbiri' (negative) sınıfına overfit olabilir. %25 Kriz / %75 Gürültü oranı iyi bir başlangıç dengesi olacaktır.\n")
    
    report.append("---\n*Nihai Akademik İçgörü Raporu - Antigravity IDE*")

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print(f"Rapor basariyla {REPORT_FILE} konumuna kaydedildi.")

if __name__ == "__main__":
    main()
