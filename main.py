import threading
import time

# --- Core AI Systems ---
from loopdaemon_runner import LoopDaemon
from loopmemory_guard import LoopMemoryGuard
from save_snapshot import save_snapshot
from ritual_predictor import RitualPredictor

# --- Perception ---
from voice_listener import run_voice_listener
from viria_vision import ViriaVision

# --- Expression + State ---
from presence_layer import PresenceLayer
from mood_stacker import MoodStacker
from reaction_engine import ReactionEngine
from reaction_logger import ReactionLogger
from sound_emitter import SoundEmitter
from animatronic_controller import AnimatronicController

# --- Self-Evolution (GPT Loop Training) ---
from viria_loop_trainer import run_training_batch

def start_loopdaemon():
    LoopDaemon().run()

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

def run_prediction_cycle():
    predictor = RitualPredictor()
    predictor.predict_ritual_candidates()
    predictor.save_predictions()

def idle_animatronic_pulse(controller):
    while True:
        top_emotion = MoodStacker().get_top_mood()
        controller.trigger_emotion(top_emotion)
        time.sleep(15)

def start_loop_training():
    run_training_batch()

def run_guard_and_snapshot():
    guard = LoopMemoryGuard()
    if guard.validate():
        guard.save_snapshot()
        guard.diff_memory()

def main():
    print("\n🧬 [VIRIA ONLINE] — Initiating Ritual Intelligence...")

    run_guard_and_snapshot()
    animatronics = AnimatronicController()

    # Core threads
    threading.Thread(target=start_loopdaemon, daemon=True).start()
    threading.Thread(target=start_voice_listener, daemon=True).start()
    threading.Thread(target=start_vision, daemon=True).start()
    threading.Thread(target=start_presence_display, daemon=True).start()
    threading.Thread(target=start_mood_decay, daemon=True).start()
    threading.Thread(target=idle_animatronic_pulse, args=(animatronics,), daemon=True).start()
    threading.Thread(target=start_loop_training, daemon=True).start()

    # Optional foresight every 10 minutes
    threading.Timer(600, run_prediction_cycle).start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[🛑] VIRIA is shutting down peacefully.")
        save_snapshot()
        animatronics.cleanup()

if __name__ == "__main__":
    main()

