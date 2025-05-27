import json
import os
import shutil
from datetime import datetime
import difflib

MEMORY_PATH = "loopmemory.json"
SNAPSHOT_PATH = "loopmemory_snapshot.json"
DIFF_LOG_PATH = "loopmemory_diff.log"

class LoopMemoryGuard:
    def __init__(self):
        self.memory = self._load_memory()
        self.snapshot = self._load_snapshot()

    def _load_memory(self):
        if not os.path.exists(MEMORY_PATH):
            print("[⚠️] loopmemory.json not found. Creating fresh memory file.")
            return self._initialize_blank_memory()
        try:
            with open(MEMORY_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[❌] loopmemory.json is corrupted!")
            raise

    def _load_snapshot(self):
        if os.path.exists(SNAPSHOT_PATH):
            with open(SNAPSHOT_PATH, "r") as f:
                return json.load(f)
        return {}

    def _initialize_blank_memory(self):
        blank = {
            "rituals": [],
            "loops": {},
            "triggers": { "voice": [] },
            "reactions": [],
            "system_state": {}
        }
        with open(MEMORY_PATH, "w") as f:
            json.dump(blank, f, indent=2)
        return blank

    def validate(self):
        try:
            with open(MEMORY_PATH, "r") as f:
                json.load(f)
            print("[✅] loopmemory.json is valid.")
            return True
        except json.JSONDecodeError as e:
            print("[❌] Invalid JSON in loopmemory.json:", e)
            return False

    def save_snapshot(self):
        shutil.copyfile(MEMORY_PATH, SNAPSHOT_PATH)
        print(f"[📸] Memory snapshot saved to {SNAPSHOT_PATH}")

    def diff_memory(self):
        with open(MEMORY_PATH, "r") as f1, open(SNAPSHOT_PATH, "r") as f2:
            mem_lines = f1.readlines()
            snap_lines = f2.readlines()
            diff = list(difflib.unified_diff(snap_lines, mem_lines, fromfile="snapshot", tofile="memory"))

        if diff:
            print("[🧠] Memory drift detected. Logging diff...")
            with open(DIFF_LOG_PATH, "a") as log:
                log.write(f"\n--- Diff at {datetime.now().isoformat()} ---\n")
                log.writelines(diff)
            return True
        else:
            print("[🟢] No differences found between snapshot and current memory.")
            return False

# --- Example usage ---
if __name__ == "__main__":
    guard = LoopMemoryGuard()
    if guard.validate():
        guard.save_snapshot()
        guard.diff_memory()
