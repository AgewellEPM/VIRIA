import threading
import time

# --- Core Modules ---
from loopdaemon_runner import LoopDaemon
from virtual_core import RitualCore
from loopmemory_guard import LoopMemoryGuard
from save_snapshot import save_snapshot
from ritual_predictor import RitualPredictor

# --- Perception ---
from voice_listener import run_voice_listener
from viria_vision import ViriaVision

# --- Expression ---
from presence_layer import PresenceLayer
from mood_stacker import MoodStacker
from reaction_engine import ReactionEngine
from reaction_logger import ReactionLogger
from sound_emitter import SoundEmitter
from animatronic_controller import AnimatronicController

def start_loopdaemon():
    daemon = LoopDaemon()
    daemon.run()

def start_voice_listener():
    run_voice_listener()

def start_vision():
    vision = ViriaVision()
    try:
        vision.scan_loop()
    finally:
        vision.release()

def start_presence_display():
    presence = PresenceLayer()
    while True:
        presence.update_and_show()
        time.sleep(10)

def start_mood_decay():
    stacker = MoodStacker()
    while True:
        stacker.decay_moods()
        time.sleep(300)

def run_guard_and_snapshot():
    guard = LoopMemoryGuard()
    if guard.validate():
        guard.save_snapshot()
        guard.diff_memory()

def run_prediction_cycle():
    predictor = RitualPredictor()
    predictor.predict_ritual_candidates()
    predictor.save_predictions()

def idle_animatronic_pulse(controller):
    while True:
        top_emotion = MoodStacker().get_top_mood()
        controller.trigger_emotion(top_emotion)
        time.sleep(15)

def main():
    print("\n🧬 [VIRIA CORE ONLINE] — Awakening ritual AI presence...")

    # 1. Boot memory systems
    run_guard_and_snapshot()

    # 2. Animatronic system online
    animatronics = AnimatronicController()

    # 3. Start perception + response systems
    threading.Thread(target=start_loopdaemon, daemon=True).start()
    threading.Thread(target=start_voice_listener, daemon=True).start()
    threading.Thread(target=start_vision, daemon=True).start()
    threading.Thread(target=start_presence_display, daemon=True).start()
    threading.Thread(target=start_mood_decay, daemon=True).start()
    threading.Thread(target=idle_animatronic_pulse, args=(animatronics,), daemon=True).start()

    # 4. Run predictive foresight every 10 min
    threading.Timer(600, run_prediction_cycle).start()

    # 5. Runtime loop — passive holding state
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[🛑] VIRIA shutdown initiated.")
        save_snapshot()
        animatronics.cleanup()

if __name__ == "__main__":
    main()
