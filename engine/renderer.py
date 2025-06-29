import os
from pybars import Compiler


def render_event(event_data, state):
  hbs_file = event_data["basic"]["text"]

  # 🔍 Hole Pfad zur Event-YAML-Datei und leite das hbs-Verzeichnis daraus ab
  if "__filepath__" not in event_data:
    raise ValueError(
      "Event enthält keinen '__filepath__'. Bitte sicherstellen, dass load_event() diesen setzt.")

  event_dir = os.path.dirname(event_data["__filepath__"])
  path = os.path.join(event_dir, "hbs", hbs_file)

  with open(path, "r", encoding="utf-8") as f:
    source = f.read()

  compiler = Compiler()
  template = compiler.compile(source)

  context = {
    **event_data,
    "flag": state.flags,
    "worldflag": state.worldflags,
    "counter": state.counters,
    "resource": state.resources,
    "visited": state.visited_events,
    "chosen": state.chosen_options,
    "imprint": state.imprints,
    "mindset": state.mindsets
  }

  return template(context)
