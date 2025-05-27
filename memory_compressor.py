import os
import json
from datetime import datetime

MEMORY_PATH = "loopmemory.json"
TRACE_PATH = "looptrace.json"
OUTPUT_DIR = "compressed_memory"

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def compress_loops(memory):
    loops = memory.get("loops", {})
    data = []

    for phrase, details in loops.items():
        entry = {
            "input": f"Loop phrase: {phrase}",
            "emotion": "unknown",
            "count": details.get("count", 0),
            "energy": details.get("loop_energy", 0.0),
            "ritualized": details.get("ritualized", False),
            "output": f"Emotion: Loop of {phrase} repeated {details.get('count', 0)} times"
        }
        data.append(entry)

    return data

def compress_rituals(memory):
    rituals = memory.get("rituals", [])
    return [{
        "input": f"Trigger: {r['trigger']}",
        "output": f"Invoke ritual: {r['name']} (type: {r['importance']})"
    } for r in rituals]

def compress_emotions(memory):
    reactions = memory.get("reactions", [])
    return [{
        "input": f"Triggered by: {r['source']}",
        "output": f"Emotion: {r['emotion']} ({r['emoji']})"
    } for r in reactions[-20:]]

def compress_mood_stack(memory):
    mood = memory.get("system_state", {}).get("mood_score", {})
    return [{
        "input": f"Emotions over time",
        "output": f"Mood stack: {json.dumps(mood)}"
    }]

def compress_attention(memory):
    attn = memory.get("system_state", {}).get("attention", {})
    if not attn:
        return []
    return [{
        "input": f"Last phrase: {attn.get('last_phrase')}",
        "output": f"Attention state: {attn.get('attention_state')} after {int(attn.get('seconds_since_last_phrase', 0))}s"
    }]

def save_jsonl(name, records):
    path = os.path.join(OUTPUT_DIR, f"{name}.jsonl")
    with open(path, "w") as f:
        for entry in records:
            f.write(json.dumps(entry) + "\n")
    print(f"[🧠] Saved {len(records)} entries to {path}")

def compress_all():
    ensure_output_dir()
    with open(MEMORY_PATH, "r") as f:
        memory = json.load(f)

    save_jsonl("loops", compress_loops(memory))
    save_jsonl("rituals", compress_rituals(memory))
    save_jsonl("emotions", compress_emotions(memory))
    save_jsonl("mood", compress_mood_stack(memory))
    save_jsonl("attention", compress_attention(memory))

    print("\n✅ Memory compression complete.")

# --- Optional CLI ---
if __name__ == "__main__":
    compress_all()
