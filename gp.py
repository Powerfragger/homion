import subprocess
import os

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode

# Prüfen, ob wir in einem Git-Repo sind
if not os.path.isdir(".git"):
    print("❌ Dieses Verzeichnis ist kein Git-Repository.")
    exit(1)

# Änderungen prüfen
print("📦 Änderungen seit letztem Commit:")
run("git status -s")

# Eingabe der Commit-Message
commit_msg = input("📝 Änderungsnotiz für Commit (Enter = automatisch): ").strip()

if not commit_msg:
    commit_msg = "Update ohne Kommentar"

# Ausführen
print(f"\n🔄 Änderungen werden eingespielt mit Nachricht: \"{commit_msg}\"")

if run("git add .") != 0:
    exit(1)

if run(f'git commit -m "{commit_msg}"') != 0:
    print("⚠️ Commit evtl. übersprungen (nichts zu committen?)")

if run("git push") != 0:
    print("❌ Push fehlgeschlagen.")
    exit(1)

print("✅ Erfolgreich aktualisiert.")
