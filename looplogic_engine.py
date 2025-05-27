import json
import time
from datetime import datetime
from collections import defaultdict

# File path to persistent memory
MEMORY_PATH = "loopmemory.json"
LOOPTRACE_PATH = "looptrace.json"

class LoopLogicEngine:
    def __init__(self):
        self.memory = self._load_json(MEMORY_PATH)
        self.looptrace = self._load_json(LOOPTRACE_PATH)
        self.loop_counts = defaultdict(int)

    def _load_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def register_phrase(self, phrase):
        timestamp = datetime.now().isoformat()
        self.looptrace.setdefault("phrases", []).append({"phrase": phrase, "time": timestamp})

        # Track counts
        self.loop_counts[phrase] += 1
        count = self.loop_counts[phrase]

        # Store in memory
        self.memory.setdefault("loops", {})
        self.memory["loops"].setdefault(phrase, {
            "count": 0,
            "last_used": None,
            "importance": "low",
            "loop_energy": 0.0,
            "ritualized": False
        })

        loop_entry = self.memory["loops"][phrase]
        loop_entry["count"] += 1
        loop_entry["last_used"] = timestamp
        loop_entry["loop_energy"] += self._calculate_energy(loop_entry["count"])
        
        # If passed threshold → mark as ritual
        if not loop_entry["ritualized"] and loop_entry["count"] >= 3:
            loop_entry["ritualized"] = True
            print(f"[🔁 Ritual Candidate Detected] → '{phrase}' has looped {loop_entry['count']} times.")
            self._promote_to_ritual(phrase)

        self._save_json(MEMORY_PATH, self.memory)
        self._save_json(LOOPTRACE_PATH, self.looptrace)

    def _calculate_energy(self, count):
        # Very basic loop energy formula (can evolve)
        return min(1.0, count * 0.2)

    def _promote_to_ritual(self, phrase):
        # Connect to ritual engine to formally add the ritual
        from ritual_core import RitualCore

        ritual_engine = RitualCore()
        ritual_names = [r.name for r in ritual_engine.rituals]
        ritual_name = f"looped_{phrase.replace(' ', '_')[:20]}"

        if ritual_name not in ritual_names:
            ritual_engine.add_ritual(
                name=ritual_name,
                trigger=phrase,
                effect=f"auto_effect:respond_to_{ritual_name}",
                importance="emergent"
            )
            print(f"[🌱 Ritual Formed] '{phrase}' promoted to '{ritual_name}'")

    def print_loops(self):
        print("\n[📈 Loop Summary]")
        for phrase, data in self.memory.get("loops", {}).items():
            print(f"• '{phrase}' → Count: {data['count']}, Energy: {round(data['loop_energy'], 2)}, Ritual: {data['ritualized']}")

# --- Example usage ---
if __name__ == "__main__":
    engine = LoopLogicEngine()
    while True:
        phrase = input("\nYou say (or type): ").strip()
        if phrase.lower() in ("quit", "exit"):
            break
        engine.register_phrase(phrase)
        engine.print_loops()
