import json
from datetime import datetime
import os

# Paths
MEMORY_PATH = "loopmemory.json"

# Terminal color codes (optional)
COLOR = {
    "sacred": "\033[95m",   # Magenta
    "daily": "\033[94m",    # Blue
    "emergent": "\033[92m", # Green
    "normal": "\033[93m",   # Yellow
    "end": "\033[0m"
}

def load_rituals():
    if not os.path.exists(MEMORY_PATH):
        print("[!] loopmemory.json not found.")
        return []

    with open(MEMORY_PATH, "r") as f:
        data = json.load(f)
        return data.get("rituals", [])

def print_ritual_table(rituals):
    print("\n🌒  VIRIA RITUAL MAP")
    print("=" * 72)
    print(f"{'Name':<24} | {'Type':<10} | {'Uses':<5} | {'Last Triggered':<20}")
    print("-" * 72)

    for ritual in rituals:
        name = ritual.get("name", "unknown")[:24]
        importance = ritual.get("importance", "normal")
        usage = ritual.get("usage_count", 0)
        last = ritual.get("last_triggered", "—")

        color = COLOR.get(importance, "")
        reset = COLOR["end"]
        print(f"{color}{name:<24}{reset} | {importance:<10} | {usage:<5} | {last:<20}")

    print("=" * 72)
    print(f"Total rituals: {len(rituals)}")

def ritual_stats_summary(rituals):
    type_count = {}
    for r in rituals:
        i = r.get("importance", "normal")
        type_count[i] = type_count.get(i, 0) + 1

    print("\n📊 Ritual Importance Breakdown:")
    for typ, count in type_count.items():
        bar = "█" * count
        print(f"• {typ.title():<10}: {bar} ({count})")

if __name__ == "__main__":
    rituals = load_rituals()
    if not rituals:
        print("No rituals found.")
    else:
        print_ritual_table(rituals)
        ritual_stats_summary(rituals)
