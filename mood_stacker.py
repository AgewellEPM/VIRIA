import json
import os
import time
from datetime import datetime, timedelta

MEMORY_PATH = "loopmemory.json"
DECAY_RATE = 0.1  # Mood decay per scan cycle
MAX_MOOD_VALUE = 10.0

class MoodStacker:
    def __init__(self):
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "r") as f:
                return json.load(f)
        return {"system_state": {"mood_score": {}}}

    def _save_memory(self):
        with open(MEMORY_PATH, "w") as f:
            json.dump(self.memory, f, indent=2)

    def stack_emotion(self, emotion, weight=1.0):
        mood = self.memory.setdefault("system_state", {}).setdefault("mood_score", {})
        mood[emotion] = min(mood.get(emotion, 0.0) + weight, MAX_MOOD_VALUE)
        self._save_memory()
        print(f"[🧠] Mood stacked: +{weight} → {emotion} → Total: {mood[emotion]:.2f}")

    def decay_moods(self):
        now = datetime.now()
        mood = self.memory.get("system_state", {}).get("mood_score", {})
        decayed = False

        for key in list(mood.keys()):
            mood[key] -= DECAY_RATE
            if mood[key] <= 0:
                del mood[key]
            else:
                decayed = True

        if decayed:
            self._save_memory()
            print("[🕊️] Mood decay applied.")

    def get_top_mood(self):
        mood = self.memory.get("system_state", {}).get("mood_score", {})
        if not mood:
            return "calm"
        return max(mood, key=mood.get)

    def print_mood_state(self):
        mood = self.memory.get("system_state", {}).get("mood_score", {})
        print("\n[🌗 VIRIA Mood Stack]")
        for k, v in mood.items():
            print(f"• {k}: {v:.2f}")

# --- Example usage ---
if __name__ == "__main__":
    stacker = MoodStacker()

    while True:
        choice = input("\nEmotion to stack (or 'decay', 'state', 'exit'): ").strip().lower()
        if choice == "exit":
            break
        elif choice == "decay":
            stacker.decay_moods()
        elif choice == "state":
            stacker.print_mood_state()
        else:
            stacker.stack_emotion(choice)
