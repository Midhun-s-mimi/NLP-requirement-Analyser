import spacy
from typing import List

# Load the spaCy English model
# (Ensure you have downloaded it via: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def preprocess_batch(texts: List[str]) -> List[str]:
    """
    Processes a batch of texts for TF-IDF vectorization.
    - Lowercases (handled by spaCy implicitly via token attributes)
    - Lemmatizes (converts words to base form, e.g., 'running' -> 'run')
    - Removes punctuation, stop words, and spaces
    """
    cleaned_texts = []
    
    # nlp.pipe is highly optimized for batch processing.
    # We disable 'ner' and 'parser' to speed up processing since we only need lemmas.
    for doc in nlp.pipe(texts, disable=["ner", "parser"]):
        tokens = [
            token.lemma_ 
            for token in doc 
            if not token.is_punct and not token.is_stop and not token.is_space
        ]
        cleaned_texts.append(" ".join(tokens))
        
    return cleaned_texts