import yaml
import os


def load_event(event_id):
    path = os.path.join("content", "events", f"{event_id}.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_all_events():
    all_events = []
    path = os.path.join("content", "events")
    for filename in os.listdir(path):
        if filename.endswith(".yaml"):
            with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
                event_data = yaml.safe_load(f)
                all_events.append(event_data)
    print(f"[LOAD] Lade Event-Datei: {filename}")

    return all_events
