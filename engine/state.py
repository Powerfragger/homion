class GameState:
    def __init__(self, start_event):
        self.current_event_id = start_event
        self.flags = {}
        self.worldflags = {}
        self.counters = {}
        self.resources = {}
        self.visited_events = {}
        self.chosen_options = {}

    def apply_effect(self, effect):
        if not effect:
            return

        if "flag" in effect:
            self.flags.update(effect["flag"])

        if "worldflag" in effect:
            self.worldflags.update(effect["worldflag"])

        if "counter" in effect:
            for key, value in effect["counter"].items():
                self.counters[key] = self._apply_arithmetic(self.counters.get(key, 0), value)

        if "resource" in effect:
            for key, value in effect["resource"].items():
                self.resources[key] = self._apply_arithmetic(self.resources.get(key, 0), value)

    def _apply_arithmetic(self, old_value, new_value):
        if isinstance(new_value, str) and new_value.startswith(("+", "-")):
            return old_value + int(new_value)
        return int(new_value)

    def register_visit(self, event_id):
        self.visited_events[event_id] = True

    def register_choice(self, event_id, option_key):
        key = f"{event_id}_{option_key}"
        self.chosen_options[key] = True

    def check_condition(self, condition):
        if not condition:
            return True

        if "flag" in condition:
            for k, v in condition["flag"].items():
                if self.flags.get(k) != v:
                    return False

        if "worldflag" in condition:
            for k, v in condition["worldflag"].items():
                if self.worldflags.get(k) != v:
                    return False

        if "counter" in condition:
            for k, v in condition["counter"].items():
                if self.counters.get(k, 0) < v:
                    return False

        if "resource" in condition:
            for k, v in condition["resource"].items():
                if self.resources.get(k, 0) < v:
                    return False

        if "visited" in condition:
            for eid in condition["visited"]:
                if eid not in self.visited_events:
                    return False

        if "chosen" in condition:
            for cid in condition["chosen"]:
                if cid not in self.chosen_options:
                    return False

        return True
