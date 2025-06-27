"""
dashboard_mudschikato.py
------------------------
Dashboard für Mudschikato.
- Zeigt Status/Statistiken aller Kernmodule (z. B. ToDos offen, Dateien im Papierkorb)
- Zeigt letzte Log-Einträge (max. 10)
- Schnellzugriff auf wichtige Aktionen (Backup, Papierkorb leeren, Hilfe)
- Übersichtlicher, laienfreundlicher Startbildschirm
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox
)
from logging_mudschikato import LOGFILE, log_event

TODODATEI = "mudschikato_todos.txt"
PAPIERKORB = "mudschikato_papierkorb"

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mudschikato Dashboard")
        self.layout = QVBoxLayout()
        
        # ToDo-Zähler
        self.todo_label = QLabel("Offene Aufgaben: ?")
        self.layout.addWidget(self.todo_label)
        # Papierkorb-Zähler
        self.papierkorb_label = QLabel("Dateien im Papierkorb: ?")
        self.layout.addWidget(self.papierkorb_label)
        # Letzte Log-Einträge
        self.layout.addWidget(QLabel("Letzte Aktionen:"))
        self.loglist = QListWidget()
        self.layout.addWidget(self.loglist)
        # Schnellzugriffe
        btn_ly = QHBoxLayout()
        self.btn_backup = QPushButton("Backup")
        self.btn_backup.clicked.connect(self.do_backup)
        btn_ly.addWidget(self.btn_backup)
        self.btn_clear_trash = QPushButton("Papierkorb leeren")
        self.btn_clear_trash.clicked.connect(self.clear_trash)
        btn_ly.addWidget(self.btn_clear_trash)
        self.btn_help = QPushButton("Hilfe")
        self.btn_help.clicked.connect(self.show_help)
        btn_ly.addWidget(self.btn_help)
        self.layout.addLayout(btn_ly)
        self.setLayout(self.layout)
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        # ToDos zählen
        open_tasks = 0
        if os.path.exists(TODODATEI):
            with open(TODODATEI, "r", encoding="utf-8") as f:
                for line in f:
                    if "\t" in line:
                        text, state = line.strip().split("\t")
                        if state == "0":
                            open_tasks += 1
        self.todo_label.setText(f"Offene Aufgaben: {open_tasks}")
        # Papierkorb zählen
        trash = 0
        if os.path.exists(PAPIERKORB):
            trash = len(os.listdir(PAPIERKORB))
        self.papierkorb_label.setText(f"Dateien im Papierkorb: {trash}")
        # Logs einlesen
        self.loglist.clear()
        if os.path.exists(LOGFILE):
            with open(LOGFILE, "r", encoding="utf-8") as f:
                lines = f.readlines()[-10:]
            for l in lines:
                self.loglist.addItem(l.strip())
    
    def do_backup(self):
        # Nur Dummy-Backup
        log_event("Backup ausgelöst (Dummy).", "Dashboard", "INFO")
        QMessageBox.information(self, "Backup", "Backup-Funktion ist noch ein Dummy.")

    def clear_trash(self):
        if not os.path.exists(PAPIERKORB):
            QMessageBox.information(self, "Papierkorb", "Papierkorb ist leer.")
            return
        num = len(os.listdir(PAPIERKORB))
        for fname in os.listdir(PAPIERKORB):
            try:
                os.remove(os.path.join(PAPIERKORB, fname))
            except Exception:
                pass
        log_event(f"Papierkorb geleert: {num} Datei(en) entfernt.", "Dashboard", "INFO")
        QMessageBox.information(self, "Papierkorb", f"{num} Datei(en) entfernt.")
        self.refresh_dashboard()

    def show_help(self):
        QMessageBox.information(self, "Hilfe", 
            "Mudschikato Dashboard\n\n"
            "- Zeigt Status aller Kernmodule\n"
            "- Schnellzugriffe: Backup, Papierkorb leeren\n"
            "- Log: letzte Aktionen\n"
            "\nWeitere Hilfe: www.provoware.de"
        )

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    dash = DashboardWidget()
    dash.show()
    app.exec()
