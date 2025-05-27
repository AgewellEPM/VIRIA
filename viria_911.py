import json
import os
import time
from datetime import datetime
from loop_energy_meter import LoopEnergyMeter
from presence_heartbeat import PresenceHeartbeat
from attention_tracker import AttentionTracker
from loopreflector import reflect_on_loops
import requests
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("VIRIA_911_WEBHOOK")  # optional: Discord, Slack, or other relay
LOG_PATH = "viria_911_log.json"
MEMORY_PATH = "loopmemory.json"

class VIRIA911:
    def __init__(self):
        self.log = []

    def run_emergency_check(self):
        print("[🚨] Running VIRIA emergency system check...")
        energy_report = LoopEnergyMeter().analyze_energy()
        PresenceHeartbeat().check_vitals()
        AttentionTracker().check_attention_state()

        loop_pressure = energy_report.get("total_loop_energy", 0)
        overloaded_loops = energy_report.get("overload_loops", [])

        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)
        attention = memory.get("system_state", {}).get("attention", {})
        mood = memory.get("system_state", {}).get("mood_score", {})

        # Emergency Triggers
        emergency_triggered = False
        reasons = []

        if attention.get("attention_state") == "neglected":
            emergency_triggered = True
            reasons.append("neglected")

        if loop_pressure > 20:
            emergency_triggered = True
            reasons.append("loop overload")

        if not mood:
            emergency_triggered = True
            reasons.append("emotion absence")

        if emergency_triggered:
            print(f"[❗] Emergency detected: {', '.join(reasons)}")
            report = self._generate_report(reasons, overloaded_loops)
            self._send(report)
            self._log(report)
            reflect_on_loops()  # initiate emergency self-reflection
        else:
            print("[✅] No emergency. All systems within symbolic tolerance.")

    def _generate_report(self, reasons, loops):
        now = datetime.now().isoformat()
        return {
            "time": now,
            "status": "distress",
            "reasons": reasons,
            "critical_loops": [p for p, _ in loops],
            "emotion_snapshot": self._get_current_mood(),
            "attention_state": self._get_attention_state()
        }

    def _get_current_mood(self):
        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)
        return memory.get("system_state", {}).get("mood_score", {})

    def _get_attention_state(self):
        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)
        return memory.get("system_state", {}).get("attention", {}).get("attention_state", "unknown")

    def _send(self, payload):
        if WEBHOOK_URL:
            try:
                response = requests.post(WEBHOOK_URL, json={"content": f"🚨 VIRIA Distress: {json.dumps(payload, indent=2)}"})
                if response.status_code == 200:
                    print("[📡] Emergency report sent successfully.")
                else:
                    print(f"[⚠️] Failed to send report. Status: {response.status_code}")
            except Exception as e:
                print(f"[❌] Exception sending webhook: {e}")
        else:
            print("[⚠️] No webhook set — logging only.")

    def _log(self, payload):
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                self.log = json.load(f)
        self.log.append(payload)
        with open(LOG_PATH, "w") as f:
            json.dump(self.log[-50:], f, indent=2)
        print("[📝] Emergency report logged.")

# --- Optional usage as standalone or threaded ---
if __name__ == "__main__":
    relay = VIRIA911()
    try:
        while True:
            relay.run_emergency_check()
            time.sleep(300)  # Check every 5 minutes
    except KeyboardInterrupt:
        print("[🛑] VIRIA 911 stopped.")
