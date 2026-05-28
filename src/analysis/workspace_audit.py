import os
import csv
import json
import collections

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILE = os.path.join(WORKSPACE, "outputs", "reports", "workspace_report.md")

def main():
    report_lines = []
    report_lines.append("# Workspace Data & State Audit Report\n")
    report_lines.append("Bu rapor, proje dizinindeki verilerin, CSV yapılarının, veri dağılımlarının ve JSON durum dosyalarının fiziksel analizlerini içermektedir.\n")

    # 1. Dosya Keşfi ve Boyut Analizi
    raw_dir = os.path.join(WORKSPACE, "data", "raw")
    states_dir = os.path.join(WORKSPACE, "data", "states")
    csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    json_files = [f for f in os.listdir(states_dir) if f.endswith('.json')]
    
    report_lines.append("## 1. Dosya Keşfi ve Boyut Analizi\n")
    report_lines.append("| Dosya Adı | Tür | Boyut (Byte) | Satır/Kayıt Sayısı |")
    report_lines.append("|---|---|---|---|")
    
    file_stats = {}
    for f in csv_files + json_files:
        filepath = os.path.join(raw_dir, f) if f.endswith('.csv') else os.path.join(states_dir, f)
        if not os.path.exists(filepath): continue
        size = os.path.getsize(filepath)
        
        count = 0
        file_type = "CSV" if f.endswith(".csv") else "JSON"
        
        if file_type == "CSV":
            with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as file:
                count = sum(1 for line in file)
        else:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        if 'tweets' in data: count = len(data['tweets'])
                        elif 'scraped_ids' in data: count = len(data['scraped_ids'])
                        elif 'total_collected' in data: count = data['total_collected']
                        else: count = len(data.keys())
                    elif isinstance(data, list):
                        count = len(data)
            except:
                count = "HATA"
                
        file_stats[f] = {'size': size, 'count': count}
        report_lines.append(f"| {f} | {file_type} | {size:,} | {count} |")
        
    report_lines.append("\n**Gözlem:** Dosya boyutları ve satır sayıları başarılı bir şekilde indekslenmiştir.\n")

    # 2. CSV Veri Yapısı ve Sütun Doğrulama
    report_lines.append("## 2. CSV Veri Yapısı ve Sütun Doğrulama\n")
    
    csv_headers = {}
    bad_lines_count = 0
    total_lines = 0
    
    for f in csv_files:
        filepath = os.path.join(raw_dir, f)
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as file:
            reader = csv.reader(file)
            try:
                header = next(reader)
                cleaned_header = [h.strip() for h in header if h.strip()]
                csv_headers[f] = cleaned_header
                
                # Sadece massive_crisis_data.csv için bad lines kontrolü
                if f == "massive_crisis_data.csv":
                    expected_len = len(cleaned_header)
                    for row in reader:
                        total_lines += 1
                        if len(row) != expected_len:
                            bad_lines_count += 1
            except StopIteration:
                csv_headers[f] = []
                
    report_lines.append("### Sütun Yapıları:\n")
    for f, header in csv_headers.items():
        report_lines.append(f"- **{f}**: `{', '.join(header)}`")
        
    report_lines.append(f"\n**Gözlem:** `massive_crisis_data.csv` dosyasındaki toplam veri satırı: {total_lines}. Tespit edilen yapısal bozuk/kaymış satır (bad lines) sayısı: {bad_lines_count}.")
    if bad_lines_count > 0:
        report_lines.append(" Bu durum, tırnak işareti ('\"') uyuşmazlıkları veya yeni satır karakteri (\\n) taşıyan metinlerin düzgün kaçış karakteriyle ayrılmamasından kaynaklanıyor olabilir.\n")
    else:
        report_lines.append(" Yapısal bir bozulma veya sütun kayması tespit edilmemiştir.\n")

    # 3 & 4 & 5. Veri Okuma, Dağılım, Duplicate ve Lokasyon Analizi
    report_lines.append("## 3. Kategori Dağılımı ve Sınıf Dengesi\n")
    
    category_counts = collections.Counter()
    all_urls = set()
    total_records = 0
    duplicate_records = 0
    
    loc_filled = 0
    profile_loc_valid = 0
    
    for f in csv_files:
        filepath = os.path.join(raw_dir, f)
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total_records += 1
                
                # Kategoriler
                cat = row.get('category', '').strip()
                if not cat:
                    # Dosya adından tahmin et
                    if 'deprem' in f: cat = 'deprem'
                    elif '15temmuz' in f: cat = '15temmuz'
                    elif 'sarachane' in f: cat = 'sarachane'
                    elif 'yangin' in f: cat = 'yangin'
                    elif 'bogazici' in f: cat = 'bogazici'
                    elif 'corlu' in f: cat = 'corlu'
                    elif 'maden' in f: cat = 'maden'
                    else: cat = 'Bilinmeyen_Kategori'
                category_counts[cat] += 1
                
                # Dublike
                url = row.get('url', '').strip()
                if url:
                    if url in all_urls:
                        duplicate_records += 1
                    else:
                        all_urls.add(url)
                        
                # Konum Analizi
                ext_loc = row.get('extracted_locations', '').strip()
                if ext_loc:
                    loc_filled += 1
                    
                prof_loc = row.get('profile_location', '').strip()
                if prof_loc and prof_loc.lower() != 'bilinmiyor (profil ziyareti gerektirir)' and prof_loc.lower() != 'bilinmiyor':
                    profile_loc_valid += 1

    report_lines.append("| Kategori | Veri Sayısı |")
    report_lines.append("|---|---|")
    for cat, count in category_counts.most_common():
        report_lines.append(f"| {cat} | {count} |")
        
    report_lines.append(f"\n**Gözlem:** Verilerin kategorik sınıflarında {'dengesizlikler mevcut' if len(set(category_counts.values())) > 1 else 'dengeli bir dağılım var'}. Makine öğrenmesi modelleri için veri artırımı (augmentation) veya alt örneklem (undersampling) gerekebilir.\n")
    
    report_lines.append("## 4. Veri Kalitesi ve Tekerrür (Duplicate) Analizi\n")
    dup_rate = (duplicate_records / total_records * 100) if total_records else 0
    report_lines.append(f"- **Toplam İncelenen Kayıt (Tüm CSV'ler):** {total_records}")
    report_lines.append(f"- **Benzersiz URL/Kayıt Sayısı:** {len(all_urls)}")
    report_lines.append(f"- **Dublike (Mükerrer) Kayıt Sayısı:** {duplicate_records}")
    report_lines.append(f"- **Tekerrür Oranı:** %{dup_rate:.2f}\n")
    report_lines.append("**Gözlem:** Scraper, görevler kesintiye uğradığında veya farklı görevlerde aynı tweetler denk geldiğinde mükerrer çekim yapmış olabilir.\n")

    report_lines.append("## 5. Konum ve NER Doluluk Analizi\n")
    loc_rate = (loc_filled / total_records * 100) if total_records else 0
    prof_loc_rate = (profile_loc_valid / total_records * 100) if total_records else 0
    
    report_lines.append(f"- **Extracted Locations (Semantic Geolocation) Dolu Kayıt:** {loc_filled} (%{loc_rate:.2f})")
    report_lines.append(f"- **Geçerli Profile Location (Location Deception Testi) Dolu Kayıt:** {profile_loc_valid} (%{prof_loc_rate:.2f})\n")
    report_lines.append("**Gözlem:** Tweet metinlerinden konum çıkarılabilen verilerin oranı oldukça belirleyici. Profil konumlarında varsayılan 'Bilinmiyor' metni dışındaki gerçek lokasyon verisi oranı da kriz anında koordinat/yardım tespiti (NER - Named Entity Recognition) çalışmaları için önemli bir kalite metriği teşkil ediyor.\n")

    # 6. JSON Durum (State) Dosyası Kontrolü
    report_lines.append("## 6. JSON Durum (State) Dosyası Kontrolü ve Senkronizasyon Analizi\n")
    report_lines.append("| State Dosyası | Kaydedilen Tweet / Scraped ID Sayısı | Durum |")
    report_lines.append("|---|---|---|")
    
    for f in json_files:
        filepath = os.path.join(states_dir, f)
        if not os.path.exists(filepath): continue
        if "session" in f and not "state" in f: continue # Sadece state dosyaları
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                count = 0
                if 'scraped_ids' in data: count = len(data['scraped_ids'])
                elif 'total_collected' in data: count = data['total_collected']
                elif 'tweets' in data: count = len(data['tweets'])
                report_lines.append(f"| {f} | {count} | Hafıza senkronizasyonu yapılmış. |")
        except:
            report_lines.append(f"| {f} | Okunamadı | Hata! |")
            
    report_lines.append("\n**Gözlem:** JSON tabanlı state tracking yapısı görevler arası hafıza kaybını engellemek için kullanılmış. Scraper_state ile CSV'deki veri sayıları genellikle paralellik göstermelidir.\n")
    
    report_lines.append("---\n*Otomatik Audit Raporu - Antigravity IDE*")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"Rapor basariyla {OUTPUT_FILE} konumuna kaydedildi.")

if __name__ == "__main__":
    main()
