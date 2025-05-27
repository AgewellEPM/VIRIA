import json
import os
import time
import subprocess
from viria_mutator import ViriaMutator
from code_patch_planner import CodePatchPlanner

PROTECTED_FILES = ["main.py", "loopmemory.json"]
LAST_PATCH_PLAN = "patch_plan_log.json"

class AutoDeploy:
    def __init__(self):
        self.planner = CodePatchPlanner()
        self.mutator = ViriaMutator()

    def run_latest_patch(self):
        patch = self._load_last_patch()

        if not patch:
            print("[❌] No patch plan found.")
            return

        if patch["target_file"] in PROTECTED_FILES:
            print(f"[🛑] Mutation blocked — {patch['target_file']} is protected.")
            return

        print(f"\n[🧬] Applying patch to {patch['target_file']}")
        print(f"• Purpose: {patch['purpose']}")
        print(f"• Reason: {patch['reasoning']}")
        print("\nSuggested Code:\n" + patch["patch_code"])

        if not self._confirm_syntax(patch["patch_code"]):
            print("[❌] Patch failed syntax check. Aborting deployment.")
            return

        payload = {
            "after": "import json",  # crude, can be improved
            "code": patch["patch_code"]
        }

        self.mutator.mutate(
            target_file=patch["target_file"],
            mutation_type="inject_code",
            payload=payload,
            reason=patch.get("reasoning", "autodeploy")
        )

        self._restart_if_enabled()

    def _load_last_patch(self):
        if not os.path.exists(LAST_PATCH_PLAN):
            return None
        with open(LAST_PATCH_PLAN, "r") as f:
            plans = json.load(f)
        return plans[-1] if plans else None

    def _confirm_syntax(self, code):
        test_file = "temp_patch_test.py"
        with open(test_file, "w") as f:
            f.write(code)
        result = subprocess.run(["python3", "-m", "py_compile", test_file], capture_output=True)
        os.remove(test_file)
        return result.returncode == 0

    def _restart_if_enabled(self):
        RESTART_ON_DEPLOY = os.getenv("VIRIA_AUTORESTART", "false").lower() == "true"
        if RESTART_ON_DEPLOY:
            print("[♻️] Restarting VIRIA (run_viria.sh)...")
            os.system("pkill -f main.py")
            time.sleep(2)
            os.system("nohup bash run_viria.sh &")
        else:
            print("[✅] Patch applied — restart not triggered (VIRIA_AUTORESTART is false).")

# --- Optional CLI trigger ---
if __name__ == "__main__":
    deployer = AutoDeploy()
    deployer.run_latest_patch()
