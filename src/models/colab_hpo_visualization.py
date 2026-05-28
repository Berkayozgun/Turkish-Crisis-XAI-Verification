import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    print("HPO sonuçları görselleştiriliyor...")
    sns.set_theme(style="whitegrid")
    
    # 1. Validation Loss Karşılaştırması (En düşük daha iyi)
    # Deneylerin Final Epoch (Epoch 2) Validation Loss Değerleri
    experiments = [
        "Deney 1\n(LR: 2e-05, BS: 16)", 
        "Deney 2\n(LR: 3e-05, BS: 16)", 
        "Deney 3\n(LR: 5e-05, BS: 32)"
    ]
    val_losses = [0.020962, 0.025779, 0.015250]
    
    plt.figure(figsize=(10, 6))
    colors = ['#3498db', '#e74c3c', '#2ecc71'] # Deney 3 (en iyi) yeşil olsun
    bars = plt.bar(experiments, val_losses, color=colors, edgecolor='black', width=0.5)
    
    plt.ylabel('Final Validation Loss', fontsize=12, fontweight='bold')
    plt.title('HPO Deneyleri: Final Validation Loss Karşılaştırması (Düşük Daha İyi)', fontsize=14, fontweight='bold', pad=15)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.0005,
                 f'{height:.6f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
                 
    # Y eksenini daraltalım ki fark anlaşılsın
    plt.ylim(0.01, 0.03)
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "hpo_validation_loss_comparison.png"), dpi=300)
    plt.close()
    
    # 2. Learning Curves (Training vs Validation Loss over Epochs)
    epochs = [1, 2]
    
    # Deney 1
    t1_loss = [0.054135, 0.007566]
    v1_loss = [0.020766, 0.020962]
    
    # Deney 2
    t2_loss = [0.044120, 0.008090]
    v2_loss = [0.019667, 0.025779]
    
    # Deney 3
    # Deney 3'ün Epoch 1'de logu yok, ancak Epoch 2'de train loss 0.029624. Grafikte düzgün görünmesi için Epoch 1 train loss'u epoch 2 ile aynı hizaya yakın bir değer (veya none) alabiliriz.
    # Tahmini bir başlangıç atayalım (0.04 civarı) ya da sadece çizgi çizelim. NaN verelim ki plotta boşluk olsun.
    t3_loss = [np.nan, 0.029624] 
    v3_loss = [0.019417, 0.015250]
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    fig.suptitle('HPO Deneyleri: Eğitim ve Doğrulama (Loss) Eğrileri', fontsize=16, fontweight='bold', y=1.05)
    
    def plot_curve(ax, t_loss, v_loss, title):
        ax.plot(epochs, t_loss, marker='o', label='Train Loss', color='blue', linewidth=2, linestyle='--')
        ax.plot(epochs, v_loss, marker='s', label='Validation Loss', color='orange', linewidth=2)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Epoch', fontsize=11)
        ax.set_xticks([1, 2])
        ax.grid(True, linestyle=':', alpha=0.7)
        ax.legend()
        
    plot_curve(axes[0], t1_loss, v1_loss, "Deney 1 (Standart Alt Sınır)")
    plot_curve(axes[1], t2_loss, v2_loss, "Deney 2 (Optimal Bağlam)")
    plot_curve(axes[2], t3_loss, v3_loss, "Deney 3 (Agresif Hızlı Öğrenme)")
    
    axes[0].set_ylabel('Loss', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "hpo_learning_curves.png"), dpi=300)
    plt.close()
    
    print("Colab HPO grafikleri oluşturuldu!")

if __name__ == "__main__":
    main()
