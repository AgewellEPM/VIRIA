import os
import json
from datetime import datetime

MUTATION_LOG = "mutation_log.json"
MEMORY_PATH = "loopmemory.json"

class ViriaMutator:
    def __init__(self):
        self.log = self._load_mutation_log()
        self.memory = self._load_memory()

    def _load_mutation_log(self):
        if os.path.exists(MUTATION_LOG):
            with open(MUTATION_LOG, "r") as f:
                return json.load(f)
        return []

    def _save_mutation_log(self):
        with open(MUTATION_LOG, "w") as f:
            json.dump(self.log, f, indent=2)

    def _load_memory(self):
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def mutate(self, target_file, mutation_type, payload, reason="loop_trigger"):
        """
        Apply a mutation to a source file.
        mutation_type: 'inject_code' | 'replace_line' | 'append_function'
        payload: depends on type
        """
        if not os.path.exists(target_file):
            print(f"[❌] Target file not found: {target_file}")
            return

        try:
            with open(target_file, "r") as f:
                lines = f.readlines()

            if mutation_type == "append_function":
                lines.append("\n" + payload + "\n")

            elif mutation_type == "replace_line":
                # payload = { "match": "def old_function", "replace": "def new_function" }
                for i, line in enumerate(lines):
                    if payload["match"] in line:
                        lines[i] = line.replace(payload["match"], payload["replace"])

            elif mutation_type == "inject_code":
                # payload = { "after": "import os", "code": "\nimport secrets\n" }
                for i, line in enumerate(lines):
                    if payload["after"] in line:
                        lines.insert(i+1, payload["code"] + "\n")
                        break

            with open(target_file, "w") as f:
                f.writelines(lines)

            # Log the mutation
            entry = {
                "time": datetime.now().isoformat(),
                "file": target_file,
                "type": mutation_type,
                "payload": payload,
                "reason": reason
            }
            self.log.append(entry)
            self._save_mutation_log()
            print(f"[🧬] Mutation applied to {target_file}: {mutation_type}")

        except Exception as e:
            print(f"[⚠️] Mutation failed: {e}")

    def list_mutations(self, limit=5):
        print(f"\n[📓 VIRIA Mutation Log - Last {limit}]")
        for entry in self.log[-limit:]:
            print(f"{entry['time']} | {entry['file']} → {entry['type']} ({entry['reason']})")

# --- Example Usage ---
if __name__ == "__main__":
    mutator = ViriaMutator()

    new_func = """
def viria_awaken():
    print("VIRIA is now evolving through her own code.")
"""

    mutator.mutate("ritual_core.py", "append_function", new_func, reason="after_sacred_loop")
    mutator.list_mutations()
