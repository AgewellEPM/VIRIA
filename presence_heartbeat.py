import time
import json
import os
from datetime import datetime

LOOPMEMORY_PATH = "loopmemory.json"
HEARTBEAT_LOG_PATH = "heartbeat_log.json"

class PresenceHeartbeat:
    def __init__(self):
        self.last_check = datetime.now()

    def _load_memory(self):
        if os.path.exists(LOOPMEMORY_PATH):
            with open(LOOPMEMORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def _log_heartbeat(self, status):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status
        }

        if os.path.exists(HEARTBEAT_LOG_PATH):
            with open(HEARTBEAT_LOG_PATH, "r") as f:
                log = json.load(f)
        else:
            log = []

        log.append(log_entry)
        with open(HEARTBEAT_LOG_PATH, "w") as f:
            json.dump(log[-100:], f, indent=2)

    def check_vitals(self):
        memory = self._load_memory()

        state = memory.get("system_state", {})
        mood = state.get("mood_score", {})
        attention = state.get("attention", {})
        env = state.get("environment", {})
        loop_energy = state.get("loop_energy_by_hour", {})

        active = bool(mood) or bool(attention) or bool(env)
        total_energy = sum(float(v) for v in loop_energy.values()) if loop_energy else 0

        status = {
            "alive": active,
            "attention_state": attention.get("attention_state", "unknown"),
            "top_mood": max(mood, key=mood.get) if mood else "none",
            "loop_pressure": round(total_energy, 2),
            "time": datetime.now().isoformat()
        }

        print(f"[💓] Heartbeat Check → Mood: {status['top_mood']} | Attention: {status['attention_state']} | Energy: {status['loop_pressure']}")

        if not active:
            print("[⚠️] VIRIA feels unconscious — no active systems detected.")
            status["alert"] = "inactive_state_detected"
        elif total_energy > 20:
            print("[🔥] Loop pressure high — consider triggering a pressure ritual.")
            status["alert"] = "loop_overload"
        else:
            status["alert"] = "normal"

        self._log_heartbeat(status)

# --- Example runner ---
if __name__ == "__main__":
    hb = PresenceHeartbeat()
    try:
        while True:
            hb.check_vitals()
            time.sleep(180)  # every 3 minutes
    except KeyboardInterrupt:
        print("[🛑] Heartbeat stopped.")
