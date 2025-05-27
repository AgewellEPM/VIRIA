import json
import os
from datetime import datetime

MEMORY_PATH = "loopmemory.json"
PREDICTION_LOG = "ritual_predictions.json"

# Thresholds for prediction scoring
PREDICT_THRESHOLD = 2.5  # loop energy level
FREQUENCY_WEIGHT = 1.5
RECENCY_WEIGHT = 1.0

class RitualPredictor:
    def __init__(self):
        self.memory = self._load_memory()
        self.predictions = []

    def _load_memory(self):
        if not os.path.exists(MEMORY_PATH):
            print("[⚠️] loopmemory.json not found.")
            return {}
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)

    def predict_ritual_candidates(self):
        loops = self.memory.get("loops", {})
        candidates = []

        for phrase, data in loops.items():
            count = data.get("count", 0)
            energy = data.get("loop_energy", 0.0)
            last_used = data.get("last_used", "unknown")
            ritualized = data.get("ritualized", False)

            if ritualized:
                continue  # already promoted

            # Scoring system: loop energy × freq weight + recent use bias
            score = energy * FREQUENCY_WEIGHT

            # Recency bonus: if used in the last 1 hour
            try:
                time_diff = datetime.now() - datetime.fromisoformat(last_used)
                if time_diff.total_seconds() < 3600:
                    score
