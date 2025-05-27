import os
import time
import json
from datetime import datetime
import random

# Optional real sensors (can stub these out if not available)
try:
    import board
    import analogio  # for light sensor on GPIO (e.g. LDR)
    import adafruit_dht
    SENSOR_AVAILABLE = True
except ImportError:
    SENSOR_AVAILABLE = False

LOOPMEMORY_PATH = "loopmemory.json"
ENVIRONMENT_LOG_PATH = "environment_log.json"

class EnvironmentSense:
    def __init__(self):
        self.env_state = {
            "light_level": "unknown",
            "sound_level": "unknown",
            "temperature": "unknown",
            "last_update": None
        }

        if SENSOR_AVAILABLE:
            self.light_sensor = analogio.AnalogIn(board.A1)
            self.temp_sensor = adafruit_dht.DHT22(board.D4)

    def _simulate_light_level(self):
        return random.choice(["bright", "dim", "dark"])

    def _simulate_sound_level(self):
        return random.choice(["quiet", "normal", "noisy"])

    def _simulate_temperature(self):
        return random.choice(["cold", "comfortable", "hot"])

    def sense_environment(self):
        # Replace with real sensor reads if available
        if SENSOR_AVAILABLE:
            # Stub for light: scale analog to string
            light_raw = self.light_sensor.value
            if light_raw > 50000:
                light = "bright"
            elif light_raw > 20000:
                light = "dim"
            else:
                light = "dark"

            try:
                temp = self.temp_sensor.temperature
                if temp < 18:
                    temp_state = "cold"
                elif temp > 28:
                    temp_state = "hot"
                else:
                    temp_state = "comfortable"
            except RuntimeError:
                temp_state = "unknown"

            # TODO: Add microphone RMS for sound sensing
            sound = "normal"
        else:
            light = self._simulate_light_level()
            sound = self._simulate_sound_level()
            temp_state = self._simulate_temperature()

        self.env_state = {
            "light_level": light,
            "sound_level": sound,
            "temperature": temp_state,
            "last_update": datetime.now().isoformat()
        }

        self._log_environment()
        self._write_to_memory()
        print(f"[🌡️] Environment sensed → Light: {light} | Sound: {sound} | Temp: {temp_state}")

    def _log_environment(self):
        if os.path.exists(ENVIRONMENT_LOG_PATH):
            with open(ENVIRONMENT_LOG_PATH, "r") as f:
                log = json.load(f)
        else:
            log = []

        log.append(self.env_state)

        with open(ENVIRONMENT_LOG_PATH, "w") as f:
            json.dump(log[-100:], f, indent=2)  # keep last 100 entries

    def _write_to_memory(self):
        if not os.path.exists(LOOPMEMORY_PATH):
            return

        with open(LOOPMEMORY_PATH, "r") as f:
            memory = json.load(f)

        memory.setdefault("system_state", {})
        memory["system_state"]["environment"] = self.env_state

        with open(LOOPMEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)

# --- Example runner ---
if __name__ == "__main__":
    es = EnvironmentSense()
    try:
        while True:
            es.sense_environment()
            time.sleep(60)  # check once per minute
    except KeyboardInterrupt:
        print("[🛑] Environment sensing stopped.")
