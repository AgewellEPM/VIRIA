import random
import time
from datetime import datetime

# Optional: import TTS or sound logic
try:
    import pyttsx3
    TTS_ENABLED = True
except ImportError:
    TTS_ENABLED = False

# Emoji/Mood reaction map
REACTION_MAP = {
    "joy": ["😊", "🌞", "✨", "💖"],
    "rage": ["😠", "🔥", "💢", "🚨"],
    "calm": ["😌", "🌙", "💤", "🍃"],
    "curious": ["🤔", "🔍", "📚", "👁️"],
    "confused": ["😕", "❓", "🔄", "💭"],
    "sacred": ["🕯️", "🌌", "🔮", "🧿"],
}

# Optional ASCII templates
ASCII_FACES = {
    "joy": r"""
     (^‿^)
    """,
    "rage": r"""
     (╬ಠ益ಠ)
    """,
    "calm": r"""
     (－‿－) zZ
    """,
    "curious": r"""
     ( •_•)>⌐■-■
    """,
    "confused": r"""
     (°ロ°) !
    """,
    "sacred": r"""
     (◕‿◕✿)
    """,
}

class ReactionEngine:
    def __init__(self):
        self.tts = pyttsx3.init() if TTS_ENABLED else None
        self.last_reaction = None

    def react(self, emotion_type, source="loop"):
        if emotion_type not in REACTION_MAP:
            print(f"[⚠️ Unknown emotion]: {emotion_type}")
            return

        emoji = random.choice(REACTION_MAP[emotion_type])
        face = ASCII_FACES.get(emotion_type, "")
        timestamp = datetime.now().strftime("%H:%M:%S")

        print("\n[🎭 VIRIA REACTS]")
