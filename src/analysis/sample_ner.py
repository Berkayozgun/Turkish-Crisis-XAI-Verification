import pandas as pd
import json
import os
from transformers import pipeline

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def extract_locs(ner_results):
    locs = []
    current_entity = []
    for entity in ner_results:
        if entity['entity'].startswith('B-LOC'):
            if current_entity:
                locs.append(" ".join(current_entity))
            current_entity = [entity['word'].replace('##', '')]
        elif entity['entity'].startswith('I-LOC'):
            if current_entity:
                if entity['word'].startswith('##'):
                    current_entity[-1] += entity['word'].replace('##', '')
                else:
                    current_entity.append(entity['word'])
    if current_entity:
        locs.append(" ".join(current_entity))
    return list(set(locs))

def main():
    print("Veri yükleniyor...")
    df = pd.read_csv(os.path.join(WORKSPACE, "data", "processed", "test_set.csv"), encoding="utf-8-sig")
    
    # Kriz verilerini filtrele
    crisis_df = df[df['label'] == 'crisis'].copy()
    
    # 200 rastgele tweet seç
    sampled_df = crisis_df.sample(n=200, random_state=42)
    
    print("NER Modeli yükleniyor...")
    ner_pipeline = pipeline("ner", model="savasy/bert-base-turkish-ner-cased", tokenizer="savasy/bert-base-turkish-ner-cased")
    
    results = []
    
    for i, row in sampled_df.iterrows():
        text = str(row['text'])
        ner_res = ner_pipeline(text)
        locs = extract_locs(ner_res)
        results.append({
            "id": i,
            "text": text,
            "model_locs": locs
        })
        
    output_path = os.path.join(WORKSPACE, "outputs", "reports", "ner_evaluation_sample.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"200 tweet NER'den geçirildi ve {output_path} konumuna kaydedildi.")

if __name__ == "__main__":
    main()
