# Mudschikato Struktur & Hilfstool 2025

Dieses Repository enthält eine Sammlung einfacher Hilfstools mit einer gemeinsamen
PyQt6-Oberfläche. Optional kann die Anwendung auch über Electron gestartet werden.

## Installation

### Python-Abhängigkeiten
1. Python 3.8 oder neuer installieren.
2. Anschließend benötigte Pakete laden:
   ```bash
   pip install PyQt6 pygame psutil
   ```
   *Hinweis:* Ein virtuelles Environment (`python -m venv venv`) ist empfehlenswert, aber
   nicht zwingend.

### Node-/Electron-Abhängigkeiten (optional)
1. Node.js 18+ installieren.
2. Die im Projekt enthaltene Setup-Datei einrichten:
   ```bash
   bash auto_setup_validate.sh
   ```
   Dadurch werden `npm install` sowie Playwright-Tests ausgeführt und die
   benötigten Dateien (z.B. `src/main.js`) angelegt.
3. Alternativ können die Abhängigkeiten manuell installiert werden:
   ```bash
   npm install
   ```
   Start der Electron-Oberfläche:
   ```bash
   npm start
   ```

## Verwendung
Die klassische GUI lässt sich direkt über Python starten:
```bash
python mainwindow_mudschikato.py
```
Einzelne Module können auch separat ausgeführt werden (z.B. `python todo_mudschikato.py`).

## Tipps für Einsteiger
- Im **Downloads-Manager** können Dateien gefahrlos sortiert werden; gelöschte
  Elemente landen in einem Wiederherstellungsordner.
- Das **Feedback/Notizen**-Modul eignet sich für schnelle Gedanken.
  Änderungen lassen sich kurzfristig rückgängig machen (Undo).
- Die **Wiki**- und **Settings**-Tabs bieten einen zentralen Ort für Anleitungen
  und persönliche Einstellungen.
- Geplante Backups (Dashboard-Button) sind noch nicht implementiert –
  regelmäßige manuelle Sicherungen sind empfehlenswert.

Viel Spaß beim Ausprobieren!
