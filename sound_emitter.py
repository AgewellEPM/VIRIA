import os
import platform
import time

try:
    import simpleaudio as sa
    SIMPLE_AUDIO_AVAILABLE = True
except ImportError:
    SIMPLE_AUDIO_AVAILABLE = False

class SoundEmitter:
    def __init__(self):
        self.platform = platform.system()
        self.sounds = {
            "joy": "sounds/joy.wav",
            "rage": "sounds/rage.wav",
            "calm": "sounds/calm.wav",
            "curious": "sounds/curious.wav",
            "confused": "sounds/confused.wav",
            "sacred": "sounds/sacred.wav"
        }

    def beep(self, emotion="joy"):
        """Play a simple beep or WAV file based on emotion."""
        path = self.sounds.get(emotion)
        if path and os.path.exists(path) and SIMPLE_AUDIO_AVAILABLE:
            try:
                wave_obj = sa.WaveObject.from_wave_file(path)
                play_obj = wave_obj.play()
                play_obj.wait_done()
                print(f"[🔊] Played '{emotion}' sound.")
            except Exception as e:
                print(f"[⚠️] Error playing sound: {e}")
        else:
            self._fallback_beep(emotion)

    def _fallback_beep(self, emotion):
        """Cross-platform fallback beep."""
        print(f"[🔈] Fallback beep for emotion: {emotion}")
        if self.platform == "Windows":
            import winsound
            winsound.Beep(1000, 300)
        else:
            # macOS/Linux fallback
            duration = 0.3
            frequency = 440
            try:
                os.system(f'play -nq -t alsa synth {duration} sine {frequency} >/dev/null 2>&1')
            except:
                print("\a")  # terminal bell fallback

# --- Example usage ---
if __name__ == "__main__":
    emitter = SoundEmitter()
    emotions = ["joy", "rage", "calm", "curious", "confused", "sacred"]

    for e in emotions:
        print(f"Triggering emotion sound: {e}")
        emitter.beep(e)
        time.sleep(1)
