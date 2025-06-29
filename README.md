# Mudschikato - Struktur & Hilfstool 2025

Dieses Projekt bietet die Mudschikato-Oberfläche sowie diverse Hilfsmodule.

## Setup

1. **Repository klonen**
   ```bash
   git clone <REPO-URL>
   cd <REPO-Verzeichnis>
   ```
2. **Virtuelle Umgebung einrichten und Abhängigkeiten installieren**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # unter Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **GUI starten**
   ```bash
   python mainwindow_mudschikato.py
   ```

Benötigte Pakete sind unter anderem **PyQt6** (für die Oberfläche) und **pygame** (für den integrierten Mediaplayer).

## Weiterführende Laienvorschläge
- Stellen Sie sicher, dass Python und `pip` installiert sind. Auf vielen Systemen kann `python3 --version` dies prüfen.
- Bei Problemen mit der virtuellen Umgebung hilft es oft, die Konsole neu zu starten und sie erneut zu aktivieren.
- Weitere Informationen finden Sie im Changelog und in den einzelnen Modulen.
