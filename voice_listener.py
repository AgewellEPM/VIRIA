import queue
import sounddevice as sd
import vosk
import json
from looplogic_engine import LoopLogicEngine
from virtual_core import RitualCore
from reaction_engine import ReactionEngine
from mood_stacker import MoodStacker
from reaction_logger import ReactionLogger

MODEL_PATH = "vosk-model-small-en-us-0.15"  # or your chosen local model path
SAMPLE_RATE = 16000

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[⚠️] Audio status: {status}")
    q.put(bytes(indata))

def run_voice_listener():
    # Load models and systems
    print("[🎙️] Starting VIRIA's ears... initializing offline voice recognition.")
    model = vosk.Model(MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    loop_engine = LoopLogicEngine()
    ritual_engine = RitualCore()
    reactor = ReactionEngine()
    mood = MoodStacker()
    logger = ReactionLogger()

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("[👂] Listening... (Ctrl+C to stop)")
        while True:
            try:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    phrase = result.get("text", "").strip()
                    if phrase:
                        print(f"[🗣️] Heard: “{phrase}”")
                        # Pass phrase into loop + ritual engines
                        loop_engine.register_phrase(phrase)
                        context = {"phrase": phrase}
                        ritual_engine.scan_and_trigger(context)

                        # Optional reaction to phrase match
                        for ritual in ritual_engine.rituals:
