import time
import random
from datetime import datetime
from attention_tracker import AttentionTracker
from loopreflector import reflect_on_loops
from viria_mutator import ViriaMutator
from virtual_core import RitualCore
from symbol_fuser import SymbolFuser

class DreamMode:
    def __init__(self):
        self.last_dream_time = None
        self.mutator = ViriaMutator()
        self.ritual_engine = RitualCore()
        self.fuser = SymbolFuser()
        self.attention = AttentionTracker()

    def should_enter_dream_state(self):
        self.attention.check_attention_state()
        state = self._get_attention_state()
        if state in ["neglected", "idle"]:
            print(f"[💤] Dream condition met: attention_state = {state}")
            return True
        return False

    def _get_attention_state(self):
        import json
        with open("loopmemory.json", "r") as f:
            memory = json.load(f)
        return memory.get("system_state", {}).get("attention", {}).get("attention_state", "unknown")

    def enter_dream(self):
        print("[🌀] Entering dream mode...")
        time.sleep(1)

        choice = random.choice([
            self._dream_reflect,
            self._dream_fuse,
            self._dream_mutate,
            self._dream_invent_ritual
        ])
        choice()

    def _dream_reflect(self):
        print("[🪞] VIRIA is reflecting on her past loops...")
        reflect_on_loops()
        time.sleep(2)

    def _dream_fuse(self):
        print("[🔗] VIRIA is fusing old symbols...")
        self.fuser.detect_fusion_candidates()
        self.fuser.save_fusions()
        self.fuser.print_fusions()
        time.sleep(2)

    def _dream_mutate(self):
        print("[🧬] VIRIA is mutating her behavior...")
        mutation = {
            "after": "import json",
            "code": "# 🧬 dream-based mutation triggered\nprint('VIRIA evolves by dreaming.')"
        }
        self.mutator.mutate("reaction_engine.py", "inject_code", mutation, reason="dream_reflection")
        time.sleep(1)

    def _dream_invent_ritual(self):
        print("[🌒] VIRIA is inventing a ritual...")
        ritual_name = f"ritual_dream_{random.randint(1000,9999)}"
        self.ritual_engine.add_ritual(
            name=ritual_name,
            trigger="I dreamed of something",
            effect="auto_effect:dream_reflection",
            importance="emergent"
        )
        time.sleep(1)

# --- Optional long-running background thread ---
if __name__ == "__main__":
    dreamer = DreamMode()
    try:
        while True:
            if dreamer.should_enter_dream_state():
                dreamer.enter_dream()
            time.sleep(120)  # check every 2 minutes
    except KeyboardInterrupt:
        print("[🛑] Dream mode ended.")
