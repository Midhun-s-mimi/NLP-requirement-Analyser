from transformers import pipeline

class NLIEngine:
    def __init__(self, model_name="cross-encoder/nli-deberta-v3-small"):
        print(f"Loading NLI model: {model_name}...")
        # top_k=None returns scores for all labels
        self.classifier = pipeline("text-classification", model=model_name, top_k=None, device=-1)
        print("✅ NLI model loaded.")
        
    def predict_batch(self, pairs: list) -> list:
        """
        Predicts NLI labels for a batch of (premise, hypothesis) pairs.
        Returns a list of dicts: [{'label': 'contradiction', 'confidence': 0.95}, ...]
        """
        # Format for HF pipeline NLI
        formatted_pairs = [{"text": p[0], "text_pair": p[1]} for p in pairs]
        raw_results = self.classifier(formatted_pairs)
        
        label_map = {
            "CONTRADICTION": "contradiction",
            "ENTAILMENT": "entailment",
            "NEUTRAL": "neutral"
        }
        
        final_results = []
        for result_list in raw_results:
            best_label = None
            best_score = -1.0
            
            for item in result_list:
                label = label_map.get(item['label'].upper(), item['label'].lower())
                if item['score'] > best_score:
                    best_score = item['score']
                    best_label = label
                    
            final_results.append({"label": best_label, "confidence": float(best_score)})
            
        return final_results