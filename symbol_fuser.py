import json
import os
from datetime import datetime
from itertools import combinations

MEMORY_PATH = "loopmemory.json"
FUSION_LOG_PATH = "symbol_fusions.json"

class SymbolFuser:
    def __init__(self):
        self.memory = self._load_memory()
        self.fusions = []

    def _load_memory(self):
        if not os.path.exists(MEMORY_PATH):
            print("[⚠️] loopmemory.json not found.")
            return {}
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)

    def detect_fusion_candidates(self):
        rituals = self.memory.get("rituals", [])
        pairs = list(combinations(rituals, 2))
        candidates = []

        for r1, r2 in pairs:
            score = self._fusion_score(r1, r2)
            if score >= 0.6:
                fusion_name = f"{r1['name']}_{r2['name']}_fused"
                candidates.append({
                    "fusion_name": fusion_name,
                    "components": [r1["name"], r2["name"]],
                    "score": round(score, 2),
                    "last_triggered": max(r1.get("last_triggered", ""), r2.get("last_triggered", ""))
                })

        self.fusions = sorted(candidates, key=lambda x: x["score"], reverse=True)
        return self.fusions

    def _fusion_score(self, r1, r2):
        # Similarity scoring based on:
        # 1. Shared trigger phrase fragment
        # 2. Emotional proximity via ritual names
        # 3. Usage count similarity

        trigger_match = 0
        if isinstance(r1["trigger"], str) and isinstance(r2["trigger"], str):
            if any(word in r2["trigger"] for word in r1["trigger"].split()):
                trigger_match = 0.4

        name_overlap = 0.2 if any(w in r2["name"] for w in r1["name"].split("_")) else 0.0

        usage_diff = abs(r1.get("usage_count", 0) - r2.get("usage_count", 0))
        usage_score = max(0.2 - (usage_diff * 0.02), 0)

        return trigger_match + name_overlap + usage_score

    def save_fusions(self):
        with open(FUSION_LOG_PATH, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "fusions": self.fusions
            }, f, indent=2)
        print(f"[🔗] Symbolic fusions saved to {FUSION_LOG_PATH}")

    def print_fusions(self):
        if not self.fusions:
            print("\n[🧩] No viable symbolic fusions found.")
            return

        print("\n[🔗 Symbolic Fusion Proposals]")
        for fusion in self.fusions:
            print(f"• {fusion['fusion_name']} ← [{', '.join(fusion['components'])}] (Score: {fusion['score']})")

# --- Example usage ---
if __name__ == "__main__":
    fuser = SymbolFuser()
    results = fuser.detect_fusion_candidates()
    fuser.print_fusions()
    fuser.save_fusions()
