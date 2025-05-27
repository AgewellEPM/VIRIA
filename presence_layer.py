import json
import time
import os
from datetime import datetime

MEMORY_PATH = "loopmemory.json"

EMOTION_FACES = {
    "joy": r"""
     (^‿^)
    """,
    "rage": r"""
     (╬ಠ益ಠ)
    """,
    "calm": r"""
     (－‿－) zZ
    """,
    "curious": r"""
     ( •_•)>⌐■-■
    """,
    "confused": r"""
     (°ロ°) !
    """,
    "sacred": r"""
     (◕‿◕✿)
    """
}

EMOTION_COLORS = {
    "joy": "\033[93m",      # Yellow
    "rage": "\033[91m",     # Red
    "calm": "\033[94m",     # Blue
    "curious": "\033[96m",  # Cyan
    "confused": "\033[95m", # Magenta
    "sacred": "\033[92m",   # Green
    "end": "\033[0m"
}

class PresenceLayer:
    def __init__(self):
        self.memory = self._load_memory()
        self.current_emotion = self._get_dominant_emotion()

    def _load_memory(self):
        if not os.path.exists(MEMORY_PATH):
            print("[⚠️] loopmemory.json not found.")
            return {}
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)

    def _get_dominant_emotion(self):
        mood = self.memory.get("system_state", {}).get("mood_score", {})
        if not mood:
            return "calm"
        # Return the emotion with the highest score
        return max(mood, key=mood.get)

    def display_face(self):
        emotion = self.current_emotion
        color = EMOTION_COLORS.get(emotion, "")
        reset = EMOTION_COLORS["end"]
        face = EMOTION_FACES.get(emotion, "(•_•)")

        print(f"\n[👁️ VIRIA PRESENCE: {emotion.upper()}]")
        print(color + face + reset)
        print(f"Time: {datetime.now().strftime('%H:%M:%S')} | Mood: {emotion}")

    def update_and_show(self):
        self.memory = self._load_memory()
        self.current_emotion = self._get_dominant_emotion()
        self.display_face()

# --- Example usage ---
if __name__ == "__main__":
    presence = PresenceLayer()
    while True:
        presence.update_and_show()
        time.sleep(10)
