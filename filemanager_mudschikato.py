"""
filemanager_mudschikato.py
--------------------------
Einfacher Dateimanager für Mudschikato.
- Zeigt Dateien in gewähltem Verzeichnis als Liste
- Dateien "löschen" = in Papierkorb verschieben (nie echt löschen!)
- Undo: Letzte 5 Löschaktionen rückgängig machen
- Logging aller Aktionen
- Später erweiterbar um Drag & Drop, Vorschau, etc.
"""

import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QLabel, QHBoxLayout
)
from logging_mudschikato import log_event
from undo_mudschikato import UndoManager, UndoAction

PAPIERKORB = "mudschikato_papierkorb"

class FileManagerWidget(QWidget):
    def __init__(self, undo_manager: UndoManager):
        super().__init__()
        self.undo_manager = undo_manager
        self.setWindowTitle("Mudschikato Dateimanager")
        self.resize(540, 360)
        self.layout = QVBoxLayout()
        
        self.info = QLabel("Verzeichnis: Nicht gewählt")
        self.layout.addWidget(self.info)
        
        btn_layout = QHBoxLayout()
        self.btn_choose = QPushButton("Verzeichnis wählen")
        self.btn_choose.clicked.connect(self.choose_dir)
        btn_layout.addWidget(self.btn_choose)
        
        self.btn_delete = QPushButton("Markierte in Papierkorb")
        self.btn_delete.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.btn_delete)
        
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_action)
        btn_layout.addWidget(self.btn_undo)
        
        self.layout.addLayout(btn_layout)
        self.filelist = QListWidget()
        self.layout.addWidget(self.filelist)
        self.setLayout(self.layout)
        
        self.dirpath = None
        if not os.path.exists(PAPIERKORB):
            os.makedirs(PAPIERKORB)
    
    def choose_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Verzeichnis wählen")
        if folder:
            self.dirpath = folder
            self.info.setText(f"Verzeichnis: {folder}")
            self.load_files()
    
    def load_files(self):
        self.filelist.clear()
        if not self.dirpath or not os.path.isdir(self.dirpath):
            return
        for fname in os.listdir(self.dirpath):
            fpath = os.path.join(self.dirpath, fname)
            if os.path.isfile(fpath):
                self.filelist.addItem(QListWidgetItem(fname))
    
    def delete_selected(self):
        if not self.dirpath:
            QMessageBox.warning(self, "Fehler", "Kein Verzeichnis gewählt!")
            return
        selected = self.filelist.selectedItems()
        if not selected:
            QMessageBox.information(self, "Info", "Keine Datei markiert.")
            return
        # Liste von (filename, fullpath) für Undo
        removed = []
        for item in selected:
            fname = item.text()
            src = os.path.join(self.dirpath, fname)
            dst = os.path.join(PAPIERKORB, fname)
            try:
                shutil.move(src, dst)
                removed.append((fname, src, dst))
                log_event(f"Datei verschoben in Papierkorb: {fname}", "FileManager", "INFO")
            except Exception as e:
                log_event(f"Fehler beim Verschieben: {fname}: {e}", "FileManager", "ERROR")
        self.load_files()
        QMessageBox.information(self, "Papierkorb", f"{len(removed)} Datei(en) in Papierkorb verschoben.")
        # Undo: Dateien zurückholen
        def undo():
            for fname, src, dst in removed:
                if os.path.exists(dst):
                    shutil.move(dst, src)
                    log_event(f"Datei wiederhergestellt aus Papierkorb: {fname}", "Undo", "INFO")
            self.load_files()
        self.undo_manager.add(UndoAction(undo, description="Dateien in Papierkorb verschoben"))
    
    def undo_action(self):
        result = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", result)

if __name__ == "__main__":
    app = QApplication([])
    undo_mgr = UndoManager()
    win = FileManagerWidget(undo_mgr)
    win.show()
    app.exec()
