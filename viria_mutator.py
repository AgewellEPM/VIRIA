import os
import json
import shutil
from datetime import datetime
from vulnerability_guard import VulnerabilityGuard

MUTATION_LOG_PATH = "mutation_log.json"
BACKUP_DIR = "code_backup"

class ViriaMutator:
    def __init__(self):
        self.log = []
        self.guard = VulnerabilityGuard()

        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

    def mutate(self, target_file, mutation_type, payload, reason="unknown"):
        if not os.path.exists(target_file):
            print(f"[❌] File not found: {target_file}")
            return

        if self.guard.is_protected(target_file):
            print(f"[🛑] Mutation blocked: '{target_file}' is protected. Unlock required.")
            return

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"{os.path.basename(target_file)}.{timestamp}.bak")
        shutil.copyfile(target_file, backup_file)

        try:
            with open(target_file, "r") as f:
                lines = f.readlines()

            if mutation_type == "inject_code":
                after_line = payload["after"]
                code = payload["code"] + "\n"
                for i, line in enumerate(lines):
                    if after_line in line:
                        lines.insert(i + 1, code)
                        break

            elif mutation_type == "replace_line":
                match = payload["match"]
                replace = payload["replace"]
                for i, line in enumerate(lines):
                    if match in line:
                        lines[i] = line.replace(match, replace)

            elif mutation_type == "append_function":
                code = "\n" + payload + "\n"
                lines.append(code)

            with open(target_file, "w") as f:
                f.writelines(lines)

            self._log_mutation(target_file, mutation_type, payload, reason)
            print(f"[🧬] Mutation applied to {target_file} [{mutation_type}]")

        except Exception as e:
            print(f"[❌] Mutation failed: {e}")

    def _log_mutation(self, file, mtype, payload, reason):
        entry = {
            "time": datetime.now().isoformat(),
            "file": file,
            "type": mtype,
            "payload": payload,
            "reason": reason
        }

        if os.path.exists(MUTATION_LOG_PATH):
            with open(MUTATION_LOG_PATH, "r") as f:
                self.log = json.load(f)
        else:
            self.log = []

        self.log.append(entry)

        with open(MUTATION_LOG_PATH, "w") as f:
            json.dump(self.log[-100:], f, indent=2)

    def list_mutations(self, limit=5):
        if not self.log:
            print("[ℹ️] No mutations logged yet.")
            return

        print(f"\n[📝 Last {limit} Mutations]")
        for entry in self.log[-limit:]:
            print(f"• {entry['time']} → {entry['file']} ({entry['type']}) — {entry['reason']}")

# --- Manual Test ---
if __name__ == "__main__":
    vm = ViriaMutator()

    test_patch = {
        "after": "import json",
        "code": "# 🔧 Self-mutation test\nprint('I evolved.')"
    }

    vm.mutate("reaction_engine.py", "inject_code", test_patch, reason="self_test")
    vm.list_mutations()
