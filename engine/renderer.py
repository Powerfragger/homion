import os
from pybars import Compiler


def render_event(event_data, state):
    hbs_file = event_data["basic"]["text"]
    path = os.path.join("content", "events", "hbs", hbs_file)

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
