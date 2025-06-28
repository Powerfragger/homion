HOMION – Textbasiertes RPG

Dies ist das interaktive Entwicklungsprojekt HOMION, ein narratives, textbasiertes RPG auf Basis von Python, YAML, Handlebars und Streamlit.

🔗 Öffentliche Vorschau
Die aktuelle Version ist jederzeit online erreichbar unter:
👉 https://homion-jmbwvrdpdeqnumtxykxquy.streamlit.app/

🧰 Lokale Entwicklung starten
Im Projektverzeichnis:

    streamlit run start.py

🔄 Änderungen pushen (GitHub + Streamlit Cloud)

    # 1. Änderungen speichern
    git add .

    # 2. Commit mit Nachricht
    git commit -m "Kurzbeschreibung deiner Änderungen"

    # 3. Push zur Cloud (Streamlit aktualisiert automatisch)
    git push

🗂️ Verzeichnisstruktur (Kurzüberblick)

- engine/ – Spiellogik, State-Management, Loader und Renderer
- content/events/ – YAML-Eventdaten
- content/events/hbs/ – Handlebars-Templates für Texte
- start.py – Streamlit-UI zum Testen & Präsentieren
- main.py – CLI-Version (optional)
- requirements.txt – benötigte Python-Pakete

🧪 Entwickler-Hinweis
In der Streamlit-UI kann per "Entwickler-Status"-Panel der Zustand (Flags, Counter etc.) live eingesehen werden.

© Powerfragger – 2025
