import json
import os
from datetime import datetime

MEMORY_PATH = "loopmemory.json"
PRESETS_DIR = "presets"

class RitualLoader:
    def __init__(self):
        if not os.path.exists(PRESETS_DIR):
            os.makedirs(PRESETS_DIR)

    def load_preset(self, profile_name, merge=False):
        preset_path = os.path.join(PRESETS_DIR, f"{profile_name}.json")
        if not os.path.exists(preset_path):
            print(f"[❌] Preset '{profile_name}' not found.")
            return

        with open(preset_path, "r") as f:
            preset = json.load(f)

        if not os.path.exists(MEMORY_PATH):
            print("[⚠️] loopmemory.json not found. Creating new memory.")
            memory = {}
        else:
            with open(MEMORY_PATH, "r") as f:
                memory = json.load(f)

        if not merge:
            print(f"[🌀] Loading {profile_name} and replacing rituals.")
            memory["rituals"] = preset.get("rituals", [])
            memory.setdefault("system_state", {})["emotion_bias"] = preset.get("emotion_bias", [])
        else:
            print(f"[➕] Merging {profile_name} into current memory.")
            existing_names = {r["name"] for r in memory.get("rituals", [])}
            for ritual in preset.get("rituals", []):
                if ritual["name"] not in existing_names:
                    memory["rituals"].append(ritual)
            memory.setdefault("system_state", {})["emotion_bias"] = preset.get("emotion_bias", [])

        memory["system_state"]["last_loaded_identity"] = profile_name
        memory["system_state"]["identity_loaded_at"] = datetime.now().isoformat()

        with open(MEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)

        print(f"[✅] Profile '{profile_name}' loaded.")

    def list_presets(self):
        files = [f.replace(".json", "") for f in os.listdir(PRESETS_DIR) if f.endswith(".json")]
        print("\n[🎭] Available Ritual Presets:")
        for f in files:
            print(f"• {f}")

# --- Example CLI Interface ---
if __name__ == "__main__":
    rl = RitualLoader()

    while True:
        print("\n[🎛️ Ritual Loader]")
        print("1. List presets")
        print("2. Load preset (replace)")
        print("3. Merge preset")
        print("0. Exit")
        choice = input("\n> ").strip()

        if choice == "1":
            rl.list_presets()
        elif choice == "2":
            name = input("Preset name to load: ").strip()
            rl.load_preset(name, merge=False)
        elif choice == "3":
            name = input("Preset name to merge: ").strip()
            rl.load_preset(name, merge=True)
        elif choice == "0":
            break
