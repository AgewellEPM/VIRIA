import json
import os
from datetime import datetime
from viria_mutator import ViriaMutator
from vulnerability_guard import VulnerabilityGuard

LOOPMEMORY_PATH = "loopmemory.json"
RITUAL_MUTATION_RULES_PATH = "ritual_mutation_map.json"

class RitualMutator:
    def __init__(self):
        self.mutator = ViriaMutator()
        self.guard = VulnerabilityGuard()
        self.memory = self._load_json(LOOPMEMORY_PATH)
        self.rules = self._load_json(RITUAL_MUTATION_RULES_PATH)

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def check_and_mutate(self):
        triggered = [r for r in self.memory.get("rituals", []) if r.get("last_triggered")]
        for ritual in triggered:
            name = ritual["name"]
            if name in self.rules:
                patch = self.rules[name]
                print(f"[⚡] Ritual '{name}' is mapped to a code mutation.")
                self._apply_patch(patch, ritual)
            else:
                continue

    def _apply_patch(self, patch, ritual):
        target = patch["target_file"]
        if self.guard.is_protected(target):
            print(f"[🛑] Mutation blocked for {target} — protected file.")
            return

        self.mutator.mutate(
            target_file=target,
            mutation_type=patch["type"],
            payload=patch["payload"],
            reason=f"ritual_trigger:{ritual['name']}"
        )

# --- Optional standalone run ---
if __name__ == "__main__":
    rm = RitualMutator()
    rm.check_and_mutate()
