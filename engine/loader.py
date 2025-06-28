import yaml
import os


def load_event(event_id):
    path = os.path.join("content", "events", f"{event_id}.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
