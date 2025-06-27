# -Projekte-Mudditool20250627

Mudditool (in den Modulen auch "Mudschikato" genannt) ist ein kleines Hilfsprogramm mit mehreren Python-Modulen und einer optionalen Electron-Oberfläche. Es erleichtert den Umgang mit Dateien, Medien und weiteren Werkzeugen.

## Installation

1. Repository klonen und optional eine virtuelle Umgebung anlegen.
2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
   (Falls die Datei fehlt, können die Module einzeln installiert werden.)
3. Für die Electron-Oberfläche Node-Pakete installieren:
   ```bash
   npm install
   ```
4. Electron-GUI starten:
   ```bash
   npm start
   ```

## Nutzung

Die Hauptoberfläche startest du mit:

```bash
python3 mainwindow_mudschikato.py
```

Jedes Modul lässt sich auch einzeln ausführen.

## Funktionen

- Rückgängig-Funktion über `undo_mudschikato.py`.
- Ereignisprotokollierung in `mudditool.log`.

## Weiterführende Laienvorschläge

- Halte Python und Node stets aktuell.
- Nutze virtuelle Umgebungen, um Abhängigkeitskonflikte zu vermeiden.
- Passe die Log-Stufe in `logging_mudschikato.py` nach Bedarf an.
- Dokumentiere deine Änderungen regelmäßig mit sinnvollen Git-Commits.
- Lege eine `.gitignore` an, damit Logdateien und `node_modules` nicht versioniert werden.
- Pflege `requirements.txt`, falls du weitere Bibliotheken nutzt.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe die Datei `LICENSE` für Details.

