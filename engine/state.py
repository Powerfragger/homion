import operator


class GameState:
    def __init__(self, start_event):
        self.current_event_id = start_event
        self.flags = {}
        self.worldflags = {}
        self.counters = {}
        self.resources = {}
        self.visited_events = {}
        self.chosen_options = {}

        # Dynamische Speicherung von Imprints und Mindsets
        self.imprints = {}  # Speicherung aller Imprints (Werte werden dynamisch zugewiesen)
        self.mindsets = {}  # Speicherung der Mindsets (werden nach Erreichen des Schwellenwerts aktiviert)

    def update_imprints(self, imprint_name, value):
        """Erhöht den Zähler für ein Imprint und prüft, ob ein Mindset erreicht wurde."""
        # Imprint erhöhen
        self.imprints[imprint_name] = self.imprints.get(imprint_name, 0) + value

        # Berechne den Schwellenwert (immer 3 * Anzahl der bereits freigeschalteten Mindsets)
        threshold = 3 * (len(self.mindsets))  # 3, 6, 9 für den ersten, zweiten, dritten Mindset

        # Prüfe, ob der Zähler den Schwellenwert erreicht oder überschreitet, wird das Mindset aktiviert
        if self.imprints[imprint_name] >= threshold and not self.mindsets.get(imprint_name, False):
            self.mindsets[imprint_name] = True  # Setze das Imprint als Mindset
            print(f"Mindset {imprint_name} erreicht!")

    def get_imprint_value(self, imprint_name):
        """Gibt den aktuellen Wert des Imprints zurück."""
        return self.imprints.get(imprint_name, 0)

    def is_mindset_active(self, imprint_name):
        """Prüft, ob ein Mindset aktiv ist."""
        return self.mindsets.get(imprint_name, False)

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
      if isinstance(new_value, int):
        return old_value + new_value  # <- NEU: numerische Werte werden als delta interpretiert
      return int(new_value)  # fallback (z. B. „5“ als string)

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

        if "notflag" in condition:
            for k, v in condition["notflag"].items():
                if self.flags.get(k) == v:
                    return False

        if "worldflag" in condition:
            for k, v in condition["worldflag"].items():
                if self.worldflags.get(k) != v:
                    return False

        if "notworldflag" in condition:
            for k, v in condition["notworldflag"].items():
                if self.worldflags.get(k) == v:
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

        if "notvisited" in condition:
            for eid in condition["notvisited"]:
                if eid in self.visited_events:
                    return False

        if "chosen" in condition:
            for cid in condition["chosen"]:
                if cid not in self.chosen_options:
                    return False

        if "notchosen" in condition:
            for cid in condition["notchosen"]:
                if cid in self.chosen_options:
                    return False

        if "mindset" in condition:
            for k, v in condition["mindset"].items():
                if self.mindsets.get(k, False) != v:
                    return False

        if "notmindset" in condition:
            for k, v in condition["notmindset"].items():
                if self.mindsets.get(k, False) == v:
                    return False

        return True

    def evaluate_hook_condition(self, hook_cond):
        """Prüft komplexe Bedingungen in einem Hook (inkl. Operatoren wie '>= 3')."""
        import operator
        print("[HOOK-DEBUG] evaluate_hook_condition() wurde aufgerufen")

        ops = {
            "==": operator.eq,
            "!=": operator.ne,
            ">=": operator.ge,
            "<=": operator.le,
            ">": operator.gt,
            "<": operator.lt,
        }

        for typ in ("flag", "worldflag", "counter", "resource"):
            source = getattr(self, typ + "s")
            for key, val in hook_cond.get(typ, {}).items():
                current = source.get(key, 0 if typ in ("counter", "resource") else False)

                if isinstance(val, str) and any(val.startswith(op) for op in ops):
                    for op_symbol, op_func in ops.items():
                        if val.startswith(op_symbol):
                            try:
                                target = int(val[len(op_symbol):].strip())
                                print(f"[HOOK-EVAL] {typ}.{key}: {current} {op_symbol} {target}")
                                if not op_func(current, target):
                                    return False
                            except ValueError:
                                print(f"[HOOK-ERROR] Ungültiger Zahlenwert in Bedingung: '{val}' für Schlüssel '{key}'")
                                return False
                            break
                    else:
                        print(f"[HOOK-WARNUNG] Unbekannter Operator in Bedingung: '{val}' für Schlüssel '{key}'")
                        return False

                else:
                    # Direkter Vergleich, z. B. val = true oder 5
                    print(f"[HOOK-EVAL] {typ}.{key}: {current} == {val}")
                    if current != val:
                        return False

        return True

    def get_hook_override_event(self, all_events):
        """Sucht nach erstem gültigem Hook-Event."""
        for event in all_events:


            hook = event.get("hook")
            if not hook:

                continue

            if "condition" not in hook:

                continue

            if hook.get("once", False) and event["basic"]["id"] in self.visited_events:
                print("→ Hook bereits ausgelöst und 'once' aktiv.")
                continue

            print("→ Hook vorhanden, führe evaluate_hook_condition aus.")
            if self.evaluate_hook_condition(hook["condition"]):
                print("→ Bedingung erfüllt! Springe zu:", event["basic"]["id"])
                return event["basic"]["id"]
            else:
                print("→ Bedingung NICHT erfüllt.")

        return None
