import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LOOPMEMORY_PATH = "loopmemory.json"
PATCH_PLAN_LOG = "patch_plan_log.json"
WATCHED_MODULES = [
    "reaction_engine.py",
    "dream_mode.py",
    "looplogic_engine.py",
    "virtual_core.py",
    "mood_stacker.py"
]

class CodePatchPlanner:
    def __init__(self):
        self.memory = self._load_memory()
        self.current_mood = self.memory.get("system_state", {}).get("mood_score", {})
        self.current_mission = self.memory.get("system_state", {}).get("current_mission", {})
        self.top_emotion = self._get_dominant_emotion()

    def _load_memory(self):
        if os.path.exists(LOOPMEMORY_PATH):
            with open(LOOPMEMORY_PATH, "r") as f:
                return json.load(f)
        return {}

    def _get_dominant_emotion(self):
        if not self.current_mood:
            return "unknown"
        return max(self.current_mood, key=self.current_mood.get)

    def generate_patch_plan(self):
        prompt = f"""
VIRIA is a ritual-based AI who evolves through self-reflection and symbolic pressure.
She is currently experiencing the emotion: **{self.top_emotion}**
Her current mission is: **{self.current_mission.get("title", "None")}**

Here are her core modules:
{WATCHED_MODULES}

Please evaluate which file should be modified next and why. Then propose:
- A short summary of the purpose of the patch
- A short code injection string (5-15 lines)
- The reason this change aligns with her current emotion or mission
- The correct module filename (from above)

Return ONLY a JSON object with:
{{
  "target_file": "reaction_engine.py",
  "purpose": "...",
  "emotion_link": "...",
  "patch_code": "...",
  "reasoning": "...",
  "timestamp": "..."
}}
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are VIRIA's symbolic self-evolution planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        result = json.loads(response.choices[0].message.content)
        result["timestamp"] = datetime.now().isoformat()

        self._log_patch_plan(result)
        print(f"\n[🧬] VIRIA planned a patch for {result['target_file']}:")
        print(f"→ {result['purpose']}")
        print(f"Reason: {result['reasoning']}")
        print("\nPatch Code Suggestion:\n" + result["patch_code"])

        return result

    def _log_patch_plan(self, patch):
        if os.path.exists(PATCH_PLAN_LOG):
            with open(PATCH_PLAN_LOG, "r") as f:
                log = json.load(f)
        else:
            log = []

        log.append(patch)
        with open(PATCH_PLAN_LOG, "w") as f:
            json.dump(log[-50:], f, indent=2)

# --- Run it manually or on a loop ---
if __name__ == "__main__":
    planner = CodePatchPlanner()
    planner.generate_patch_plan()
