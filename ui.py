import streamlit as st
from engine.loader import load_event
from engine.renderer import render_event
from engine.state import GameState
from main import resolve_next_event

st.set_page_config(page_title="HOMION", layout="wide")

# 🎬 Startbildschirm anzeigen, falls Spiel noch nicht initialisiert
if "state" not in st.session_state:
    st.markdown("""
    <style>
    html, body, .main, .block-container {
        overflow: hidden !important;
    }

    .homion-title {
        text-align: center;
        font-size: 4rem;
        color: #8c1f1f;
        font-family: "Share Tech Mono", monospace;
        font-weight: bold;
        text-shadow: 1px 1px 0 #000, -1px -1px 0 #000;
        margin-bottom: 0.2em;
    }

    .homion-subtitle {
        text-align: center;
        font-size: 1.5rem;
        color: #bb6666;
        font-family: "Share Tech Mono", monospace;
        margin-bottom: 2em;
    }

    .homion-button-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1em;
        margin-top: 2em;
    }

    .stButton>button {
        width: 200px;
        font-size: 1.1em;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
    </style>

    <div class='homion-title'>HOMION</div>
    <div class='homion-subtitle'>menschlich</div>
    <div class='homion-button-container'>
    """, unsafe_allow_html=True)

    if st.button("▶️ Neues Spiel"):
        st.session_state.state = GameState("intro00")
        st.rerun()
    st.button("🔒 Laden", disabled=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 🎮 Spiel läuft: CSS für Buttons und Anzeige
st.markdown("""
<style>
/* Basis-Styling für Buttons */
.stButton button {
  background-color: #222 !important;
  color: #EEE !important;
  border: 1px solid #444 !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  font-family: "Share Tech Mono", monospace !important;
  font-size: 1em !important;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

/* Hover-Effekt */
.stButton button:hover {
  background-color: #800000 !important;
  color: #fff !important;
  transform: scale(1.02);
  cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ⏳ Zustand und Event laden
state = st.session_state.state
event = load_event(state.current_event_id)
state.register_visit(event["basic"]["id"])
state.apply_effect(event.get("effect"))

# 📋 Metadaten
meta = event["basic"]
title = meta.get("title", "")
biome = meta.get("biome", "")
location = meta.get("location", "")
full_text = render_event(event, state)

# ➕ HTML-Markup für fett/kursiv (von dir)
formatted_text = full_text.replace("**", "<b>").replace("__", "<b>").replace("*", "<i>").replace("_", "<i>").replace("</b><b>", "").replace("</i><i>", "")

# 🧱 Layout
col1, col2 = st.columns([4, 1])

with col1:
    st.markdown("""
        <style>
        .meta-info {
            font-size: 0.8em;
            color: gray;
            margin-bottom: 4px;
        }
        .textbox {
            border: 1px solid #444;
            padding: 1rem;
            height: 400px;
            overflow-y: auto;
            background-color: #111;
            color: #EEE;
            font-family: "Share Tech Mono", monospace;
            font-size: 1.05em;
            white-space: pre-wrap;
        }
        .textbox::-webkit-scrollbar {
            width: 6px;
        }
        .textbox::-webkit-scrollbar-thumb {
            background: #666;
            border-radius: 3px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='meta-info'>{title} | {biome} | {location}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='textbox' id='storybox'>{formatted_text}</div>", unsafe_allow_html=True)

    st.markdown("""
        <script>
        const box = window.parent.document.getElementById("storybox");
        if (box) box.scrollTop = 0;
        </script>
    """, unsafe_allow_html=True)

    options = event.get("options", {})
    visible_options = [
        (key, opt) for key, opt in options.items()
        if state.check_condition(opt.get("condition")) or opt.get("visible", False) is True
    ]

    for key, option in visible_options:
        label = option.get("label", f"[{key}]")

        if st.button(label, key=f"opt_{key}"):
            if state.check_condition(option.get("condition")):
                for imprint, value in option.get("effect", {}).get("imprint", {}).items():
                    state.update_imprints(imprint, value)

                state.register_choice(event["basic"]["id"], key)
                state.current_event_id = resolve_next_event(state, option)
                st.rerun()
            else:
                st.warning("Diese Option ist aktuell nicht verfügbar.")

with col2:
    with st.expander("🛠 Entwickler-Status", expanded=False):
        st.markdown("### 🔍 Variablen")

        st.markdown("**Flags:**")
        for k, v in state.flags.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("**Resources:**")
        for k, v in state.resources.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("**Counters:**")
        for k, v in state.counters.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("**Imprints:**")
        for k, v in state.imprints.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("**Mindsets:**")
        for k, v in state.mindsets.items():
            st.markdown(f"- {k}: {'Aktiv' if v else 'Inaktiv'}")

        st.markdown("**Aktueller Schwellwert:**")
        st.markdown(f"- {3 * len(state.mindsets)}")

        st.markdown("---")
        st.markdown("### ⏩ Direkter Sprung")

        manual = st.text_input("Event-ID manuell setzen:")
        if st.button("Springe zu Event"):
            state.current_event_id = manual
            st.rerun()

        st.markdown("---")
        st.markdown("### 📜 Log (letzte 20 Einträge)")

        visited = list(state.visited_events)[-20:] if isinstance(state.visited_events, dict) else []
        chosen = list(state.chosen_options)[-20:] if isinstance(state.chosen_options, dict) else []

        visited_log = "<br>".join(visited) if visited else "–"
        chosen_log = "<br>".join(chosen) if chosen else "–"

        st.markdown("**Visited Events:**")
        st.markdown(
            f"<div style='max-height: 120px; overflow-y: auto; background-color: #111; padding: 0.5em; border: 1px solid #444;'>{visited_log}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("**Chosen Options:**")
        st.markdown(
            f"<div style='max-height: 120px; overflow-y: auto; background-color: #111; padding: 0.5em; border: 1px solid #444;'>{chosen_log}</div>",
            unsafe_allow_html=True,
        )
