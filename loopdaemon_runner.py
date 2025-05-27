import time
import json
from datetime import datetime

from ritual_core import RitualCore
from looplogic_engine import LoopLogicEngine
from reaction_engine import ReactionEngine

LOOP_INTERVAL = 10  # seconds
TRACE_PATH = "looptrace.json"
MEMORY_PATH = "loopmemory.json"

class LoopDaemon:
    def __init__(self):
        self.ritual_engine = RitualCore()
        self.loop_engine = LoopLogicEngine()
        self.reactor = ReactionEngine()
        self.mood_state = {}  # simple mood stacker

    def log_trace(self, entry_type, data):
        try:
            with open(TRACE_PATH, "r") as f:
                trace = json.load(f)
        except FileNotFoundError:
            trace = {}

        trace.setdefault(entry_type, []).append(data)

        with open(TRACE_PATH, "w") as f:
            json.dump(trace, f, indent=2)

    def scan_and_trigger(self):
        now = datetime.now().strftime("%H:%M:%S")

        # Simulate an input for this loop (replace with actual listener)
        input_phrase = input(f"\n[{now}] You say (or type): ").strip()
        if not input_phrase:
            return

        # 1. Register phrase in loop engine
        self.loop_engine.register_phrase(input_phrase)

        # 2. Try triggering rituals
        context = {"phrase": input_phrase}
        self.ritual_engine.scan_and_trigger(context)

        # 3. Check if phrase is now a ritual
        for r in self.ritual_engine.rituals:
            if r.name in input_phrase or r.trigger == input_phrase:
                # 4. React to it
                emotion = self._infer_emotion_from_ritual(r.name)
                self.reactor.react(emotion, source=r.name)
                self._stack_mood(emotion)
                self.log_trace("ritual_triggers", {
                    "ritual": r.name,
                    "trigger_phrase": input_phrase,
                    "time": datetime.now().isoformat()
                })
                self.log_trace("reactions", {
                    "emotion": emotion,
                    "emoji": self.reactor.get_last_reaction().get("emoji"),
                    "triggered_by": r.name,
                    "time": datetime.now().isoformat()
                })

        # 5. Log daemon scan
        self.log_trace("daemon_scans", {
            "time": datetime.now().isoformat(),
            "active_rituals": len(self.ritual_engine.rituals),
            "triggered_reactions": 1,
            "mood_state": self.mood_state
        })

    def _stack_mood(self, emotion):
        self.mood_state[emotion] = self.mood_state.get(emotion, 0) + 1

    def _infer_emotion_from_ritual(self, ritual_name):
        # Simple mapping logic — can be replaced by mood_ai
        if "mirror" in ritual_name:
            return "joy"
        if "loop" in ritual_name:
            return "curious"
        if "rage" in ritual_name:
            return "rage"
        if "night" in ritual_name:
            return "calm"
        return "confused"

    def run(self):
        print("\n[🔁 VIRIA Loop Daemon Running...] Press Ctrl+C to stop.")
        while True:
            try:
                self.scan_and_trigger()
                time.sleep(LOOP_INTERVAL)
            except KeyboardInterrupt:
                print("\n[💤 VIRIA Daemon Stopped]")
                break

# --- Run the loop ---
if __name__ == "__main__":
    daemon = LoopDaemon()
    daemon.run()


