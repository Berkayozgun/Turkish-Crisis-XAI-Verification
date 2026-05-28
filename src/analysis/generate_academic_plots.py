import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def clean_percent(val):
    if isinstance(val, str):
        return float(val.replace('%', '').strip())
    return float(val)

def main():
    print("Veriler yükleniyor...")
    csv_path = os.path.join(WORKSPACE, "outputs", "reports", "final_model_comparison.csv")
    if not os.path.exists(csv_path):
        print(f"Hata: {csv_path} bulunamadı!")
        return
        
    df = pd.read_csv(csv_path)
    
    # Yüzdelik değerleri numerik formata çevir
    df['Accuracy_val'] = df['Accuracy'].apply(clean_percent)
    df['Crisis F1-Score_val'] = df['Crisis F1-Score'].apply(clean_percent)
    df['Crisis Recall_val'] = df['Crisis Recall'].apply(clean_percent)
    
    # Görselleştirme stili
    sns.set_theme(style="whitegrid")
    
    # -------------------------------------------------------------------------
    # Grafik 1: academic_performance_comparison.png
    # -------------------------------------------------------------------------
    print("1. academic_performance_comparison.png üretiliyor...")
    plt.figure(figsize=(14, 7))
    
    x = np.arange(len(df['Model']))
    width = 0.25
    
    bars1 = plt.bar(x - width, df['Accuracy_val'], width, label='Accuracy', color='#3498db', edgecolor='black')
    bars2 = plt.bar(x, df['Crisis F1-Score_val'], width, label='Crisis F1-Score', color='#e67e22', edgecolor='black')
    bars3 = plt.bar(x + width, df['Crisis Recall_val'], width, label='Crisis Recall', color='#2ecc71', edgecolor='black')
    
    plt.ylabel('Skor (%)', fontsize=14, fontweight='bold')
    plt.title('Modellerin Akademik Performans Karşılaştırması', fontsize=18, fontweight='bold', pad=20)
    plt.xticks(x, df['Model'], fontsize=12, fontweight='bold')
    
    # Y Eksenini 85-100 arasına sabitleme (farkların daha net görülmesi için)
    plt.ylim(85, 100)
    plt.legend(loc='lower right', fontsize=12)
    
    # Barların üzerine değerleri yazdırma
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "academic_performance_comparison.png"), dpi=300)
    plt.close()
    
    # -------------------------------------------------------------------------
    # Grafik 2: crisis_missed_tweets_rate.png
    # -------------------------------------------------------------------------
    print("2. crisis_missed_tweets_rate.png üretiliyor...")
    # (100 - Recall) hesabı: Gözden kaçırılan (Hayata mal olabilecek) kriz tweetlerinin oranı
    df['Missed_Rate'] = 100.0 - df['Crisis Recall_val']
    df_sorted = df.sort_values(by='Missed_Rate', ascending=False)
    
    plt.figure(figsize=(12, 6))
    
    # Reds_r (Ters Kırmızı Gradyan) ile görselleştirme
    norm = plt.Normalize(df_sorted['Missed_Rate'].min(), df_sorted['Missed_Rate'].max())
    sm = plt.cm.ScalarMappable(cmap="Reds_r", norm=norm)
    colors = [sm.to_rgba(val) for val in df_sorted['Missed_Rate']]
    
    bars = plt.barh(df_sorted['Model'], df_sorted['Missed_Rate'], color=colors, edgecolor='black', height=0.6)
    
    plt.xlabel('Gözden Kaçırılan Kriz Tweetleri Oranı (%) [100 - Recall]', fontsize=14, fontweight='bold')
    plt.title('Modellerin Kriz Anındaki Hata (Missed) Oranları', fontsize=16, fontweight='bold', color='darkred', pad=15)
    plt.yticks(fontsize=12, fontweight='bold')
    
    # Değerleri barların sağına yazma
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.15, bar.get_y() + bar.get_height()/2, f"%{width:.2f}", 
                 va='center', ha='left', fontsize=12, fontweight='bold')
                 
    plt.xlim(0, max(df_sorted['Missed_Rate']) + 2)
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "crisis_missed_tweets_rate.png"), dpi=300)
    plt.close()
    
    # -------------------------------------------------------------------------
    # Grafik 3: accuracy_vs_recall_tradeoff.png
    # -------------------------------------------------------------------------
    print("3. accuracy_vs_recall_tradeoff.png üretiliyor...")
    plt.figure(figsize=(10, 8))
    
    # Modelleri özel ikonlar ve renklerle dağılım tablosuna yerleştir
    colors_map = ['blue', 'purple', 'gray', 'red']
    markers = ['o', 's', '^', '*']
    
    for i, row in df.iterrows():
        is_bert = 'BERTurk' in row['Model']
        size = 600 if is_bert else 300
        edge = 'black'
        linewidth = 2 if is_bert else 1
        alpha = 1.0 if is_bert else 0.8
        
        plt.scatter(row['Accuracy_val'], row['Crisis Recall_val'], 
                    s=size, color=colors_map[i%len(colors_map)], marker=markers[i%len(markers)], 
                    label=row['Model'], edgecolor=edge, linewidth=linewidth, alpha=alpha)
        
        # Noktaların ismini yazdır
        offset_y = 0.3 if not is_bert else -0.5
        plt.annotate(row['Model'], 
                     (row['Accuracy_val'], row['Crisis Recall_val']),
                     xytext=(0, 15 if not is_bert else -25), textcoords='offset points', 
                     ha='center', fontsize=12, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7))
                     
    plt.xlabel('Genel Doğruluk - Accuracy (%)', fontsize=14, fontweight='bold')
    plt.ylabel('Kriz Duyarlılığı - Recall (%)', fontsize=14, fontweight='bold')
    plt.title('Accuracy vs. Crisis Recall Ödünleşim (Trade-off) Grafiği', fontsize=16, fontweight='bold', pad=20)
    
    plt.legend(loc='lower left', fontsize=11, markerscale=0.7, title='Modeller', title_fontsize=12)
    
    # Eksenleri daraltıp farkları vurgula
    plt.xlim(df['Accuracy_val'].min() - 1, df['Accuracy_val'].max() + 1.5)
    plt.ylim(df['Crisis Recall_val'].min() - 1, df['Crisis Recall_val'].max() + 1.5)
    
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "accuracy_vs_recall_tradeoff.png"), dpi=300)
    plt.close()
    
    print("Tüm akademik görseller (300 DPI) başarıyla oluşturuldu!")

if __name__ == "__main__":
    main()
