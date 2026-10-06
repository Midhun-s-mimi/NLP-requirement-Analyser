import faulthandler, sys
faulthandler.enable()
# If the process HANGS, this prints the exact stuck line after 90 seconds
faulthandler.dump_traceback_later(90, exit=True)

def log(msg): print(msg, flush=True)

log("A: importing joblib...")
import joblib
log("A: OK")

log("B: importing similarity_engine...")
sys.path.append(r"C:\Users\Deepak\Documents\project_root")
from ml.inference.similarity_engine import SimilarityEngine
log("B: OK")

log("C: importing nli_engine...")
from ml.inference.nli_engine import NLIEngine
log("C: OK")

log("D: importing refinement_engine...")
from ml.rules.refinement_engine import RefinementEngine
log("D: OK")

log("ALL ML IMPORTS SUCCESSFUL")