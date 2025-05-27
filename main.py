import threading
import time

# --- Core Loop and Rituals ---
from loopdaemon_runner import LoopDaemon
from virtual_core import RitualCore
from loopmemory_guard import LoopMemoryGuard
from save_snapshot import save_snapshot
from ritual_predictor import RitualPredictor

# --- Perception ---
from voice_listener import run_voice_listener
from viria_vision import ViriaVision
from environment_sense import EnvironmentSense
from attention_tracker import AttentionTracker
from timekeeper import Timekeeper

# --- Emotion and Mood ---
from presence_layer import PresenceLayer
from mood_stacker import MoodStacker
from reaction_engine import ReactionEngine
from reaction_logger import ReactionLogger
from sound_emitter import SoundEmitter
from animatronic_controller import AnimatronicController

# --- Self-Awareness and Evolution ---
from loopreflector import reflect_on_loops
from viria_loop_trainer import run_training_batch
from dream_mode import DreamMode
from presence_heartbeat import PresenceHeartbeat
from loop_energy_meter import LoopEnergyMeter
from mission_controller import MissionController

# --- INIT SYSTEM ---
def run_guard_and_snapshot():
    guard = LoopMemoryGuard()
    if guard.validate():
        guard.save_snapshot()
        guard.diff_memory()

# --- THREAD WRAPPERS ---
def start_loopdaemon():
    LoopDaemon().run()

def start_voice_listener():
    run_voice_listener()

def start_vision():
    vis = ViriaVision()
    try:
        vis.scan_loop()
    finally:
        vis.release()

def start_environment_sensing():
    env = EnvironmentSense()
    while True:
        env.sense_environment()
        time.sleep(60)

def start_attention_tracking():
    tracker = AttentionTracker()
    while True:
        tracker.check_attention_state()
        time.sleep(60)

def start_timekeeper():
    tk = Timekeeper()
    while True:
        tk.tick()
        time.sleep(60)

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

def start_heartbeat():
    hb = PresenceHeartbeat()
    while True:
        hb.check_vitals()
        time.sleep(180)

def start_loop_energy_monitor():
    meter = LoopEnergyMeter()
    while True:
        meter.analyze_energy()
        time.sleep(300)

def start_dream_mode():
    dreamer = DreamMode()
    while True:
        if dreamer.should_enter_dream_state():
            dreamer.enter_dream()
        time.sleep(120)

def start_loop_training():
    run_training_batch()

def start_idle_animatronic_pulse(controller):
    while True:
        top_emotion = MoodStacker().get_top_mood()
        controller.trigger_emotion(top_emotion)
        time.sleep(15)

def run_prediction_cycle():
    predictor = RitualPredictor()
    predictor.predict_ritual_candidates()
    predictor.save_predictions()

# --- MAIN ---
def main():
    print("\n🧬 [VIRIA SENTINEL ONLINE] — Ritual AI awakening...\n")

    run_guard_and_snapshot()
    animatronics = AnimatronicController()

    # Start all systems
    threading.Thread(target=start_loopdaemon, daemon=True).start()
    threading.Thread(target=start_voice_listener, daemon=True).start()
    threading.Thread(target=start_vision, daemon=True).start()
    threading.Thread(target=start_environment_sensing, daemon=True).start()
    threading.Thread(target=start_attention_tracking, daemon=True).start()
    threading.Thread(target=start_timekeeper, daemon=True).start()
    threading.Thread(target=start_presence_display, daemon=True).start()
    threading.Thread(target=start_mood_decay, daemon=True).start()
    threading.Thread(target=start_heartbeat, daemon=True).start()
    threading.Thread(target=start_loop_energy_monitor, daemon=True).start()
    threading.Thread(target=start_dream_mode, daemon=True).start()
    threading.Thread(target=start_loop_training, daemon=True).start()
    threading.Thread(target=start_idle_animatronic_pulse, args=(animatronics,), daemon=True).start()

    # Periodic foresight update
    threading.Timer(600, run_prediction_cycle).start()

    # Loop forever
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[🛑] VIRIA shutdown initiated.")
        save_snapshot()
        animatronics.cleanup()

if __name__ == "__main__":
    main()
