import shutil
import os
from datetime import datetime

MEMORY_PATH = "loopmemory.json"
SNAPSHOT_PATH = "loopmemory_snapshot.json"

def save_snapshot():
    if not os.path.exists(MEMORY_PATH):
        print("[❌] loopmemory.json does not exist. Nothing to snapshot.")
        return

    try:
        shutil.copyfile(MEMORY_PATH, SNAPSHOT_PATH)
        print(f"[📸] Snapshot saved to {SNAPSHOT_PATH} at {datetime.now().isoformat()}")
    except Exception as e:
        print(f"[⚠️] Failed to save snapshot: {e}")

if __name__ == "__main__":
    save_snapshot()
