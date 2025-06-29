import os
import yaml
import json
import re
from pathlib import Path
from collections import defaultdict

# === Konfiguration ===
PROJECT_ROOT = Path(__file__).resolve().parent
EVENT_DIR = PROJECT_ROOT / "content/events/intro"
HBS_DIR = EVENT_DIR / "hbs"
OUTPUT_FILE = PROJECT_ROOT / "obsidian/homion_data/event_graph.canvas"

def load_yaml_files(directory):
    data = {}
    for file in directory.glob("*.yaml"):
        with open(file, encoding="utf-8") as f:
            try:
                content = yaml.safe_load(f)
                if not content or "basic" not in content or "id" not in content["basic"]:
                    print(f"⚠️ Datei {file.name} hat kein gültiges 'basic.id'.")
                    continue
                event_id = content["basic"]["id"]
                data[event_id] = {
                    "file": file,
                    "data": content
                }
                print(f"✅ {file.name} → id: {event_id}")
            except Exception as e:
                print(f"❌ Fehler beim Parsen von {file.name}: {e}")
    return data

def extract_targets(option_block):
    targets = []
    if "next" in option_block and "target" in option_block["next"]:
        targets.append(option_block["next"]["target"])
    for key in ("if", "elif", "else"):
        if key in option_block:
            block = option_block[key]
            if isinstance(block, list):
                for cond in block:
                    tgt = cond.get("destination", {}).get("next", {}).get("target")
                    if tgt:
                        targets.append(tgt)
            elif isinstance(block, dict):
                tgt = block.get("destination", {}).get("next", {}).get("target")
                if tgt:
                    targets.append(tgt)
    return targets

# erkennt intro00, intro01, usw. – alles andere wird als "special" eingeordnet
def extract_layer(id_str):
    match = re.match(r"intro(\d{2})", id_str)
    if match:
        return int(match.group(1))
    return "special"

def build_canvas_data(event_data):
    nodes = []
    edges = []
    edge_count = 0
    spacing_x = 340
    spacing_y = 260

    layers = defaultdict(list)
    for event_id in event_data:
        layer = extract_layer(event_id)
        layers[layer].append(event_id)

    for y_index, layer in enumerate(sorted(layers.keys(), key=lambda x: (999 if x == "special" else int(x)))):
        events_in_layer = sorted(layers[layer])
        for x_index, event_id in enumerate(events_in_layer):
            content = event_data[event_id]["data"]
            title = content.get("basic", {}).get("title", "")

            yaml_abs = (EVENT_DIR / f"{event_id}.yaml").resolve().as_uri()
            hbs_abs = (HBS_DIR / f"{event_id}.hbs").resolve().as_uri()

            text = (
                f"**{event_id}**\n"
                f"*{title}*\n\n"
                f"[{event_id}.yaml]({yaml_abs})\n"
                f"[{event_id}.hbs]({hbs_abs})"
            )

            x = x_index * spacing_x
            y = y_index * spacing_y

            # Spezialevents weiter rechts platzieren
            if layer == "special":
                x += 500 + spacing_x * 4

            nodes.append({
                "id": event_id,
                "type": "text",
                "x": x,
                "y": y,
                "width": 260,
                "height": 140,
                "text": text
            })

    for event_id, info in event_data.items():
        content = info["data"]
        options = content.get("options", {})
        for opt_key, opt_content in options.items():
            targets = extract_targets(opt_content)
            for target_id in targets:
                if target_id in event_data:
                    edge_count += 1
                    edges.append({
                        "id": f"e{edge_count}",
                        "fromNode": event_id,
                        "toNode": target_id,
                        "type": "arrow"
                    })

    return {"nodes": nodes, "edges": edges, "version": "0.1.0"}

if __name__ == "__main__":
    print("⏳ Lade Events aus YAML...")
    events = load_yaml_files(EVENT_DIR)
    print(f"📦 {len(events)} Event-Dateien geladen.\n")

    print("🎨 Erzeuge Canvas...")
    canvas_data = build_canvas_data(events)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(canvas_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Canvas-Datei gespeichert: {OUTPUT_FILE}")
