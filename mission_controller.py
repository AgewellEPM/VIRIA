import json
import os
from datetime import datetime

LOOPMEMORY_PATH = "loopmemory.json"
MISSION_LOG_PATH = "mission_log.json"

class MissionController:
    def __init__(self):
        self.memory = self._load_memory()
        self._ensure_mission_structure()

    def _load_memory(self):
        if os.path.exists(LOOPMEMORY_PATH):
            with open(LOOPMEMORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def _save_memory(self):
        with open(LOOPMEMORY_PATH, "w") as f:
            json.dump(self.memory, f, indent=2)

    def _ensure_mission_structure(self):
        self.memory.setdefault("system_state", {})
        self.memory["system_state"].setdefault("current_mission", None)
        self.memory["system_state"].setdefault("mission_history", [])
        self._save_memory()

    def assign_mission(self, title, goal_description, success_conditions=None, emotion_bias=None):
        mission = {
            "title": title,
            "goal": goal_description,
            "assigned_at": datetime.now().isoformat(),
            "success_conditions": success_conditions or [],
            "emotion_bias": emotion_bias or [],
            "status": "active"
        }

        self.memory["system_state"]["current_mission"] = mission
        self.memory["system_state"]["mission_history"].append(mission)
        self._save_memory()
        self._log_mission(mission)

        print(f"\n[🎯] Mission Assigned: {title}")
        print(f"Goal: {goal_description}")
        if success_conditions:
            print(f"Conditions: {success_conditions}")
        if emotion_bias:
            print(f"Emotional Tilt: {emotion_bias}")

    def _log_mission(self, mission):
        if os.path.exists(MISSION_LOG_PATH):
            with open(MISSION_LOG_PATH, "r") as f:
                log = json.load(f)
        else:
            log = []

        log.append(mission)
        with open(MISSION_LOG_PATH, "w") as f:
            json.dump(log[-100:], f, indent=2)

    def get_active_mission(self):
        return self.memory.get("system_state", {}).get("current_mission", None)

    def complete_mission(self):
        mission = self.get_active_mission()
        if not mission:
            print("[⚠️] No active mission.")
            return

        mission["completed_at"] = datetime.now().isoformat()
        mission["status"] = "complete"
        self.memory["system_state"]["current_mission"] = None
        self._save_memory()

        print(f"[🏁] Mission Complete: {mission['title']}")

# --- Example Usage ---
if __name__ == "__main__":
    mc = MissionController()

    print("\n[🧭 VIRIA Mission System]")
    print("1. Assign mission")
    print("2. Show current mission")
    print("3. Complete mission")
    print("0. Exit")

    while True:
        choice = input("\n> ").strip()
        if choice == "1":
            title = input("Title: ")
            goal = input("Goal: ")
            emotions = input("Emotional bias (comma-separated, optional): ").strip().split(",")
            mc.assign_mission(title, goal, emotion_bias=[e.strip() for e in emotions if e.strip()])
        elif choice == "2":
            mission = mc.get_active_mission()
            print(json.dumps(mission, indent=2) if mission else "[🚫] No mission active.")
        elif choice == "3":
            mc.complete_mission()
        elif choice == "0":
            break
