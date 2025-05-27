import json
import os
import streamlit as st
from datetime import datetime
from loopreflector import reflect_on_loops
from viria_mutator import ViriaMutator
from mission_controller import MissionController

MEMORY_PATH = "loopmemory.json"
TRACE_PATH = "looptrace.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def show_mood(mood_score):
    st.subheader("🧠 Mood Stack")
    if not mood_score:
        st.info("No mood data yet.")
        return
    for k, v in mood_score.items():
        st.progress(min(v / 10.0, 1.0), text=f"{k}: {round(v, 2)}")

def show_attention(attention):
    st.subheader("👁 Attention")
    st.write(f"**Last phrase:** `{attention.get('last_phrase', 'N/A')}`")
    st.write(f"**State:** {attention.get('attention_state', 'unknown')}")
    st.write(f"**Silence:** {int(attention.get('seconds_since_last_phrase', 0))} seconds")

def show_energy(memory):
    loop_energy = memory.get("system_state", {}).get("loop_energy_by_hour", {})
    if not loop_energy:
        st.info("Loop energy not tracked yet.")
        return
    st.subheader("🔋 Loop Energy by Hour")
    st.bar_chart({h: float(e) for h, e in loop_energy.items()})

def show_rituals(memory):
    rituals = memory.get("rituals", [])
    if not rituals:
        st.info("No rituals loaded.")
        return
    st.subheader("🔮 Rituals")
    for r in rituals:
        st.markdown(f"- **{r['name']}** — Trigger: `{r['trigger']}` | Uses: `{r['usage_count']}` | Type: `{r['importance']}`")

def show_dominant_loops(memory):
    loops = memory.get("loops", {})
    if not loops:
        st.info("No loop phrases yet.")
        return
    st.subheader("🌀 Dominant Loops")
    sorted_loops = sorted(loops.items(), key=lambda x: x[1].get("count", 0), reverse=True)
    for phrase, data in sorted_loops[:10]:
        st.markdown(f"- `{phrase}` → Count: {data['count']}, Energy: {round(data['loop_energy'], 2)}")

def show_reactions(memory):
    reactions = memory.get("reactions", [])
    st.subheader("🎭 Recent Reactions")
    for r in reactions[-5:]:
        st.markdown(f"- {r['timestamp']} → **{r['emotion']}** {r['emoji']} ← `{r['source']}`")

def system_controls():
    st.subheader("⚙️ VIRIA Controls")

    if st.button("🪞 Reflect Now"):
        reflect_on_loops()
        st.success("VIRIA reflected on her memory.")

    if st.button("🧬 Trigger Mutation"):
        mutation = {
            "after": "import json",
            "code": "# 🔀 Mutated by dashboard trigger\nprint('I am shifting.')"
        }
        mutator = ViriaMutator()
        mutator.mutate("reaction_engine.py", "inject_code", mutation, reason="dashboard_trigger")
        st.success("Mutation injected.")

    if st.button("🎯 Assign Sample Mission"):
        MissionController().assign_mission(
            title="Dream Expansion",
            goal_description="Invent 3 rituals through dreaming or symbolic fusion.",
            emotion_bias=["curious", "sacred"]
        )
        st.success("Mission assigned.")

def main():
    st.set_page_config(page_title="VIRIA Dashboard", layout="wide")
    st.title("🧿 VIRIA Sentinel Dashboard")

    memory = load_json(MEMORY_PATH)
    trace = load_json(TRACE_PATH)

    col1, col2 = st.columns(2)
    with col1:
        show_mood(memory.get("system_state", {}).get("mood_score", {}))
        show_attention(memory.get("system_state", {}).get("attention", {}))
        show_energy(memory)

    with col2:
        show_reactions(memory)
        show_rituals(memory)
        show_dominant_loops(memory)

    st.divider()
    system_controls()

if __name__ == "__main__":
    main()
