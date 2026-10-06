import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.metrics import classification_report, f1_score

sys.path.append(str(Path(__file__).resolve().parent.parent))
from inference.similarity_engine import SimilarityEngine
from inference.nli_engine import NLIEngine

def evaluate_similarity(df, engine):
    print("\n--- Evaluating Semantic Similarity Engine ---")
    texts_a = df['requirement_a'].tolist()
    texts_b = df['requirement_b'].tolist()
    
    # Compute similarities
    similarities = engine.compute_batch_similarity(texts_a, texts_b)
    df['similarity_score'] = similarities
    
    # Binary classification: Is it a Duplicate or Not?
    y_true_binary = (df['relationship'] == 'Duplicate').astype(int)
    
    # Experimental Threshold Tuning
    print("Tuning similarity threshold...")
    best_threshold = 0.5
    best_f1 = 0.0
    
    for threshold in np.arange(0.50, 0.95, 0.01):
        y_pred_binary = (similarities >= threshold).astype(int)
        current_f1 = f1_score(y_true_binary, y_pred_binary, zero_division=0)
        if current_f1 > best_f1:
            best_f1 = current_f1
            best_threshold = threshold
            
    print(f"✅ Optimal Similarity Threshold: {best_threshold:.2f} (F1: {best_f1:.4f})")
    
    # Final report with optimal threshold
    y_pred_optimal = (similarities >= best_threshold).astype(int)
    print("\nSimilarity Classification Report (Duplicate vs Non-Duplicate):")
    print(classification_report(y_true_binary, y_pred_optimal, target_names=['Non-Duplicate', 'Duplicate']))
    
    return best_threshold

def evaluate_nli(df, engine):
    print("\n--- Evaluating Contradiction (NLI) Engine ---")
    pairs = list(zip(df['requirement_a'].tolist(), df['requirement_b'].tolist()))
    
    # Predict
    predictions = engine.predict_batch(pairs)
    
    df['nli_label'] = [p['label'] for p in predictions]
    df['nli_confidence'] = [p['confidence'] for p in predictions]
    
    # Map our ground truth to NLI labels for evaluation
    # Duplicate/Similar -> entailment/neutral (mostly neutral)
    # Contradictory -> contradiction
    # Neutral -> neutral
    y_true_nli = []
    for rel in df['relationship']:
        if rel == 'Contradictory':
            y_true_nli.append('contradiction')
        else:
            y_true_nli.append('neutral') # Simplifying for the 3-class NLI evaluation
            
    y_pred_nli = df['nli_label'].tolist()
    
    print("\nNLI Classification Report:")
    print(classification_report(y_true_nli, y_pred_nli, labels=['contradiction', 'neutral', 'entailment']))

if __name__ == "__main__":
    data_path = "data/synthetic/pairwise_requirements.csv"
    df = pd.read_csv(data_path)
    
    # Initialize engines (This will download the models on first run)
    sim_engine = SimilarityEngine()
    nli_engine = NLIEngine()
    
    # Evaluate
    optimal_threshold = evaluate_similarity(df, sim_engine)
    evaluate_nli(df, nli_engine)
    
    print("\n✅ Pairwise Evaluation Complete.")
    print(f"Note the optimal similarity threshold ({optimal_threshold:.2f}) for use in the backend API.")