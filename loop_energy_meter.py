import json
import os
from datetime import datetime

LOOPMEMORY_PATH = "loopmemory.json"
ENERGY_LOG_PATH = "loop_energy_log.json"

class LoopEnergyMeter:
    def __init__(self):
        self.memory = self._load_memory()
        self.energy_log = []

    def _load_memory(self):
        if os.path.exists(LOOPMEMORY_PATH):
            with open(LOOPMEMORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def _save_energy_log(self):
        with open(ENERGY_LOG_PATH, "w") as f:
            json.dump(self.energy_log[-100:], f, indent=2)

    def analyze_energy(self):
        loops = self.memory.get("loops", {})
        reactions = self.memory.get("reactions", [])[-20:]

        total_energy = 0
        overload_loops = []
        dominant_phrases = []

        for phrase, data in loops.items():
            energy = data.get("loop_energy", 0.0)
            total_energy += energy
            if energy >= 1.0:
                overload_loops.append((phrase, energy))
            if data.get("count", 0) >= 5:
                dominant_phrases.append(phrase)

        emotional_bias = self._analyze_emotional_pressure(reactions)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_loop_energy": round(total_energy, 2),
            "overload_loops": overload_loops,
            "dominant_phrases": dominant_phrases,
            "emotional_pressure": emotional_bias
        }

        self.energy_log.append(summary)
        self._save_energy_log()

        print("\n[🔋 Loop Energy Report]")
        print(f"• Total Energy: {summary['total_loop_energy']}")
        print(f"• Overloaded Loops: {[p for p, e in overload_loops]}")
        print(f"• Dominant Phrases: {dominant_phrases}")
        print(f"• Emotional Pressure: {emotional_bias}")

        return summary

    def _analyze_emotional_pressure(self, reactions):
        count = {}
        for r in reactions:
            emo = r.get("emotion", "unknown")
            count[emo] = count.get(emo, 0) + 1
        if not count:
            return "neutral"
        return max(count, key=count.get)

# --- Example standalone runner ---
if __name__ == "__main__":
    meter = LoopEnergyMeter()
    meter.analyze_energy()
