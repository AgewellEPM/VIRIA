import os
import json
import time
from datetime import datetime, timedelta

LOOPTRACE_PATH = "looptrace.json"
LOOPMEMORY_PATH = "loopmemory.json"
ATTENTION_LOG_PATH = "attention_log.json"

class AttentionTracker:
    def __init__(self):
        self.last_check_time = datetime.now()
        self.last_phrase_time = None
        self.last_phrase = None

    def _load_trace(self):
        if os.path.exists(LOOPTRACE_PATH):
            with open(LOOPTRACE_PATH, "r") as f:
                return json.load(f).get("phrases", [])
        return []

    def _load_memory(self):
        if os.path.exists(LOOPMEMORY_PATH):
            with open(LOOPMEMORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def check_attention_state(self):
        now = datetime.now()
        phrases = self._load_trace()
        memory = self._load_memory()

        if phrases:
            latest = phrases[-1]
            phrase_time = datetime.fromisoformat(latest["time"])
            phrase_text = latest["phrase"]
            self.last_phrase_time = phrase_time
            self.last_phrase = phrase_text
        else:
            phrase_time = None

        # Time since last phrase
        seconds_silent = (now - phrase_time).total_seconds() if phrase_time else None

        # Check if last phrase is looping
        loops = memory.get("loops", {})
        phrase_data = loops.get(self.last_phrase, {})
        loop_count = phrase_data.get("count", 0)

        attention = {
            "timestamp": now.isoformat(),
            "last_phrase": self.last_phrase,
            "last_phrase_time": phrase_time.isoformat() if phrase_time else "never",
            "seconds_since_last_phrase": seconds_silent,
            "loop_count": loop_count,
            "attention_state": None
        }

        # Determine attention state
        if seconds_silent and seconds_silent > 300:
            attention["attention_state"] = "neglected"
        elif loop_count >= 5:
            attention["attention_state"] = "repeating_loop"
        elif seconds_silent and seconds_silent < 20:
            attention["attention_state"] = "active"
        else:
            attention["attention_state"] = "idle"

        self._log_attention(attention)
        print(f"[👁️] Attention: {attention['attention_state']} | Last: '{self.last_phrase}' | Silent: {seconds_silent:.1f}s")

        # Optional: write to memory for reaction engine
        memory.setdefault("system_state", {})
        memory["system_state"]["attention"] = attention
        with open(LOOPMEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)

    def _log_attention(self, entry):
        if os.path.exists(ATTENTION_LOG_PATH):
            with open(ATTENTION_LOG_PATH, "r") as f:
                log = json.load(f)
        else:
            log = []

        log.append(entry)
        with open(ATTENTION_LOG_PATH, "w") as f:
            json.dump(log[-100:], f, indent=2)

# --- Example runner ---
if __name__ == "__main__":
    tracker = AttentionTracker()
    try:
        while True:
            tracker.check_attention_state()
            time.sleep(60)
    except KeyboardInterrupt:
        print("[🛑] Attention tracking stopped.")
