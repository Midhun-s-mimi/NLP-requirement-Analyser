from pydantic_settings import BaseSettings
from pathlib import Path

# Go up two levels from this file to reach project_root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "NLP Requirement Analyzer"
    VERSION: str = "1.0.0"
    
    # Database: SQLite for local dev, easily swappable to PostgreSQL
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/backend/app/db/requirements.db"
    
    # ML Model Paths
    CLASSIFIER_MODEL_PATH: str = str(BASE_DIR / "models" / "classifier" / "Logistic_Regression_pipeline.joblib")
    SIMILARITY_THRESHOLD: float = 0.71  # Experimentally determined!

    class Config:
        env_file = str(BASE_DIR / ".env")

settings = Settings()