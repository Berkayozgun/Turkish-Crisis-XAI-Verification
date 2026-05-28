import pandas as pd
import numpy as np
import time
import os
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Boşlukları temizleme (fazla boşlukları tek boşluğa indirme)
    return " ".join(text.split())

def main():
    print("1. Veri yükleniyor ve vektörizasyon işlemi başlatılıyor...")
    train_df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "train_set.csv"), encoding='utf-8-sig')
    test_df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "test_set.csv"), encoding='utf-8-sig')
    
    # Boşlukları temizle
    train_df['text'] = train_df['text'].apply(clean_text)
    test_df['text'] = test_df['text'].apply(clean_text)
    
    # Label mapping ('crisis' -> 1, 'noise' -> 0)
    if 'noise' in train_df['label'].values or 'crisis' in train_df['label'].values:
        label_map = {'crisis': 1, 'noise': 0}
        train_df['label'] = train_df['label'].map(label_map).fillna(train_df['label'])
        test_df['label'] = test_df['label'].map(label_map).fillna(test_df['label'])
    
    train_df = train_df.dropna(subset=['text', 'label'])
    test_df = test_df.dropna(subset=['text', 'label'])
    
    X_train = train_df['text']
    y_train = train_df['label'].astype(int)
    X_test = test_df['text']
    y_test = test_df['label'].astype(int)
    
    # Vektörizasyon: TF-IDF (Unigram ve Bigram, 10000 özellik)
    print("-> TF-IDF dönüştürücüsü (ngram_range=(1,2), max_features=10000) çalıştırılıyor...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"-> Eğitim Seti Vektör Boyutu: {X_train_vec.shape}, Test Seti Vektör Boyutu: {X_test_vec.shape}\n")
    
    # 2. Modeller ve GridSearchCV Optimizasyon Uzayları
    models_configs = {
        "Logistic Regression": {
            "estimator": LogisticRegression(solver='saga', class_weight='balanced', random_state=42, max_iter=500),
            "param_grid": {
                "C": [0.1, 1, 10],
                "penalty": ['l1', 'l2']
            }
        },
        "Linear SVM": {
            "estimator": LinearSVC(class_weight='balanced', random_state=42, max_iter=1000),
            "param_grid": {
                "C": [0.1, 1, 10],
                "loss": ['hinge', 'squared_hinge']
            }
        },
        "Random Forest": {
            "estimator": RandomForestClassifier(class_weight='balanced', random_state=42),
            "param_grid": {
                "n_estimators": [100, 200],
                "max_depth": [10, 20, None]
            }
        }
    }
    
    results = []
    
    print("2. Makine Öğrenmesi Modelleri Eğitiliyor ve GridSearch Optimizasyonu (cv=3, n_jobs=-1)...")
    for model_name, config in models_configs.items():
        print(f"\n[{model_name}] aranıyor...")
        start_time = time.time()
        
        grid_search = GridSearchCV(
            estimator=config["estimator"],
            param_grid=config["param_grid"],
            cv=3,
            scoring='f1_macro',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train_vec, y_train)
        
        best_model = grid_search.best_estimator_
        print(f"-> En iyi parametreler: {grid_search.best_params_}")
        
        # Test Setinde Tahminleme
        preds = best_model.predict(X_test_vec)
        
        # Sadece Kriz Sınıfı (Label = 1) için metrikler
        acc = accuracy_score(y_test, preds)
        crisis_f1 = f1_score(y_test, preds, pos_label=1)
        crisis_recall = recall_score(y_test, preds, pos_label=1)
        
        elapsed = time.time() - start_time
        print(f"-> {model_name} optimizasyon süresi: {elapsed:.2f} saniye")
        
        results.append({
            "Model": model_name,
            "Best Parameters": str(grid_search.best_params_),
            "Accuracy": acc,
            "Crisis F1-Score": crisis_f1,
            "Crisis Recall": crisis_recall
        })
    
    # 3. Buluttaki BERTurk Sonuçları ile Birleştirme
    results.append({
        "Model": "BERTurk (Cloud Baseline)",
        "Best Parameters": "Pre-trained + Fine-Tuned",
        "Accuracy": 0.9600,
        "Crisis F1-Score": 0.9300,
        "Crisis Recall": 0.9400
    })
    
    df_results = pd.DataFrame(results)
    
    # 4. Çıktı Yönetimi: Akademik Tablo Formatlama
    df_results_formatted = df_results.copy()
    df_results_formatted['Accuracy'] = (df_results_formatted['Accuracy'] * 100).round(2).astype(str) + '%'
    df_results_formatted['Crisis F1-Score'] = (df_results_formatted['Crisis F1-Score'] * 100).round(2).astype(str) + '%'
    df_results_formatted['Crisis Recall'] = (df_results_formatted['Crisis Recall'] * 100).round(2).astype(str) + '%'
    
    print("\n" + "="*110)
    print("NİHAİ MODEL KARŞILAŞTIRMA TABLOSU (TEST SETİ PERFORMANSI)")
    print("="*110)
    print(df_results_formatted.to_string(index=False))
    print("="*110)
    
    # Diske CSV olarak kaydet (İşlenmemiş float değerlerle kaydetmek analiz için daha iyi olur, formatlısını da kaydedebiliriz)
    out_path = os.path.join(WORKSPACE, "outputs", "reports", "final_model_comparison.csv")
    df_results_formatted.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"\nAkademik Karşılaştırma Tablosu başarıyla kaydedildi: {out_path}")

if __name__ == "__main__":
    main()
