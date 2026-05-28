import pandas as pd
import numpy as np
import torch
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    print("Veriler yükleniyor ve hazırlanıyor...")
    
    # 1. Veri Yükleme ve Hazırlık
    train_df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "train_set.csv"), encoding='utf-8-sig')
    test_df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "test_set.csv"), encoding='utf-8-sig')
    
    # label sütunundaki 'crisis' değerlerini 1, 'noise' değerlerini 0 olarak map et
    label_map = {'crisis': 1, 'noise': 0}
    train_df['label'] = train_df['label'].map(label_map)
    test_df['label'] = test_df['label'].map(label_map)
    
    # Metinlerin string formatında olduğundan ve NaN olmadığından emin ol
    train_df['text'] = train_df['text'].astype(str)
    test_df['text'] = test_df['text'].astype(str)
    train_df = train_df.dropna(subset=['text', 'label'])
    test_df = test_df.dropna(subset=['text', 'label'])
    
    # Pandas DataFrame'i Hugging Face Dataset formatına çevir
    train_dataset = Dataset.from_pandas(train_df[['text', 'label']])
    test_dataset = Dataset.from_pandas(test_df[['text', 'label']])
    
    # Tokenizer
    model_name = "dbmdz/bert-base-turkish-cased"
    print(f"Tokenizer yükleniyor: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True, max_length=128)
        
    print("Tokenization işlemi yapılıyor...")
    train_tokenized = train_dataset.map(tokenize_function, batched=True)
    test_tokenized = test_dataset.map(tokenize_function, batched=True)
    
    # PyTorch formatına hazırla
    train_tokenized = train_tokenized.remove_columns(["text"])
    test_tokenized = test_tokenized.remove_columns(["text"])
    train_tokenized.set_format("torch")
    test_tokenized.set_format("torch")
    
    # Model Yükleme
    print(f"Model yükleniyor: {model_name}")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    # 2. Hiperparametreler
    training_args = TrainingArguments(
        output_dir=os.path.join(WORKSPACE, "outputs", "results"),
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        logging_dir=os.path.join(WORKSPACE, "outputs", "logs"),
        load_best_model_at_end=True,
    )
    
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return {"accuracy": (predictions == labels).mean()}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=test_tokenized,
        compute_metrics=compute_metrics,
    )
    
    print("Eğitim (Fine-Tuning) başlıyor...")
    trainer.train()
    
    # 3. Grafik Üretimi (Sunum İçin - Loss Curve)
    print("Eğitim tamamlandı. Grafikler oluşturuluyor...")
    log_history = trainer.state.log_history
    
    epoch_logs = {}
    for log in log_history:
        ep = round(log.get('epoch', 0), 2)
        if ep == 0: continue
        if ep not in epoch_logs:
            epoch_logs[ep] = {}
        if 'loss' in log:
            epoch_logs[ep]['train_loss'] = log['loss']
        if 'eval_loss' in log:
            epoch_logs[ep]['eval_loss'] = log['eval_loss']
            
    plot_epochs = sorted([e for e in epoch_logs.keys() if 'train_loss' in epoch_logs[e] or 'eval_loss' in epoch_logs[e]])
    t_loss = [epoch_logs[e].get('train_loss', None) for e in plot_epochs]
    v_loss = [epoch_logs[e].get('eval_loss', None) for e in plot_epochs]
    
    plt.figure(figsize=(10, 6))
    if any(t is not None for t in t_loss):
        plt.plot(plot_epochs, t_loss, label='Training Loss', marker='o')
    if any(v is not None for v in v_loss):
        plt.plot(plot_epochs, v_loss, label='Validation Loss', marker='s')
    
    plt.title('Training and Validation Loss per Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.xticks(plot_epochs)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "loss_curve.png"), dpi=300)
    plt.close()
    print("loss_curve.png başarıyla kaydedildi.")
    
    # 4. Akademik Raporlama: Tahminleme ve Metrikler
    print("Test seti üzerinde nihai tahminleme yapılıyor...")
    predictions = trainer.predict(test_tokenized)
    preds = np.argmax(predictions.predictions, axis=-1)
    true_labels = predictions.label_ids
    
    print("\n" + "="*60)
    print("SINIFLANDIRMA RAPORU (Classification Report)")
    print("="*60)
    report = classification_report(true_labels, preds, target_names=['Noise (0)', 'Crisis (1)'], digits=4)
    print(report)
    print("="*60 + "\n")
    
    # Karmaşıklık Matrisi (Confusion Matrix)
    cm = confusion_matrix(true_labels, preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Noise (0)', 'Crisis (1)'], 
                yticklabels=['Noise (0)', 'Crisis (1)'],
                annot_kws={"size": 14})
    plt.title('Confusion Matrix', fontsize=16)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(WORKSPACE, "outputs", "plots", "confusion_matrix.png"), dpi=300)
    plt.close()
    
    print("confusion_matrix.png başarıyla kaydedildi.")
    print("Tüm işlemler başarıyla tamamlandı. Model ve metrikler sunuma hazır!")

if __name__ == "__main__":
    main()
