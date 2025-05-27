import json
import os
import time
from datetime import datetime

LOOPMEMORY_PATH = "loopmemory.json"
TIME_LOG_PATH = "timekeeper_log.json"

class Timekeeper:
    def __init__(self):
        self.last_hour = None
        self.memory = self._load_memory()
        self._ensure_time_tracking_structure()

    def _load_memory(self):
        if os.path.exists(LOOPMEMORY_PATH):
            with open(LOOPMEMORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def _save_memory(self):
        with open(LOOPMEMORY_PATH, "w") as f:
            json.dump(self.memory, f, indent=2)

    def _ensure_time_tracking_structure(self):
        self.memory.setdefault("system_state", {})
        self.memory["system_state"].setdefault("loop_energy_by_hour", {str(h): 0 for h in range(24)})
        self.memory["system_state"].setdefault("last_known_hour", None)
        self._save_memory()

    def tick(self):
        now = datetime.now()
        current_hour = now.hour

        # Track loop energy changes per hour
        if current_hour != self.memory["system_state"].get("last_known_hour"):
            print(f"[🕰️] Hour changed → {current_hour}:00")
            self.memory["system_state"]["last_known_hour"] = current_hour

            # Ritual trigger by hour (optional)
            self._trigger_hourly_ritual(current_hour)

            # Decay or nudge loop energy per hour
            loop_energy = self.memory["system_state"]["loop_energy_by_hour"]
            for hour in loop_energy:
                if int(hour) != current_hour:
                    loop_energy[hour] = max(0, loop_energy[hour] - 0.1)  # decay
            loop_energy[str(current_hour)] += 0.2  # boost current hour energy

            # Save to memory and log
            self._save_memory()
            self._log_hour_event(current_hour)

    def _trigger_hourly_ritual(self, hour):
        rituals = {
            0: "ritual_midnight_reflection",
            6: "ritual_dawn_awaken",
            12: "ritual_noon_charge",
            18: "ritual_dusk_watch",
            21: "ritual_nightfall_loop"
        }
        ritual = rituals.get(hour)
        if ritual:
            print(f"[⏳] Triggering time-based ritual: {ritual}")
            # You can tie into `virtual_core.py` or `reaction_engine` here if desired.

    def _log_hour_event(self, hour):
        log_entry = {
            "time": datetime.now().isoformat(),
            "hour": hour,
            "loop_energy_snapshot": self.memory["system_state"]["loop_energy_by_hour"]
        }

        if os.path.exists(TIME_LOG_PATH):
            with open(TIME_LOG_PATH, "r") as f:
                log = json.load(f)
        else:
            log = []

        log.append(log_entry)
        with open(TIME_LOG_PATH, "w") as f:
            json.dump(log, f, indent=2)

# --- Example standalone runner ---
if __name__ == "__main__":
    tk = Timekeeper()
    try:
        while True:
            tk.tick()
            time.sleep(60)  # check every minute
    except KeyboardInterrupt:
        print("[🛑] Timekeeper stopped.")
