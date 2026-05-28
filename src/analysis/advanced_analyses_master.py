import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from itertools import combinations
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import learning_curve
from sklearn.metrics import accuracy_score, f1_score
from transformers import pipeline
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def clean_text(text):
    if not isinstance(text, str): return ""
    return " ".join(text.split())

def main():
    print("Veri yükleniyor...")
    train_df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "train_set.csv"), encoding='utf-8-sig')
    test_df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "test_set.csv"), encoding='utf-8-sig')
    
    train_df['text'] = train_df['text'].apply(clean_text)
    test_df['text'] = test_df['text'].apply(clean_text)
    
    if 'noise' in train_df['label'].values or 'crisis' in train_df['label'].values:
        label_map = {'crisis': 1, 'noise': 0}
        train_df['label'] = train_df['label'].map(label_map).fillna(train_df['label'])
        test_df['label'] = test_df['label'].map(label_map).fillna(test_df['label'])
    
    train_df = train_df.dropna(subset=['text', 'label'])
    test_df = test_df.dropna(subset=['text', 'label'])
    
    # Sadece kriz verileri
    all_df = pd.concat([train_df, test_df], ignore_index=True)
    crisis_df = all_df[all_df['label'] == 1].copy()
    noise_df = all_df[all_df['label'] == 0].copy()
    
    # ------------------------------------------------------------------
    # BÖLÜM 1: KONU MODELLEME (LDA)
    # ------------------------------------------------------------------
    print("\nBölüm 1: LDA Konu Modellemesi Başlıyor...")
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words=['ve', 'bir', 'bu', 'için', 'ile', 'de', 'da', 'mi', 'mu'])
    tf = tf_vectorizer.fit_transform(crisis_df['text'])
    
    lda = LatentDirichletAllocation(n_components=3, random_state=42, max_iter=10)
    lda.fit(tf)
    
    tf_feature_names = tf_vectorizer.get_feature_names_out()
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True)
    for topic_idx, topic in enumerate(lda.components_):
        top_features_ind = topic.argsort()[: -10 - 1 : -1]
        top_features = [tf_feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]
        
        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7, color='teal')
        ax.set_title(f'Konu (Topic) {topic_idx + 1}', fontdict={'fontsize': 14, 'fontweight': 'bold'})
        ax.invert_yaxis()
        ax.tick_params(axis='both', which='major', labelsize=10)

    plt.suptitle('Kriz Tweetlerinde Konu Modelleme (LDA) - 3 Ana Tema', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "topic_modeling_lda.png"), dpi=300)
    plt.close()
    
    # ------------------------------------------------------------------
    # BÖLÜM 2: CROSS-DOMAIN GENELLEME
    # ------------------------------------------------------------------
    print("\nBölüm 2: Çapraz Olay (Cross-Domain) Genelleme Testi...")
    # 'deprem', 'yangin' vs. kategorilerini ayır
    # Subcategory sütunu train_df'de de var mı?
    if 'subcategory' in all_df.columns:
        source_cats = ['deprem', 'yangin', '15temmuz']
        target_cats = ['maden', 'sarachane', 'bogazici', 'corlu']
        
        # Filtreleme (büyük-küçük harf duyarsız)
        def map_cat(c): return str(c).lower().replace('ş', 's').replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u')
        all_df['norm_cat'] = all_df['subcategory'].apply(map_cat)
        
        # Noise eklemek zorundayız ki model iki sınıfı da öğrensin
        noise_mask = all_df['norm_cat'] == 'noise'
        
        # Eğitim seti: Kaynak afetler + Tüm noiseların yarısı
        source_mask = all_df['norm_cat'].apply(lambda x: any(sc in x for sc in source_cats))
        train_cd_mask = source_mask | noise_mask
        
        # Test seti: Hedef afetler
        target_mask = all_df['norm_cat'].apply(lambda x: any(tc in x for tc in target_cats))
        
        if sum(source_mask) > 0 and sum(target_mask) > 0:
            X_train_cd = all_df[train_cd_mask]['text']
            y_train_cd = all_df[train_cd_mask]['label'].astype(int)
            X_test_cd = all_df[target_mask]['text']
            y_test_cd = all_df[target_mask]['label'].astype(int)
            
            vec_cd = TfidfVectorizer(max_features=5000)
            X_train_vec_cd = vec_cd.fit_transform(X_train_cd)
            X_test_vec_cd = vec_cd.transform(X_test_cd)
            
            lr_cd = LogisticRegression(C=10, class_weight='balanced')
            lr_cd.fit(X_train_vec_cd, y_train_cd)
            preds_cd = lr_cd.predict(X_test_vec_cd)
            
            # They are all label=1 (crisis) in target_mask since noise is not in target_cats.
            # So Accuracy == Recall here.
            cd_acc = accuracy_score(y_test_cd, preds_cd)
            
            plt.figure(figsize=(6, 5))
            bars = plt.bar(['Cross-Domain\n(Maden/Saraçhane Test)'], [cd_acc * 100], color='#e67e22', edgecolor='black', width=0.4)
            plt.ylim(0, 100)
            plt.ylabel('Tespit Başarısı (Recall %)', fontsize=12, fontweight='bold')
            plt.title('Çapraz Afet (Cross-Domain) Başarımı', fontsize=14, fontweight='bold')
            plt.text(0, (cd_acc*100) + 2, f"%{(cd_acc*100):.1f}", ha='center', fontsize=12, fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "cross_domain_generalization.png"), dpi=300)
            plt.close()
    else:
        print("Subcategory sütunu bulunamadığı için Cross-Domain atlandı.")

    # ------------------------------------------------------------------
    # BÖLÜM 3: NER (VARLIK İSMİ TANIMA) İLE LOKASYON ÇIKARIMI
    # ------------------------------------------------------------------
    print("\nBölüm 3: NER Modeli İndiriliyor ve Lokasyon Çıkarılıyor...")
    # Test setindeki kriz tweetlerinden sadece 100 tanesini seçerek hızlandıralım
    test_crisis = test_df[test_df['label'] == 1].head(100)
    
    try:
        ner_pipe = pipeline("ner", model="savasy/bert-base-turkish-ner-cased", aggregation_strategy="simple")
        
        loc_count = 0
        extracted_locations = []
        
        for idx, row in tqdm(test_crisis.iterrows(), total=len(test_crisis), desc="NER İşleniyor"):
            entities = ner_pipe(row['text'])
            locs = [ent['word'] for ent in entities if ent['entity_group'] in ['LOC']]
            if len(locs) > 0:
                loc_count += 1
                extracted_locations.append((row['text'], locs))
        
        ner_rate = (loc_count / len(test_crisis)) * 100
        
        with open(os.path.join(WORKSPACE, "outputs", "reports", "ner_location_recovery_report.md"), "w", encoding="utf-8") as f:
            f.write("# Otonom Lokasyon Keşfi (NER) Raporu\n\n")
            f.write("Kullanıcıların %100'ü profil lokasyonunu gizlemiş olsa da (Location Deception), ")
            f.write("gelişmiş NLP modelleri kullanılarak metin içindeki lokasyonlar analiz edilmiştir.\n\n")
            f.write(f"**Sonuç:** Analiz edilen {len(test_crisis)} kriz tweetinin **%{ner_rate:.1f}'ünde** ")
            f.write("başarılı bir şekilde coğrafi lokasyon (LOC) tespit edilmiştir.\n\n")
            f.write("### Tespit Edilen Bazı Örnekler:\n")
            for t, l in extracted_locations[:10]:
                f.write(f"- **Bulunan:** `{', '.join(l)}` | **Tweet:** {t}\n")
    except Exception as e:
        print(f"NER İşleminde hata (Ağ veya Modülden kaynaklı olabilir): {e}")

    # ------------------------------------------------------------------
    # BÖLÜM 4: CO-OCCURRENCE NETWORK (AĞ GRAFİĞİ)
    # ------------------------------------------------------------------
    print("\nBölüm 4: Kelime Ortak Görünüm Ağı Çiziliyor...")
    vec = CountVectorizer(max_features=30, stop_words=['ve', 'bir', 'bu', 'da', 'de', 'mi', 'mu', 'için', 'ile'])
    X_counts = vec.fit_transform(crisis_df['text'].sample(min(2000, len(crisis_df)), random_state=42))
    words = vec.get_feature_names_out()
    
    co_matrix = (X_counts.T * X_counts)
    co_matrix.setdiag(0)
    
    G = nx.Graph()
    for i in range(len(words)):
        for j in range(i+1, len(words)):
            weight = co_matrix[i, j]
            if weight > 20: # Threshold
                G.add_edge(words[i], words[j], weight=weight)
                
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    edges = G.edges()
    weights = [G[u][v]['weight']/100 for u, v in edges]
    
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, 
            font_size=10, font_weight='bold', edge_color='gray', width=weights)
            
    plt.title('Kriz Anı Kelime Ağı (Co-occurrence Network)', fontsize=16, fontweight='bold')
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "crisis_word_network.png"), dpi=300)
    plt.close()

    # ------------------------------------------------------------------
    # BÖLÜM 5: LEARNING CURVE
    # ------------------------------------------------------------------
    print("\nBölüm 5: Öğrenme Eğrisi (Learning Curve) Hesaplanıyor...")
    X_all = all_df['text']
    y_all = all_df['label'].astype(int)
    
    vec_lc = TfidfVectorizer(max_features=5000)
    X_all_vec = vec_lc.fit_transform(X_all)
    
    train_sizes, train_scores, test_scores = learning_curve(
        LogisticRegression(C=10), X_all_vec, y_all, cv=3, n_jobs=-1, 
        train_sizes=np.linspace(0.1, 1.0, 5), scoring='f1_macro')
        
    train_mean = np.mean(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    
    plt.figure(figsize=(8, 6))
    plt.plot(train_sizes, train_mean, 'o-', color="r", label="Eğitim Skoru")
    plt.plot(train_sizes, test_mean, 'o-', color="g", label="Çapraz Doğrulama Skoru (Test)")
    plt.title('Öğrenme Eğrisi (Veri Miktarı vs Başarı)', fontsize=14, fontweight='bold')
    plt.xlabel('Eğitim Verisi Boyutu', fontsize=12, fontweight='bold')
    plt.ylabel('F1 Makro Skor', fontsize=12, fontweight='bold')
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "learning_curve_analysis.png"), dpi=300)
    plt.close()

    # ------------------------------------------------------------------
    # BÖLÜM 6: LEXICAL RICHNESS (TTR)
    # ------------------------------------------------------------------
    print("\nBölüm 6: Sözcüksel Çeşitlilik (Panik Dili) Analizi...")
    def get_ttr(text):
        tokens = str(text).split()
        if len(tokens) == 0: return 0
        return len(set(tokens)) / len(tokens)
        
    all_df['ttr'] = all_df['text'].apply(get_ttr)
    
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='label', y='ttr', data=all_df, palette=['#3498db', '#e74c3c'])
    plt.xticks([0, 1], ['Gürültü (Noise)', 'Kriz (Crisis)'], fontsize=12, fontweight='bold')
    plt.ylabel('Type/Token Oranı (Sözcük Çeşitliliği)', fontsize=12, fontweight='bold')
    plt.title('Kriz Anında Dilin Basitleşmesi: Panik Dili Analizi', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "lexical_richness_boxplot.png"), dpi=300)
    plt.close()

    print("\n TUM ILERI DUZEY ANALIZLER TAMAMLANDI!")

if __name__ == "__main__":
    main()
