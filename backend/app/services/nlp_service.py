import sys
from pathlib import Path
import joblib

# Add project root to path to import our custom ML modules
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from ml.preprocessing.text_cleaner import preprocess_batch
from ml.inference.similarity_engine import SimilarityEngine
from ml.inference.nli_engine import NLIEngine
from ml.rules.refinement_engine import RefinementEngine

class NLPService:
    def __init__(self, classifier_path: str, similarity_threshold: float = 0.71):
        print("🔄 Loading AI Models into memory...")
        
        # 1. Load Custom Classifier
        self.classifier = joblib.load(classifier_path)
        print("✅ Classifier loaded.")
        
        # 2. Load Pre-trained Engines
        self.similarity_engine = SimilarityEngine()
        self.nli_engine = NLIEngine()
        self.refinement_engine = RefinementEngine()
        
        # 3. Store the threshold for later use
        self.similarity_threshold = similarity_threshold
        
        print("🚀 All AI models loaded successfully!")

    def analyze_requirement(self, text: str) -> dict:
        # A. Classification (using preprocessed text since the model was trained on it)
        processed_text = preprocess_batch([text])[0]
        
        prediction = self.classifier.predict([processed_text])[0]
        probabilities = self.classifier.predict_proba([processed_text])[0]
        confidence = float(max(probabilities))
        
        # B. Rule-based Refinement & Ambiguity Detection
        refinement_result = self.refinement_engine.analyze_and_refine(text)
        
        # C. Simple Quality Score Calculation (0-100)
                # C. Simple Quality Score Calculation (0-100)
        score = 100.0
        
        # Penalize based on clarity label
        if prediction in ["INCOMPLETE", "NON_TESTABLE"]:
            score -= 40  # Big penalty for incomplete/non-testable
        elif prediction == "AMBIGUOUS":
            score -= 20
            
        # Additional penalty for detected issues
        for issue in refinement_result["issues"]:
            if issue["severity"] == "High":
                score -= 15
            elif issue["severity"] == "Medium":
                score -= 10
        
        score = max(0.0, score)
        
        return {
            "clarity_label": prediction,
            "confidence_score": round(confidence, 4),
            "quality_score": round(score, 2),
            "is_ambiguous": refinement_result["is_ambiguous"],
            "issues": refinement_result["issues"],
            "suggested_refinement": refinement_result["suggested_refinement"]
        }

    def refine_requirement(self, text: str, values: list) -> dict:
        issues = self.refinement_engine.analyze_and_refine(text)["issues"]
        if not issues:
            return {"refined_text": text, "filled_templates": []}
        if len(values) != len(issues):
            raise ValueError(f"Expected {len(issues)} values (one per issue), got {len(values)}.")

        system_noun = self.refinement_engine.extract_system_noun(text)
        filled = []
        for issue, value in zip(issues, values):
            t = (issue["template"]
                 .replace("{system}", system_noun)
                 .replace("[VALUE]", str(value).strip())
                 .replace("[TASK]", "the primary task"))
            filled.append(t.rstrip("."))

        prefix = f"The {system_noun} shall "
        bodies, extras = [], []
        for t in filled:
            if t.startswith(prefix):
                bodies.append(t[len(prefix):])
            else:
                extras.append(t + ".")
        refined = (prefix + " and ".join(bodies) + ".") if bodies else ""
        refined = (refined + " " + " ".join(extras)).strip()
        return {"refined_text": refined, "filled_templates": [f + "." for f in filled]}

    def compare_similarity(self, text_a: str, text_b: str) -> dict:
        score = float(self.similarity_engine.compute_batch_similarity([text_a], [text_b])[0])
        if score >= self.similarity_threshold:
            classification = "Duplicate"
        elif score >= self.similarity_threshold - 0.15:
            classification = "Similar"
        else:
            classification = "Unrelated"
        return {
            "similarity_score": round(score, 4),
            "classification": classification,
            "threshold_used": self.similarity_threshold,
        }

    def check_contradiction(self, text_a: str, text_b: str) -> dict:
        return self.nli_engine.predict_batch([(text_a, text_b)])[0]

# Global instance will be initialized in main.py lifespan
nlp_service: NLPService = None