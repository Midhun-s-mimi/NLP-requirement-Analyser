import sys
import traceback

print("=" * 50)
print("STARTING IMPORT TEST")
print("=" * 50)

try:
    print("1. Testing config import...")
    from app.core.config import settings
    print("✅ Config OK")
except Exception as e:
    print(f" Config FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Testing database import...")
    from app.db.database import engine
    print("✅ Database OK")
except Exception as e:
    print(f" Database FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Testing models import...")
    from app.db import models
    print("✅ Models OK")
except Exception as e:
    print(f"❌ Models FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Testing schemas import...")
    from app.schemas.requirement import AnalysisRequest
    print("✅ Schemas OK")
except Exception as e:
    print(f"❌ Schemas FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. Testing NLP service import (this might take time)...")
    from app.services.nlp_service import NLPService
    print("✅ NLP Service OK")
except Exception as e:
    print(f" NLP Service FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("6. Testing main app import...")
    from app.main import app
    print("✅ Main App OK")
except Exception as e:
    print(f"❌ Main App FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

print("=" * 50)
print("ALL IMPORTS SUCCESSFUL!")
print("=" * 50)