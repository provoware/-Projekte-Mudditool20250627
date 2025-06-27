"""
todo_mudschikato.py
-------------------
Einfaches, robustes ToDo-/Aufgabenlisten-Modul für Mudschikato.
- Aufgaben anlegen, abhaken, löschen
- Persistente Speicherung in Textdatei
- Logging jeder Aktion
- Undo für die letzten 5 Aktionen (z. B. Aufgabe gelöscht oder abgehakt)
"""

import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox
)
from logging_mudschikato import log_event
from undo_mudschikato import UndoManager, UndoAction

TODODATEI = "mudschikato_todos.txt"

class ToDoWidget(QWidget):
    def __init__(self, undo_manager: UndoManager):
        super().__init__()
        self.undo_manager = undo_manager
        self.setWindowTitle("Mudschikato ToDo-Liste")
        self.resize(420, 350)
        self.layout = QVBoxLayout()
        self.input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Neue Aufgabe eingeben ...")
        self.btn_add = QPushButton("Hinzufügen")
        self.btn_add.clicked.connect(self.add_todo)
        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.btn_add)
        
        self.todolist = QListWidget()
        self.todolist.itemChanged.connect(self.todo_checked)
        
        self.btn_delete = QPushButton("Markierte löschen")
        self.btn_delete.clicked.connect(self.delete_selected)
        
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_action)
        
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.todolist)
        self.layout.addWidget(self.btn_delete)
        self.layout.addWidget(self.btn_undo)
        self.setLayout(self.layout)
        
        self.load_todos()
    
    def add_todo(self):
        task = self.input_field.text().strip()
        if not task:
            QMessageBox.warning(self, "Fehler", "Bitte eine Aufgabe eingeben!")
            return
        item = QListWidgetItem(task)
        item.setFlags(item.flags() | item.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0)  # Nicht abgehakt
        self.todolist.addItem(item)
        self.input_field.clear()
        self.save_todos()
        log_event(f"Neue Aufgabe hinzugefügt: {task}", "ToDo", "INFO")
        # Undo für Hinzufügen: Aufgabe entfernen
        def undo():
            self.todolist.takeItem(self.todolist.row(item))
            self.save_todos()
            log_event(f"Aufgabe entfernt (Undo): {task}", "ToDo", "UNDO")
        self.undo_manager.add(UndoAction(undo, description=f"Aufgabe: {task} hinzugefügt"))
    
    def todo_checked(self, item):
        # Wird aufgerufen, wenn Checkbox geändert wird
        state = "abgehakt" if item.checkState() else "offen"
        log_event(f"Aufgabe geändert: {item.text()} – Status: {state}", "ToDo", "INFO")
        self.save_todos()
        # Undo für Abhaken: Status zurücksetzen
        def undo():
            item.setCheckState(0 if item.checkState() else 2)
            self.save_todos()
            log_event(f"Aufgabe-Status geändert (Undo): {item.text()}", "ToDo", "UNDO")
        self.undo_manager.add(UndoAction(undo, description=f"Status: {item.text()}"))
    
    def delete_selected(self):
        selected = self.todolist.selectedItems()
        if not selected:
            QMessageBox.information(self, "Info", "Keine Aufgabe markiert.")
            return
        # Aufgaben und ihre Reihen merken (für Undo)
        removed = [(self.todolist.row(item), item.text(), item.checkState()) for item in selected]
        for item in selected:
            self.todolist.takeItem(self.todolist.row(item))
        self.save_todos()
        log_event(f"{len(removed)} Aufgaben gelöscht", "ToDo", "INFO")
        # Undo: Aufgaben wieder einfügen
        def undo():
            for idx, text, state in removed:
                item = QListWidgetItem(text)
                item.setFlags(item.flags() | item.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(state)
                self.todolist.insertItem(idx, item)
            self.save_todos()
            log_event(f"Aufgaben wiederhergestellt (Undo)", "ToDo", "UNDO")
        self.undo_manager.add(UndoAction(undo, description="Aufgaben gelöscht"))
    
    def undo_action(self):
        result = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", result)
    
    def save_todos(self):
        with open(TODODATEI, "w", encoding="utf-8") as f:
            for i in range(self.todolist.count()):
                item = self.todolist.item(i)
                f.write(f"{item.text()}\t{item.checkState()}\n")
    
    def load_todos(self):
        self.todolist.clear()
        if not os.path.exists(TODODATEI):
            return
        with open(TODODATEI, "r", encoding="utf-8") as f:
            for line in f:
                if "\t" in line:
                    text, state = line.strip().split("\t")
                    item = QListWidgetItem(text)
                    item.setFlags(item.flags() | item.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(int(state))
                    self.todolist.addItem(item)

if __name__ == "__main__":
    app = QApplication([])
    undo_mgr = UndoManager()
    win = ToDoWidget(undo_mgr)
    win.show()
    app.exec()
