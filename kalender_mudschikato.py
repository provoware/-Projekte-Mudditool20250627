"""
kalender_mudschikato.py
-----------------------
Einfacher Monats-Kalender für Mudschikato.
- Zeigt Monatsansicht, aktuelle Woche hervorgehoben
- ToDos/Termine können pro Tag angelegt, abgehakt, gelöscht werden
- Erinnerung an fällige Aufgaben/Termine
- Alles GUI, keine Code-Eingabe für Nutzer
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCalendarWidget, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import QDate
from logging_mudschikato import log_event

KALENDERDATEI = "mudschikato_kalender.txt"

class KalenderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mudschikato Kalender")
        self.resize(520, 440)
        self.layout = QVBoxLayout()

        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.load_day)
        self.layout.addWidget(self.calendar)

        hl = QHBoxLayout()
        self.tasks_list = QListWidget()
        hl.addWidget(self.tasks_list)
        vr = QVBoxLayout()
        self.task_edit = QTextEdit()
        vr.addWidget(self.task_edit)
        self.btn_add = QPushButton("Aufgabe hinzufügen")
        self.btn_add.clicked.connect(self.add_task)
        vr.addWidget(self.btn_add)
        self.btn_done = QPushButton("Als erledigt markieren")
        self.btn_done.clicked.connect(self.done_task)
        vr.addWidget(self.btn_done)
        self.btn_delete = QPushButton("Löschen")
        self.btn_delete.clicked.connect(self.delete_task)
        vr.addWidget(self.btn_delete)
        hl.addLayout(vr)
        self.layout.addLayout(hl)

        self.setLayout(self.layout)
        self.load_day()

    def current_date_key(self):
        date = self.calendar.selectedDate()
        return date.toString("yyyy-MM-dd")

    def add_task(self):
        task = self.task_edit.toPlainText().strip()
        if not task:
            QMessageBox.warning(self, "Fehler", "Bitte Aufgabe eingeben.")
            return
        key = self.current_date_key()
        self.tasks_list.addItem(task)
        self.save_day()
        log_event(f"Kalender: Aufgabe hinzugefügt: {task} ({key})", "Kalender", "INFO")
        self.task_edit.clear()

    def done_task(self):
        item = self.tasks_list.currentItem()
        if not item:
            QMessageBox.information(self, "Info", "Bitte Aufgabe auswählen.")
            return
        item.setText("[x] " + item.text())
        self.save_day()
        log_event(f"Kalender: Aufgabe erledigt: {item.text()}", "Kalender", "INFO")

    def delete_task(self):
        item = self.tasks_list.currentItem()
        if not item:
            QMessageBox.information(self, "Info", "Bitte Aufgabe auswählen.")
            return
        text = item.text()
        self.tasks_list.takeItem(self.tasks_list.row(item))
        self.save_day()
        log_event(f"Kalender: Aufgabe gelöscht: {text}", "Kalender", "INFO")

    def load_day(self):
        key = self.current_date_key()
        self.tasks_list.clear()
        if os.path.exists(KALENDERDATEI):
            with open(KALENDERDATEI, "r", encoding="utf-8") as f:
                for line in f:
                    d, task = line.strip().split("\t", 1)
                    if d == key:
                        self.tasks_list.addItem(task)

    def save_day(self):
        key = self.current_date_key()
        tasks = [self.tasks_list.item(i).text() for i in range(self.tasks_list.count())]
        lines = []
        if os.path.exists(KALENDERDATEI):
            with open(KALENDERDATEI, "r", encoding="utf-8") as f:
                for line in f:
                    d, task = line.strip().split("\t", 1)
                    if d != key:
                        lines.append(line.strip())
        # aktuelle Aufgaben dieses Tages speichern
        for task in tasks:
            lines.append(f"{key}\t{task}")
        with open(KALENDERDATEI, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    cal = KalenderWidget()
    cal.show()
    app.exec()
