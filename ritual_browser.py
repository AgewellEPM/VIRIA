import json
import os
from datetime import datetime

LOOPMEMORY_PATH = "loopmemory.json"
LOOPTRACE_PATH = "looptrace.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def display_rituals(memory):
    rituals = memory.get("rituals", [])
    if not rituals:
        print("[📭] No rituals stored yet.")
        return

    print("\n[🔮 ACTIVE RITUALS]")
    for r in rituals:
        print(f"• {r['name']} | Trigger: {r['trigger']} | Uses: {r['usage_count']} | Type: {r['importance']}")

def display_loops(memory):
    loops = memory.get("loops", {})
    if not loops:
        print("[🌪️] No loops tracked yet.")
        return

    print("\n[🔁 TOP LOOPED PHRASES]")
    top = sorted(loops.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    for phrase, data in top:
        print(f"• \"{phrase}\" → Count: {data['count']}, Energy: {round(data['loop_energy'], 2)}, Ritualized: {data['ritualized']}")

def display_recent_reactions(memory):
    reactions = memory.get("reactions", [])[-5:]
    if not reactions:
        print("[🫥] No reactions yet.")
        return

    print("\n[🎭 RECENT EMOTIONAL REACTIONS]")
    for r in reactions:
        print(f"• {r['timestamp']} | {r['emotion']} {r['emoji']} ← from {r['source']}")

def display_attention_state(memory):
    attention = memory.get("system_state", {}).get("attention", {})
    if attention:
        print("\n[👁️ ATTENTION STATUS]")
        print(f"• Last Phrase: {attention.get('last_phrase')}")
        print(f"• State: {attention.get('attention_state')}")
        print(f"• Silent for: {int(attention.get('seconds_since_last_phrase', 0))}s")

def display_environment_state(memory):
    env = memory.get("system_state", {}).get("environment", {})
    if env:
        print("\n[🌡️ ENVIRONMENT STATUS]")
        print(f"• Light: {env.get('light_level')} | Sound: {env.get('sound_level')} | Temp: {env.get('temperature')}")

def display_mood(memory):
    mood = memory.get("system_state", {}).get("mood_score", {})
    if mood:
        print("\n[🧠 MOOD STACK]")
        for k, v in mood.items():
            print(f"• {k}: {round(v, 2)}")

def display_ritual_by_name(memory, name):
    rituals = memory.get("rituals", [])
    match = next((r for r in rituals if r["name"] == name), None)
    if match:
        print(f"\n[🔍 DETAIL — {name}]")
        print(json.dumps(match, indent=2))
    else:
        print(f"[❌] Ritual '{name}' not found.")

def ritual_browser():
    memory = load_json(LOOPMEMORY_PATH)
    print("\n🧿 VIRIA RITUAL BROWSER")

    while True:
        print("\nOptions:")
        print("1. View active rituals")
        print("2. View top looped phrases")
        print("3. View recent emotional reactions")
        print("4. Show attention state")
        print("5. Show environment state")
        print("6. Show mood stack")
        print("7. Inspect ritual by name")
        print("8. Refresh")
        print("0. Exit")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            display_rituals(memory)
        elif choice == "2":
            display_loops(memory)
        elif choice == "3":
            display_recent_reactions(memory)
        elif choice == "4":
            display_attention_state(memory)
        elif choice == "5":
            display_environment_state(memory)
        elif choice == "6":
            display_mood(memory)
        elif choice == "7":
            ritual_name = input("Enter ritual name: ").strip()
            display_ritual_by_name(memory, ritual_name)
        elif choice == "8":
            memory = load_json(LOOPMEMORY_PATH)
            print("[♻️] Memory refreshed.")
        elif choice == "0":
            print("[🛑] Ritual browser closed.")
            break
        else:
            print("[❌] Invalid option.")

if __name__ == "__main__":
    ritual_browser()
