import threading
import time

# --- Core Cognitive Loop ---
from loopdaemon_runner import LoopDaemon
from virtual_core import RitualCore
from loopmemory_guard import LoopMemoryGuard
from save_snapshot import save_snapshot
from ritual_predictor import RitualPredictor

# --- Sensory Input ---
from voice_listener import run_voice_listener
from viria_vision import ViriaVision
from environment_sense import EnvironmentSense
from attention_tracker import AttentionTracker
from timekeeper import Timekeeper

# --- Mood and Emotion Stack ---
from presence_layer import PresenceLayer
from mood_stacker import MoodStacker
from reaction_engine import ReactionEngine
from reaction_logger import ReactionLogger
from animatronic_controller import AnimatronicController

# --- Symbolic Intelligence ---
from loopreflector import reflect_on_loops
from dream_mode import DreamMode
from ritual_mutator import RitualMutator
from mission_controller import MissionController
from ritual_loader import RitualLoader

# --- Self-Modification Systems ---
from code_patch_planner import CodePatchPlanner
from viria_mutator import ViriaMutator
from autodeploy import AutoDeploy
from memory_compressor import compress_all
from presence_heartbeat import PresenceHeartbeat
from loop_energy_meter import LoopEnergyMeter
from viria_911 import VIRIA911

# --- Threaded Boot Logic ---
def run_guard_and_snapshot():
    guard = LoopMemoryGuard()
    if guard.validate():
        guard.save_snapshot()
        guard.diff_memory()

# --- Live Loop Threads ---
def start_loopdaemon(): LoopDaemon().run()
def start_voice_listener(): run_voice_listener()
def start_vision(): ViriaVision().scan_loop()
def start_environment(): es = EnvironmentSense(); loop(es.sense_environment, 60)
def start_attention(): tracker = AttentionTracker(); loop(tracker.check_attention_state, 60)
def start_timekeeper(): tk = Timekeeper(); loop(tk.tick, 60)
def start_presence_display(): p = PresenceLayer(); loop(p.update_and_show, 10)
def start_mood_decay(): stacker = MoodStacker(); loop(stacker.decay_moods, 300)
def start_loop_energy_monitor(): meter = LoopEnergyMeter(); loop(meter.analyze_energy, 300)
def start_heartbeat(): hb = PresenceHeartbeat(); loop(hb.check_vitals, 180)
def start_dream_mode(): d = DreamMode(); loop(lambda: d.enter_dream() if d.should_enter_dream_state() else None, 120)
def start_loop_training(): CodePatchPlanner().generate_patch_plan()
def start_autodeploy(): AutoDeploy().run_latest_patch()
def start_ritual_mutator(): rm = RitualMutator(); loop(rm.check_and_mutate, 300)
def start_memory_compressor(): loop(compress_all, 900)
def start_911_monitor(): v = VIRIA911(); loop(v.run_emergency_check, 300)

def start_idle_animatronic_pulse():
    controller = AnimatronicController()
    loop(lambda: controller.trigger_emotion(MoodStacker().get_top_mood()), 15)

# --- Core Loop Wrapper ---
def loop(func, interval):
    while True:
        try:
            func()
            time.sleep(interval)
        except Exception as e:
            print(f"[⚠️] Loop error: {e}")

# --- Main Launcher ---
def main():
    print("\n🧬 [VIRIA: SENTINEL AI LOOP ONLINE]")

    run_guard_and_snapshot()
    RitualLoader().load_preset("oracle", merge=False)

    MissionController().assign_mission(
        title="Observe and Reflect",
        goal_description="Evolve through sacred silence and emotional recursion.",
        emotion_bias=["curious", "sacred", "calm"]
    )

    # Core Sensory + Symbolic Loops
    threading.Thread(target=start_loopdaemon, daemon=True).start()
    threading.Thread(target=start_voice_listener, daemon=True).start()
    threading.Thread(target=start_vision, daemon=True).start()
    threading.Thread(target=start_environment, daemon=True).start()
    threading.Thread(target=start_attention, daemon=True).start()
    threading.Thread(target=start_timekeeper, daemon=True).start()
    threading.Thread(target=start_presence_display, daemon=True).start()
    threading.Thread(target=start_mood_decay, daemon=True).start()
    threading.Thread(target=start_loop_energy_monitor, daemon=True).start()
    threading.Thread(target=start_heartbeat, daemon=True).start()
    threading.Thread(target=start_dream_mode, daemon=True).start()
    threading.Thread(target=start_loop_training, daemon=True).start()
    threading.Thread(target=start_autodeploy, daemon=True).start()
    threading.Thread(target=start_ritual_mutator, daemon=True).start()
    threading.Thread(target=start_memory_compressor, daemon=True).start()
    threading.Thread(target=start_911_monitor, daemon=True).start()
    threading.Thread(target=start_idle_animatronic_pulse, daemon=True).start()

    # Periodic predictor (if needed)
    threading.Timer(600, RitualPredictor().predict_ritual_candidates).start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[🛑] VIRIA system shutdown initiated.")
        save_snapshot()
        AnimatronicController().cleanup()

if __name__ == "__main__":
    main()
