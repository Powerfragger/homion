# === main.py (nur Spiellogik, kein UI) ===

from engine.loader import load_event, load_all_events
from engine.renderer import render_event
from engine.state import GameState


def resolve_next_target(next_data, state):
    if isinstance(next_data, dict):
        if "if" in next_data:
            if state.check_condition(next_data["if"].get("condition", {})):
                return next_data["if"]["destination"]["target"]

        if "elif" in next_data:
            elif_entry = next_data["elif"]
            elif_entries = [elif_entry] if isinstance(elif_entry, dict) else elif_entry
            for entry in elif_entries:
                if state.check_condition(entry.get("condition", {})):
                    return entry["destination"]["target"]

        if "else" in next_data:
            return next_data["else"]["destination"]["target"]

        if "target" in next_data:
            return next_data["target"]

    return None


def resolve_next_event(state, option):
    state.apply_effect(option.get("effect"))
    all_events = load_all_events()
    hook_target = state.get_hook_override_event(all_events)

    if hook_target:
        return hook_target
    else:
        next_info = option.get("next")
        return resolve_next_target(next_info, state)


def main():
    state = GameState(start_event="intro00")

    while True:
        event = load_event(state.current_event_id)
        state.register_visit(event["basic"]["id"])
        state.apply_effect(event.get("effect"))

        print("\n" + render_event(event, state))

        options = event.get("options", {})
        visible_options = []
        for key, opt in options.items():
            condition_met = state.check_condition(opt.get("condition"))
            if condition_met or opt.get("visible", False) is True:
                visible_options.append((key, opt, condition_met))

        if not visible_options:
            print("\n[Keine Optionen verfügbar. Spiel beendet.]")
            break

        for i, (key, opt, met) in enumerate(visible_options, 1):
            if met:
                print(f"{i}) {opt['label']}")
            else:
                print(f"{i}) {opt['label']} [NICHT VERFÜGBAR]")

        try:
            choice = int(input("Wähle: ")) - 1
            key, option, met = visible_options[choice]
            if not met:
                print("Diese Option ist aktuell nicht verfügbar.")
                continue
        except (ValueError, IndexError):
            print("Ungültige Auswahl.")
            continue

        state.register_choice(event["basic"]["id"], key)
        state.current_event_id = resolve_next_event(state, option)


if __name__ == "__main__":
    main()
