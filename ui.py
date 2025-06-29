import streamlit as st
from engine.loader import load_event
from engine.renderer import render_event
from engine.state import GameState
from main import resolve_next_event

st.markdown("""
<style>
/* Basis-Styling für alle Buttons */
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
  background-color: #800000 !important; /* Dunkelrot beim Hover */
  color: #fff !important;
  transform: scale(1.02);
  cursor: pointer;
}
</style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="HOMION", layout="wide")

# Initialisierung der Session
if "state" not in st.session_state:
    st.session_state.state = GameState("intro00")

state = st.session_state.state

event = load_event(state.current_event_id)
state.register_visit(event["basic"]["id"])
state.apply_effect(event.get("effect"))

# Metainfos
meta = event["basic"]
title = meta.get("title", "")
biome = meta.get("biome", "")
location = meta.get("location", "")

# Text vorbereiten
full_text = render_event(event, state)

# Layout
col1, col2 = st.columns([4, 1])

# Event-Text formatieren
formatted_text = full_text.replace("**", "<b>").replace("_", "<i>").replace("**", "</b>").replace("_", "</i>")

# Layout
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
        .option-button {
            animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
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

        # Button anzeigen ohne Hervorhebung
        if st.button(label, key=f"opt_{key}"):
            if state.check_condition(option.get("condition")):
                # Update des Imprints, wenn eine Entscheidung getroffen wird
                for imprint, value in option.get("effect", {}).get("imprint", {}).items():
                    state.update_imprint(imprint, value)

                # Event fortsetzen
                state.register_choice(event["basic"]["id"], key)
                state.current_event_id = resolve_next_event(state, option)
                st.rerun()
            else:
                st.warning("Diese Option ist aktuell nicht verfügbar.")

with col2:
    with st.expander("Entwickler-Status", expanded=False):
        st.markdown("**Flags:**")
        for k, v in state.flags.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("**Counter:**")
        for k, v in state.counters.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("**Resource:**")
        for k, v in state.resources.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("---")
        st.markdown("**Event-Überspringung:**")
        manual = st.text_input("Event-ID manuell setzen:")
        if st.button("Springe zu Event"):
            state.current_event_id = manual
            st.rerun()

        # **Neue Sektion für Imprints, Schwellenwerte und Mindsets**
        st.markdown("**Imprints:**")
        for k, v in state.imprint.items():
            st.markdown(f"- {k}: {v}")

        st.markdown("**Schwellenwert für Mindsets:**")
        for mindset, imprint in state.imprint.items():
            threshold = 3 * (len(state.mindsets) + 1)  # Berechne den Schwellenwert für das nächste Mindset
            st.markdown(f"- {mindset}: {threshold} (aktuell: {imprint})")

        st.markdown("**Mindsets:**")
        for mindset, active in state.mindsets.items():
            st.markdown(f"- {mindset}: {'Aktiv' if active else 'Inaktiv'}")
