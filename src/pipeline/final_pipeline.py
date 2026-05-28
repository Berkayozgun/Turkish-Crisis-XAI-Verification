import os
import json
import csv
import pandas as pd
from sklearn.model_selection import train_test_split

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    print("Pipeline başlatılıyor...")
    
    # 1. JSON'dan Temiz Kriz Verisi Çekme (Bad Lines Bypass)
    states_dir = os.path.join(WORKSPACE, "data", "states")
    valid_urls = {}
    
    if os.path.exists(states_dir):
        for f in os.listdir(states_dir):
            if f.endswith(".json") and f.startswith("state_"):
                cat = f.replace("state_", "").replace(".json", "")
                path = os.path.join(states_dir, f)
                try:
                    with open(path, 'r', encoding='utf-8') as jf:
                        data = json.load(jf)
                        ids = data.get("scraped_ids", [])
                        for uid in ids:
                            valid_urls[uid] = cat
                except Exception as e:
                    print(f"JSON okuma hatası {f}: {e}")
    
    print(f"Toplam {len(valid_urls)} adet geçerli URL referansı JSON'lardan alındı.")
    
    crisis_data = []
    raw_dir = os.path.join(WORKSPACE, "data", "raw")
    csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    exclude_keywords = ['16k', '32k', 'winvoker', 'train_set', 'test_set']
    
    found_urls = set()
    for f in csv_files:
        if any(k in f.lower() for k in exclude_keywords):
            continue
            
        path = os.path.join(raw_dir, f)
        try:
            with open(path, 'r', encoding='utf-8-sig', errors='ignore') as cf:
                reader = csv.reader(cf)
                for row in reader:
                    if not row: continue
                    
                    matched_url = None
                    for col in row:
                        col_str = str(col).strip()
                        if col_str in valid_urls and col_str not in found_urls:
                            matched_url = col_str
                            break
                            
                    if matched_url:
                        # Metni bul (satırdaki en uzun alan genellikle tweet metnidir)
                        text = max(row, key=lambda x: len(str(x)))
                        text = str(text).replace('\n', ' ').replace('\r', ' ').strip()
                        
                        crisis_data.append({
                            'text': text,
                            'subcategory': valid_urls[matched_url],
                            'label': 'crisis'
                        })
                        found_urls.add(matched_url)
        except Exception as e:
            print(f"CSV okuma hatasi {f}: {e}")
            
    df_crisis = pd.DataFrame(crisis_data)
    print(f"CSV'lerden {len(df_crisis)} adet kriz metni başarıyla eşleştirildi (Bad lines bypass edildi).")

    # 2. 32K Gürültü Verisini Doğru Okuma
    noise_file = os.path.join(raw_dir, "tweets_data_16k.csv")
    df_noise = None
    
    if not os.path.exists(noise_file):
        print("\nUyarı: 'tweets_data_16k.csv' bulunamadı. Alternatif gürültü verisi aranıyor...")
        candidates = [f for f in os.listdir(raw_dir) if 'winvoker' in f.lower() or '16k' in f.lower() or '32k' in f.lower()]
        if candidates:
            noise_file = os.path.join(raw_dir, candidates[0])
            print(f"Gürültü verisi olarak ana dizindeki '{candidates[0]}' kullanılacak.")
        else:
            print("Kritik Hata: Hiçbir gürültü veri seti bulunamadı!")
            return
            
    try:
        df_raw_noise = pd.read_csv(noise_file, encoding='utf-8-sig')
    except Exception as e:
        try:
            df_raw_noise = pd.read_csv(noise_file, encoding='latin-1')
        except Exception as e2:
            print(f"Gürültü dosyasi okunamadi: {e2}")
            return
        
    print(f"Gürültü veri seti başarıyla okundu: Toplam {len(df_raw_noise)} satır.")
    
    # Filtreleme
    if 'label' in df_raw_noise.columns:
        if 'hiçbiri' in df_raw_noise['label'].values:
            df_filtered = df_raw_noise[df_raw_noise['label'] == 'hiçbiri']
        elif 'Notr' in df_raw_noise['label'].values:
            df_filtered = df_raw_noise[df_raw_noise['label'] == 'Notr']
        else:
            df_filtered = df_raw_noise
    else:
        df_filtered = df_raw_noise
        
    if len(df_filtered) < 8000:
        print(f"Uyarı: Gürültü verisinde 8.000 adet 'hiçbiri/Notr' satırı yok ({len(df_filtered)} bulundu). Olanlar alınacak.")
        sampled_noise = df_filtered.copy()
    else:
        sampled_noise = df_filtered.sample(n=8000, random_state=42)
        
    # Text sütununu belirle
    text_col = 'text' if 'text' in sampled_noise.columns else sampled_noise.columns[0]
    
    df_noise_final = pd.DataFrame({
        'text': sampled_noise[text_col].astype(str).str.replace('\n', ' ').str.replace('\r', ' ').str.strip(),
        'subcategory': 'noise',
        'label': 'noise'
    })
    
    print(f"Tam {len(df_noise_final)} adet gürültü verisi başarıyla örneklendi.")

    # 3. KVKK Anonimleştirme ve Birleştirme
    if len(df_crisis) == 0:
        print("HATA: Hiç kriz verisi çıkarılamadı!")
        return

    df_final = pd.concat([df_crisis, df_noise_final], ignore_index=True)
    df_final = df_final[['text', 'subcategory', 'label']]
    df_final.dropna(subset=['text'], inplace=True)
    
    print(f"\nBirleştirilmiş KVKK Anonim Ana Veri Seti: {len(df_final)} satır. (Sadece text, subcategory, label mevcut)")

    # 4. Akademik Stratified Split
    X = df_final['text']
    y = df_final[['subcategory', 'label']]
    
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, stratify=y['subcategory'], random_state=42
        )
    except Exception as e:
        print(f"Stratified split hatası, normal split yapılıyor: {e}")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )
    
    df_train = pd.concat([X_train, y_train], axis=1)
    df_test = pd.concat([X_test, y_test], axis=1)
    
    processed_dir = os.path.join(WORKSPACE, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    train_path = os.path.join(processed_dir, "train_set.csv")
    test_path = os.path.join(processed_dir, "test_set.csv")
    
    df_train.to_csv(train_path, index=False, encoding='utf-8-sig')
    df_test.to_csv(test_path, index=False, encoding='utf-8-sig')
    
    # 5. Nihai Dağılım Raporu (Jüri Standardında)
    print("\n" + "="*50)
    print("NİHAİ TEST SETİ DAĞILIM RAPORU (%20)")
    print("="*50)
    print(f"{'Alt Kategori (Subcategory)':<30} | {'Test Örnek Sayısı':<15}")
    print("-" * 50)
    
    test_counts = df_test['subcategory'].value_counts()
    for cat, count in test_counts.items():
        print(f"{cat.capitalize():<30} | {count:<15}")
    print("-" * 50)
    print(f"{'GENEL TOPLAM':<30} | {len(df_test):<15}")
    print("="*50)
    
    print(f"\nİşlem Başarılı! Veriler KVKK standartlarında anonimleştirildi.")
    print(f"Dosyalar kaydedildi:\n-> {train_path}\n-> {test_path}")

if __name__ == "__main__":
    main()
