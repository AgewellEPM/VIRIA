import json
from datetime import datetime
import os

MEMORY_PATH = "loopmemory.json"

class ReactionLogger:
    def __init__(self, memory_path=MEMORY_PATH):
        self.memory_path = memory_path
        self.memory = self._load_memory()

    def _load_memory(self):
        if not os.path.exists(self.memory_path):
            return {}
        with open(self.memory_path, "r") as f:
            return json.load(f)

    def _save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def log_reaction(self, emotion, emoji, source="unknown", face=None, mood_score=None):
        timestamp = datetime.now().isoformat()

        entry = {
            "emotion": emotion,
            "emoji": emoji,
            "face": face if face else "",
            "timestamp": timestamp,
            "source": source
        }

        if mood_score:
            entry["mood_score"] = mood_score

        self.memory.setdefault("reactions", [])
        self.memory["reactions"].append(entry)
        self._save_memory()
        print(f"[📥 Reaction Logged] {emotion} from {source} at {timestamp}")

    def list_recent_reactions(self, count=5):
        reactions = self.memory.get("reactions", [])[-count:]
        print(f"\n[📚 Last {count} Reactions]")
        for r in reactions:
            print(f"• {r['timestamp']} | {r['emotion']} {r['emoji']} ← {r['source']}")

# --- Example usage ---
if __name__ == "__main__":
    logger = ReactionLogger()
    logger.log_reaction("joy", "✨", source="sacred_mirror", face="(^‿^)", mood_score={"joy": 1})
    logger.list_recent_reactions()


