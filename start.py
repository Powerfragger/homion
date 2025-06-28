import streamlit as st
import os
from engine.loader import load_event
from engine.renderer import render_event
from engine.state import GameState

st.set_page_config(page_title="HOMION", layout="wide")

# Initialisierung der Session
if "state" not in st.session_state:
    st.session_state.state = GameState("intro00")

state = st.session_state.state

event = load_event(state.current_event_id)
state.register_visit(event["basic"]["id"])
state.apply_effect(event.get("effect"))

# Metainfos
title = event["basic"].get("title", "")
biome = event["basic"].get("biome", "")
location = event["basic"].get("location", "")

# Text vorbereiten
full_text = render_event(event, state)

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
        .textbox span[title] {
            text-decoration: underline dotted;
            color: #9cf;
            cursor: help;
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
    st.markdown(f"<div class='textbox' id='storybox'>{full_text}</div>", unsafe_allow_html=True)

    st.markdown("""
        <script>
        const box = window.parent.document.getElementById("storybox");
        if (box) box.scrollTop = 0;
        </script>
    """, unsafe_allow_html=True)

    options = event.get("options", {})
    visible_options = [
        (key, opt) for key, opt in options.items()
        if state.check_condition(opt.get("condition"))
    ]

    for key, option in visible_options:
        if st.button(option["label"], key=f"opt_{key}"):
            state.register_choice(event["basic"]["id"], key)
            state.apply_effect(option.get("effect"))
            state.current_event_id = option["next"]["target"]
            st.rerun()

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
