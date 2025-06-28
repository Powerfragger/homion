from engine.loader import load_event
from engine.renderer import render_event
from engine.state import GameState


def main():
    state = GameState(start_event="intro00")

    while True:
        event = load_event(state.current_event_id)
        state.register_visit(event["basic"]["id"])
        state.apply_effect(event.get("effect"))

        print("\n" + render_event(event, state))

        options = event.get("options", {})
        visible_options = [
            (key, opt) for key, opt in options.items()
            if state.check_condition(opt.get("condition"))
        ]

        if not visible_options:
            print("\n[Keine Optionen verfügbar. Spiel beendet.]")
            break

        for i, (key, opt) in enumerate(visible_options, 1):
            print(f"{i}) {opt['label']}")

        try:
            choice = int(input("Wähle: ")) - 1
            key, option = visible_options[choice]
        except (ValueError, IndexError):
            print("Ungültige Auswahl.")
            continue

        state.register_choice(event["basic"]["id"], key)
        state.apply_effect(option.get("effect"))
        state.current_event_id = option["next"]["target"]


if __name__ == "__main__":
    main()
