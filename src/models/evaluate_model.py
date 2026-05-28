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
    
    test_df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "test_set.csv"), encoding='utf-8-sig')
    label_map = {'crisis': 1, 'noise': 0}
    test_df['label'] = test_df['label'].map(label_map)
    test_df['text'] = test_df['text'].astype(str)
    test_df = test_df.dropna(subset=['text', 'label'])
    test_dataset = Dataset.from_pandas(test_df[['text', 'label']])
    
    model_name = "dbmdz/bert-base-turkish-cased"
    print(f"Tokenizer yükleniyor: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True, max_length=128)
        
    print("Tokenization işlemi yapılıyor...")
    test_tokenized = test_dataset.map(tokenize_function, batched=True)
    test_tokenized = test_tokenized.remove_columns(["text"])
    test_tokenized.set_format("torch")
    
    # En son kaydedilen checkpoint'i bul
    results_dir = os.path.join(WORKSPACE, "outputs", "results")
    checkpoints = [d for d in os.listdir(results_dir) if d.startswith("checkpoint-")]
    if not checkpoints:
        print("Checkpoint bulunamadı!")
        return
    best_checkpoint = sorted(checkpoints, key=lambda x: int(x.split("-")[1]))[-1]
    model_path = os.path.join(results_dir, best_checkpoint)
    
    print(f"Model yükleniyor: {model_path}")
    model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=2)
    
    training_args = TrainingArguments(
        output_dir=os.path.join(WORKSPACE, "outputs", "results"),
        per_device_eval_batch_size=16,
    )
    
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return {"accuracy": (predictions == labels).mean()}

    trainer = Trainer(
        model=model,
        args=training_args,
        eval_dataset=test_tokenized,
        compute_metrics=compute_metrics,
    )
    
    # Not: Loss curve log'ları Trainer'ın state log history'sinde bulunur.
    # Ancak yeniden yüklediğimizde log_history sıfırlanmış olabilir.
    # Bu script sadece confusion matrix ve classification report için kullanılacak.
    
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
