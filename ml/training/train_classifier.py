import pandas as pd
import joblib
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.pipeline import Pipeline

# Add 'ml' directory to sys.path to allow importing the preprocessing module
sys.path.append(str(Path(__file__).resolve().parent.parent))
from preprocessing.text_cleaner import preprocess_batch

def load_and_prepare_data(data_path: str):
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # The CSV contains 'ClarityLabel.AMBIGUOUS'. We extract just 'AMBIGUOUS'
    df['label'] = df['clarity_label'].apply(lambda x: x.split('.')[-1])
    
    X = df['requirement_text'].tolist()
    y = df['label'].tolist()
    
    return X, y

def train_and_evaluate(X, y):
    # 1. Strict Data Splitting: 70% Train, 15% Val, 15% Test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )
    
    print(f"Data Split -> Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    
    # 2. Preprocess texts using our spaCy pipeline
    print("Preprocessing texts (Lemmatization, Stopword removal)...")
    X_train_clean = preprocess_batch(X_train)
    X_val_clean = preprocess_batch(X_val)
    X_test_clean = preprocess_batch(X_test)
    
    # 3. Define Baseline Models
    models = {
        "Logistic_Regression": LogisticRegression(max_iter=1000, random_state=42),
        "SVM_Linear": SVC(kernel='linear', probability=True, random_state=42)
    }
    
    results = {}
    best_model_name = None
    best_f1 = -1.0
    
    # 4. Train and Evaluate on Validation Set
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        
        # Create a pipeline: TF-IDF -> Classifier
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ('classifier', model)
        ])
        
        pipeline.fit(X_train_clean, y_train)
        
        # Evaluate on Validation set to pick the best model
        y_val_pred = pipeline.predict(X_val_clean)
        val_f1 = f1_score(y_val, y_val_pred, average='macro')
        print(f"Validation Macro F1-Score: {val_f1:.4f}")
        
        results[name] = {'pipeline': pipeline, 'val_f1': val_f1}
        
        if val_f1 > best_f1:
            best_f1 = val_f1
            best_model_name = name
            
    # 5. Final Evaluation on the Unseen Test Set
    print(f"\n--- Final Evaluation of Best Model ({best_model_name}) on Unseen Test Set ---")
    best_pipeline = results[best_model_name]['pipeline']
    y_test_pred = best_pipeline.predict(X_test_clean)
    
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_f1 = f1_score(y_test, y_test_pred, average='macro')
    
    print("\nTest Set Classification Report:")
    report_dict = classification_report(y_test, y_test_pred, output_dict=True)
    print(classification_report(y_test, y_test_pred))
    
    # 6. Save Experiment Metrics
    metrics = {
        "model_name": best_model_name,
        "timestamp": datetime.now().isoformat(),
        "test_accuracy": test_accuracy,
        "test_macro_f1": test_f1,
        "classification_report": report_dict
    }
    
    metrics_dir = Path("ml/experiments")
    metrics_dir.mkdir(parents=True, exist_ok=True)
    with open(metrics_dir / "classifier_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to ml/experiments/classifier_metrics.json")
    
    return best_pipeline, best_model_name

def save_model(pipeline, model_name):
    output_dir = Path("models/classifier")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = output_dir / f"{model_name}_pipeline.joblib"
    joblib.dump(pipeline, model_path)
    print(f"\n✅ Best model saved to: {model_path}")

if __name__ == "__main__":
    data_path = "data/synthetic/synthetic_requirements.csv"
    
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}. Please run generate_synthetic.py first.")
        sys.exit(1)
        
    X, y = load_and_prepare_data(data_path)
    best_pipeline, best_model_name = train_and_evaluate(X, y)
    save_model(best_pipeline, best_model_name)
    