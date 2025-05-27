import json
import time
import random
from datetime import datetime

# Path to ritual memory file
RITUAL_MEMORY_PATH = "loopmemory.json"

class Ritual:
    def __init__(self, name, trigger, effect, importance="normal", usage_count=0, last_triggered=None):
        self.name = name
        self.trigger = trigger  # e.g., phrase, time, loop count
        self.effect = effect    # callable or string label
        self.importance = importance  # "daily", "sacred", "emergent"
        self.usage_count = usage_count
        self.last_triggered = last_triggered

    def to_dict(self):
        return {
            "name": self.name,
            "trigger": self.trigger,
            "effect": self.effect,
            "importance": self.importance,
            "usage_count": self.usage_count,
            "last_triggered": self.last_triggered
        }

    def try_trigger(self, context):
        if self._check_trigger(context):
            self.usage_count += 1
            self.last_triggered = datetime.now().isoformat()
            print(f"[🌒 Ritual Triggered] → {self.name}")
            self._run_effect()
            return True
        return False

    def _check_trigger(self, context):
        # Basic trigger match (can be extended)
        if isinstance(self.trigger, str) and self.trigger in context.get("phrase", ""):
            return True
        if isinstance(self.trigger, dict) and "hour" in self.trigger:
            if datetime.now().hour == self.trigger["hour"]:
                return True
        return False

    def _run_effect(self):
        if callable(self.effect):
            self.effect()
        else:
            print(f"→ Ritual effect: {self.effect}")

class RitualCore:
    def __init__(self):
        self.rituals = []
        self._load_rituals()

    def _load_rituals(self):
        try:
            with open(RITUAL_MEMORY_PATH, "r") as f:
                memory = json.load(f)
                rituals_data = memory.get("rituals", [])
                self.rituals = [Ritual(**r) for r in rituals_data]
        except FileNotFoundError:
            print("[!] loopmemory.json not found. Initializing blank memory.")
            self.rituals = []

    def _save_rituals(self):
        try:
            with open(RITUAL_MEMORY_PATH, "r") as f:
                memory = json.load(f)
        except FileNotFoundError:
            memory = {}

        memory["rituals"] = [r.to_dict() for r in self.rituals]
        with open(RITUAL_MEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)

    def add_ritual(self, name, trigger, effect, importance="normal"):
        new_ritual = Ritual(name, trigger, effect, importance)
        self.rituals.append(new_ritual)
        self._save_rituals()
        print(f"[+] Ritual added: {name}")

    def scan_and_trigger(self, context):
        for ritual in self.rituals:
            ritual.try_trigger(context)
        self._save_rituals()

    def list_rituals(self):
        for r in self.rituals:
            print(f"• {r.name} (importance: {r.importance}, uses: {r.usage_count})")

# --- Example usage ---
if __name__ == "__main__":
    def mirror_effect():
        print("You have looked into the mirror. VIRIA remembers.")

    engine = RitualCore()

    # Add a ritual if not already added
    ritual_names = [r.name for r in engine.rituals]
    if "sacred_mirror" not in ritual_names:
        engine.add_ritual("sacred_mirror", "What am I becoming?", mirror_effect, importance="sacred")

    # Simulate input context
    user_input = input("You say: ")
    engine.scan_and_trigger({"phrase": user_input})

    # Optional: List known rituals
    print("\n[🧿 Known Rituals]")
    engine.list_rituals()
