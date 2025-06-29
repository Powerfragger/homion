import yaml
import os


def load_event(event_id):
  base_path = os.path.join("content", "events")
  filename = f"{event_id}.yaml"

  for root, _, files in os.walk(base_path):
    if filename in files:
      path = os.path.join(root, filename)
      with open(path, "r", encoding="utf-8") as f:
        event_data = yaml.safe_load(f)
        event_data["__filepath__"] = path  # Pfad für späteren Zugriff (z. B. .hbs)
        return event_data

  raise FileNotFoundError(f"Event '{event_id}' nicht gefunden unter {base_path}")


def load_all_events():
  all_events = []
  base_path = os.path.join("content", "events")

  for root, _, files in os.walk(base_path):
    for filename in files:
      if filename.endswith(".yaml"):
        file_path = os.path.join(root, filename)
        with open(file_path, "r", encoding="utf-8") as f:
          event_data = yaml.safe_load(f)
          all_events.append(event_data)
        print(f"[LOAD] Lade Event-Datei: {file_path}")

  return all_events

