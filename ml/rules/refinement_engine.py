import re
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.append(str(Path(__file__).resolve().parent.parent))
from rules.ambiguity_lexicon import AMBIGUITY_LEXICON


class RefinementEngine:
    def __init__(self):
        self.patterns = {
            word: re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
            for word in AMBIGUITY_LEXICON.keys()
        }

    @staticmethod
    def extract_system_noun(text: str) -> str:
        """Extracts the noun after 'The' (e.g., 'application' from 'The application...')"""
        match = re.search(r"^[Tt]he\s+(\w+)", text)
        return match.group(1) if match else "system"

    def analyze_and_refine(self, requirement_text: str) -> Dict[str, Any]:
        detected_issues = []
        for word, pattern in self.patterns.items():
            match = pattern.search(requirement_text)
            if match:
                entry = AMBIGUITY_LEXICON[word]
                detected_issues.append({
                    "matched_phrase": match.group(),
                    "category": entry["category"],
                    "severity": entry["severity"],
                    "question": entry["question"],
                    "unit": entry["unit"],
                    "template": entry["template"],
                })

        refined_text = requirement_text
        if detected_issues:
            system_noun = self.extract_system_noun(requirement_text)
            primary = detected_issues[0]
            # Replace placeholders in the template
            refined_text = (primary["template"]
                            .replace("{system}", system_noun)
                            .replace("[VALUE]", f"**[{primary['unit'].upper()}]**"))

        return {
            "original_text": requirement_text,
            "is_ambiguous": len(detected_issues) > 0,
            "issues": detected_issues,
            "suggested_refinement": refined_text,
            "status": "needs_review" if detected_issues else "approved",
        }


if __name__ == "__main__":
    engine = RefinementEngine()
    result = engine.analyze_and_refine("The application should respond quickly and support many users.")
    print("Refinement:", result["suggested_refinement"])