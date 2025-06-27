"""
wiki_mudschikato.py
-------------------
Mini-Wiki-/Info-Modul für Mudschikato.
- Strukturiert nach Themen – Einträge – Details
- Suchen, Hinzufügen, Bearbeiten, Löschen, Undo
- Persistente Speicherung als wiki.json
- Keine Codeeingabe für User
"""

import os, json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton,
    QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from undo_mudschikato import UndoManager, UndoAction

WIKIFILE = "mudschikato_wiki.json"

class WikiWidget(QWidget):
    def __init__(self, undo_manager: UndoManager):
        super().__init__()
        self.undo_manager = undo_manager
        self.setWindowTitle("Wiki / Info & FAQ")
        self.resize(650, 500)
        self.layout = QVBoxLayout()
        
        # Suchfeld
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Suche im Wiki ...")
        self.search_field.textChanged.connect(self.refresh_themes)
        self.layout.addWidget(self.search_field)
        
        # Themenliste (Level 1)
        self.themes_list = QListWidget()
        self.themes_list.currentItemChanged.connect(self.load_entries)
        self.layout.addWidget(QLabel("Themen:"))
        self.layout.addWidget(self.themes_list)
        
        # Einträge zu Thema (Level 2)
        self.entries_list = QListWidget()
        self.entries_list.currentItemChanged.connect(self.load_details)
        self.layout.addWidget(QLabel("Einträge:"))
        self.layout.addWidget(self.entries_list)
        
        # Detail-Anzeige/Bearbeitung (Level 3)
        self.detail_edit = QTextEdit()
        self.layout.addWidget(QLabel("Details:"))
        self.layout.addWidget(self.detail_edit)
        
        # Buttons
        btn_ly = QHBoxLayout()
        self.btn_add_theme = QPushButton("Thema hinzufügen")
        self.btn_add_theme.clicked.connect(self.add_theme)
        btn_ly.addWidget(self.btn_add_theme)
        self.btn_del_theme = QPushButton("Thema löschen")
        self.btn_del_theme.clicked.connect(self.delete_theme)
        btn_ly.addWidget(self.btn_del_theme)
        self.btn_add_entry = QPushButton("Eintrag hinzufügen")
        self.btn_add_entry.clicked.connect(self.add_entry)
        btn_ly.addWidget(self.btn_add_entry)
        self.btn_del_entry = QPushButton("Eintrag löschen")
        self.btn_del_entry.clicked.connect(self.delete_entry)
        btn_ly.addWidget(self.btn_del_entry)
        self.btn_save_detail = QPushButton("Details speichern")
        self.btn_save_detail.clicked.connect(self.save_detail)
        btn_ly.addWidget(self.btn_save_detail)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_action)
        btn_ly.addWidget(self.btn_undo)
        self.layout.addLayout(btn_ly)

        self.setLayout(self.layout)
        self.data = self.load_wiki()
        self.refresh_themes()
    
    def load_wiki(self):
        if os.path.exists(WIKIFILE):
            try:
                with open(WIKIFILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # Struktur: {Thema: {Eintrag: Details}}
        return {}
    
    def save_wiki(self):
        with open(WIKIFILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
    
    def refresh_themes(self):
        search = self.search_field.text().lower()
        self.themes_list.clear()
        for theme in sorted(self.data.keys()):
            if not search or search in theme.lower():
                self.themes_list.addItem(theme)
        self.entries_list.clear()
        self.detail_edit.clear()
    
    def load_entries(self, curr, prev):
        self.entries_list.clear()
        self.detail_edit.clear()
        if not curr:
            return
        theme = curr.text()
        for entry in sorted(self.data.get(theme, {}).keys()):
            self.entries_list.addItem(entry)
    
    def load_details(self, curr, prev):
        self.detail_edit.clear()
        theme = self.current_theme()
        entry = self.current_entry()
        if theme and entry:
            self.detail_edit.setText(self.data[theme][entry])
    
    def current_theme(self):
        item = self.themes_list.currentItem()
        return item.text() if item else None
    
    def current_entry(self):
        item = self.entries_list.currentItem()
        return item.text() if item else None
    
    def add_theme(self):
        theme, ok = self.get_text("Neues Thema anlegen:", "Thema")
        if ok and theme:
            prev = dict(self.data)
            self.data[theme] = {}
            self.save_wiki()
            self.refresh_themes()
            def undo():
                self.data = prev
                self.save_wiki()
                self.refresh_themes()
            self.undo_manager.add(UndoAction(undo, description=f"Thema {theme} hinzugefügt"))
    
    def delete_theme(self):
        theme = self.current_theme()
        if not theme:
            return
        prev = dict(self.data)
        del self.data[theme]
        self.save_wiki()
        self.refresh_themes()
        def undo():
            self.data = prev
            self.save_wiki()
            self.refresh_themes()
        self.undo_manager.add(UndoAction(undo, description=f"Thema {theme} gelöscht"))
    
    def add_entry(self):
        theme = self.current_theme()
        if not theme:
            return
        entry, ok = self.get_text("Neuen Eintrag anlegen:", "Eintrag")
        if ok and entry:
            prev = dict(self.data)
            self.data[theme][entry] = ""
            self.save_wiki()
            self.load_entries(self.themes_list.currentItem(), None)
            def undo():
                self.data = prev
                self.save_wiki()
                self.load_entries(self.themes_list.currentItem(), None)
            self.undo_manager.add(UndoAction(undo, description=f"Eintrag {entry} hinzugefügt"))
    
    def delete_entry(self):
        theme = self.current_theme()
        entry = self.current_entry()
        if not theme or not entry:
            return
        prev = dict(self.data)
        del self.data[theme][entry]
        self.save_wiki()
        self.load_entries(self.themes_list.currentItem(), None)
        def undo():
            self.data = prev
            self.save_wiki()
            self.load_entries(self.themes_list.currentItem(), None)
        self.undo_manager.add(UndoAction(undo, description=f"Eintrag {entry} gelöscht"))
    
    def save_detail(self):
        theme = self.current_theme()
        entry = self.current_entry()
        if not theme or not entry:
            return
        prev = dict(self.data)
        self.data[theme][entry] = self.detail_edit.toPlainText()
        self.save_wiki()
        def undo():
            self.data = prev
            self.save_wiki()
            self.load_details(self.entries_list.currentItem(), None)
        self.undo_manager.add(UndoAction(undo, description=f"Details zu {entry} gespeichert"))
        QMessageBox.information(self, "Gespeichert", "Details gespeichert!")
    
    def get_text(self, prompt, label):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, prompt, label)
        return text, ok

    def undo_action(self):
        msg = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", msg)
        self.refresh_themes()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from undo_mudschikato import UndoManager
    app = QApplication([])
    undo_mgr = UndoManager()
    wiki = WikiWidget(undo_mgr)
    wiki.show()
    app.exec()
