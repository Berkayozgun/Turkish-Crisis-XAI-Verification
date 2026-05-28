import json
import os
import re

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    input_path = os.path.join(WORKSPACE, "outputs", "reports", "ner_evaluation_sample.json")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Kapsamlı lokasyon anahtar kelimeleri ve şehirler (Ground Truth simülasyonu)
    cities = [
        "adana", "adiyaman", "adıyaman", "afyon", "ağrı", "amasya", "ankara", "antalya", "artvin", "aydın", 
        "balıkesir", "bilecik", "bingöl", "bitlis", "bolu", "burdur", "bursa", "çanakkale", "çankırı", "çorum", 
        "denizli", "diyarbakır", "edirne", "elazığ", "erzincan", "erzurum", "eskişehir", "gaziantep", "giresun", 
        "gümüşhane", "hakkari", "hatay", "ısparta", "mersin", "istanbul", "izmir", "kars", "kastamonu", "kayseri", 
        "kırklareli", "kırşehir", "kocaeli", "konya", "kütahya", "malatya", "manisa", "kahramanmaraş", "maraş", "mardin", 
        "muğla", "muş", "nevşehir", "niğde", "ordu", "rize", "sakarya", "samsun", "siirt", "sinop", "sivas", "tekirdağ", 
        "tokat", "trabzon", "tunceli", "şanlıurfa", "urfa", "uşak", "van", "yozgat", "zonguldak", "aksaray", "bayburt", 
        "karaman", "kırıkkale", "batman", "şırnak", "bartın", "ardahan", "ığdır", "yalova", "karabük", "kilis", "osmaniye", "düzce",
        "iliç", "çorlu", "saraçhane", "boğaziçi", "marmaris", "pazarcık", "narlı"
    ]
    
    loc_keywords = ["il", "ilçe", "mahalle", "mah", "sokak", "sok", "cadde", "cad", "bulvar", "bulvarı", "apartmanı", "apt", "hastanesi", "yurdu", "otel", "oteli"]
    
    tp = 0
    fp = 0
    fn = 0
    
    tp_examples = []
    fn_examples = []
    
    for item in data:
        text_lower = item['text'].lower()
        
        # Ground Truth belirleme (Metinde şehir veya adres anahtar kelimesi geçiyor mu?)
        has_gt_loc = False
        
        # 1. Şehir veya özel ilçe kontrolü
        for c in cities:
            if re.search(r'\b' + re.escape(c) + r'\b', text_lower):
                has_gt_loc = True
                break
                
        # 2. Adres anahtar kelimesi kontrolü
        if not has_gt_loc:
            for k in loc_keywords:
                if re.search(r'\b' + re.escape(k) + r'\b', text_lower):
                    has_gt_loc = True
                    break
        
        # Modelin tahmini
        model_found_loc = len(item['model_locs']) > 0
        
        # Karşılaştırma
        if has_gt_loc and model_found_loc:
            tp += 1
            if len(tp_examples) < 2:
                tp_examples.append(item)
        elif not has_gt_loc and model_found_loc:
            fp += 1
        elif has_gt_loc and not model_found_loc:
            fn += 1
            if len(fn_examples) < 2:
                fn_examples.append(item)
                
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"TP: {tp}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall: {recall * 100:.2f}%")
    print(f"F1-Score: {f1 * 100:.2f}%")
    print("\n--- TP EXAMPLES ---")
    for ex in tp_examples:
        print(f"Text: {ex['text']}")
        print(f"Model Locs: {ex['model_locs']}")
    print("\n--- FN EXAMPLES ---")
    for ex in fn_examples:
        print(f"Text: {ex['text']}")
        print(f"Model Locs: {ex['model_locs']}")

if __name__ == "__main__":
    main()
