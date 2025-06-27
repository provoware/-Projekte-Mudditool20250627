"""
logging_mudschikato.py
----------------------
Einfaches, robustes Logging-Modul für Mudschikato.
Ermöglicht zuverlässiges Mitschreiben von Ereignissen, Fehlern und User-Aktionen.
"""

import os
from datetime import datetime

LOGFILE = "mudschikato.log"

def log_event(event:str, context:str="", typ:str="INFO", print_console:bool=True):
    """
    Schreibt einen Log-Eintrag mit Zeitstempel, Typ, Kontext und Event.
    Args:
        event (str): Die zu loggende Nachricht
        context (str): Modul, Funktion oder Benutzerbereich
        typ (str): z.B. INFO, ERROR, WARNING, SUCCESS, DEBUG
        print_console (bool): Auch auf Konsole ausgeben? (Standard: True)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{typ}]"
    if context:
        entry += f" [{context}]"
    entry += f" {event}"
    try:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        if print_console:
            print(entry)
    except Exception as e:
        # Fallback bei Log-Fehler
        print(f"!! Fehler beim Logging: {e}")

# Test und Beispiel
if __name__ == "__main__":
    log_event("Mudschikato-Logging initialisiert.", "logging_mudschikato", "INFO")
    log_event("Test: Datei wurde erfolgreich erstellt.", "logging_mudschikato", "SUCCESS")
    log_event("Test: Dummy-Fehler aufgetreten.", "main", "ERROR")
