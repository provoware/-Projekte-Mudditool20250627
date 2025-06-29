"""
contextmenu_mudschikato.py
--------------------------
Kontextmenü für Mudschikato – robust, laientauglich, Undo- und Logging-fähig.
Einsatz für Datei- und Moduloperationen.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QMenu, QAction, QVBoxLayout, QMessageBox
)
from PyQt6.QtGui import QIcon
from logging_mudschikato import log_event
from undo_mudschikato import UndoManager, UndoAction

class DateiListe(QListWidget):
    def __init__(self, undo_manager):
        super().__init__()
        self.undo_manager = undo_manager
        # Beispiel-Einträge (könnten echte Dateinamen sein)
        for i in range(5):
            self.addItem(f"Beispiel-Datei_{i+1}.txt")

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            return
        menu = QMenu(self)
        # Aktion: Datei löschen (mit Undo und Logging)
        del_action = QAction(QIcon.fromTheme("edit-delete"), "Löschen", self)
        del_action.triggered.connect(lambda: self.delete_item(item))
        menu.addAction(del_action)

        # Aktion: Info anzeigen
        info_action = QAction("Datei-Info", self)
        info_action.triggered.connect(lambda: self.show_info(item))
        menu.addAction(info_action)

        menu.exec(event.globalPos())

    def delete_item(self, item):
        name = item.text()
        idx = self.row(item)
        self.takeItem(idx)
        log_event(f"Datei gelöscht: {name}", "DateiListe", "INFO")

        def undo():
            self.insertItem(idx, name)
            log_event(f"Datei wiederhergestellt (Undo): {name}", "DateiListe", "UNDO")

        self.undo_manager.add(UndoAction(undo, description=f"Datei {name} gelöscht"))

    def show_info(self, item):
        QMessageBox.information(
            self,
            "Datei-Info",
            f"Name: {item.text()}\nPosition: {self.row(item)}",
        )

