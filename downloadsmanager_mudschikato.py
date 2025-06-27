"""
downloadsmanager_mudschikato.py
-------------------------------
Manager zur sicheren und flexiblen Bereinigung & Organisation des Downloads-Ordners.
- Übersicht & Filter: Typ, Alter, Größe
- Interaktive Auswahl: verschieben, archivieren, löschen, ignorieren
- Alle Aktionen validiert & mit Undo
- Logging jeder Aktion
- Nichts wird endgültig gelöscht, alles erst verschoben
- Perfekt für Laien & Profis
"""

import os
import shutil
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QFileDialog, QComboBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from undo_mudschikato import UndoManager, UndoAction
from logging_mudschikato import log_event

DOWNLOADS_PATH = os.path.expanduser("~/Downloads")
SAFE_ARCHIV = "mudschikato_archiv"
SAFE_TRASH = "mudschikato_downloads_trash"

class DownloadsManagerWidget(QWidget):
    def __init__(self, undo_manager: UndoManager):
        super().__init__()
        self.undo_manager = undo_manager
        self.setWindowTitle("Downloads-Ordner-Manager")
        self.resize(820, 570)
        self.layout = QVBoxLayout()

        # Zielordner sicherstellen
        os.makedirs(SAFE_ARCHIV, exist_ok=True)
        os.makedirs(SAFE_TRASH, exist_ok=True)

        # Filter & Optionen
        opt_ly = QHBoxLayout()
        self.cb_typ = QComboBox()
        self.cb_typ.addItems(["Alle Typen", "Bilder", "Audio", "Video", "Dokumente", "Archive", "Andere"])
        self.cb_typ.currentIndexChanged.connect(self.refresh_filelist)
        opt_ly.addWidget(QLabel("Typ:"))
        opt_ly.addWidget(self.cb_typ)

        self.cb_alter = QComboBox()
        self.cb_alter.addItems(["Alle", "Letzte 24h", "Letzte 7 Tage", "Letzter Monat", "Älter als 3 Monate"])
        self.cb_alter.currentIndexChanged.connect(self.refresh_filelist)
        opt_ly.addWidget(QLabel("Alter:"))
        opt_ly.addWidget(self.cb_alter)

        self.cb_groesse = QComboBox()
        self.cb_groesse.addItems(["Alle Größen", "> 1 MB", "> 10 MB", "> 100 MB"])
        self.cb_groesse.currentIndexChanged.connect(self.refresh_filelist)
        opt_ly.addWidget(QLabel("Größe:"))
        opt_ly.addWidget(self.cb_groesse)

        self.chk_subdirs = QCheckBox("Auch Unterordner prüfen")
        self.chk_subdirs.stateChanged.connect(self.refresh_filelist)
        opt_ly.addWidget(self.chk_subdirs)
        self.layout.addLayout(opt_ly)

        # Datei-Liste
        self.filelist = QListWidget()
        self.layout.addWidget(self.filelist)

        # Aktionen
        act_ly = QHBoxLayout()
        self.btn_refresh = QPushButton("Liste aktualisieren")
        self.btn_refresh.clicked.connect(self.refresh_filelist)
        act_ly.addWidget(self.btn_refresh)
        self.btn_move = QPushButton("Auswahl → Archivieren")
        self.btn_move.clicked.connect(self.move_files)
        act_ly.addWidget(self.btn_move)
        self.btn_trash = QPushButton("Auswahl → Papierkorb")
        self.btn_trash.clicked.connect(self.trash_files)
        act_ly.addWidget(self.btn_trash)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_action)
        act_ly.addWidget(self.btn_undo)
        self.layout.addLayout(act_ly)

        self.setLayout(self.layout)
        self.refresh_filelist()

    def get_files(self):
        # Hole alle Dateien mit Filter (Typ, Alter, Größe)
        filetypes = {
            "Bilder": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
            "Audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
            "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
            "Dokumente": [".pdf", ".doc", ".docx", ".odt", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
            "Archive": [".zip", ".tar", ".gz", ".rar", ".7z"],
        }
        age_opts = {
            "Alle": None,
            "Letzte 24h": 1,
            "Letzte 7 Tage": 7,
            "Letzter Monat": 31,
            "Älter als 3 Monate": -90,
        }
        size_opts = {
            "Alle Größen": 0,
            "> 1 MB": 1_000_000,
            "> 10 MB": 10_000_000,
            "> 100 MB": 100_000_000,
        }

        root = DOWNLOADS_PATH
        if not os.path.exists(root):
            return []
        result = []
        for dirpath, dirs, files in os.walk(root):
            for fname in files:
                fpath = os.path.join(dirpath, fname)
                # Filter Typ
                typ = self.cb_typ.currentText()
                if typ != "Alle Typen":
                    if not any(fname.lower().endswith(ext) for ext in filetypes.get(typ, [])):
                        if typ != "Andere":
                            continue
                        else:
                            if any(fname.lower().endswith(ext) for exts in filetypes.values() for ext in exts):
                                continue
                # Filter Alter
                alter = self.cb_alter.currentText()
                if alter != "Alle":
                    days = age_opts[alter]
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))
                    now = datetime.datetime.now()
                    if days > 0 and (now - mtime).days > days:
                        continue
                    if days < 0 and (now - mtime).days < abs(days):
                        continue
                # Filter Größe
                groesse = self.cb_groesse.currentText()
                size_min = size_opts[groesse]
                if os.path.getsize(fpath) < size_min:
                    continue
                result.append(fpath)
            if not self.chk_subdirs.isChecked():
                break
        return result

    def refresh_filelist(self):
        self.filelist.clear()
        files = self.get_files()
        for f in files:
            size = os.path.getsize(f)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
            self.filelist.addItem(f"{f}   [{size//1024} KB, {mtime}]")
        if not files:
            self.filelist.addItem("Keine Dateien gefunden.")

    def move_files(self):
        sel = self.filelist.selectedItems()
        if not sel:
            QMessageBox.information(self, "Hinweis", "Keine Datei ausgewählt.")
            return
        moved = []
        for item in sel:
            if item.text().startswith("Keine Dateien"):
                continue
            fpath = item.text().split("   [")[0]
            fname = os.path.basename(fpath)
            target = os.path.join(SAFE_ARCHIV, fname)
            # Keine Überschreibung!
            if os.path.exists(target):
                target = os.path.join(SAFE_ARCHIV, self.unique_name(fname))
            try:
                shutil.move(fpath, target)
                moved.append((fpath, target))
                log_event(f"Download archiviert: {fpath} -> {target}", "DownloadsManager", "INFO")
            except Exception as e:
                log_event(f"Fehler beim Archivieren: {fpath} ({e})", "DownloadsManager", "ERROR")
        self.refresh_filelist()
        def undo():
            for src, dst in moved:
                if os.path.exists(dst):
                    shutil.move(dst, src)
                    log_event(f"Archiv-Undo: {dst} -> {src}", "DownloadsManager", "UNDO")
            self.refresh_filelist()
        if moved:
            self.undo_manager.add(UndoAction(undo, description="Downloads archiviert"))
            QMessageBox.information(self, "Archiviert", f"{len(moved)} Datei(en) verschoben (archiviert).")

    def trash_files(self):
        sel = self.filelist.selectedItems()
        if not sel:
            QMessageBox.information(self, "Hinweis", "Keine Datei ausgewählt.")
            return
        moved = []
        for item in sel:
            if item.text().startswith("Keine Dateien"):
                continue
            fpath = item.text().split("   [")[0]
            fname = os.path.basename(fpath)
            target = os.path.join(SAFE_TRASH, fname)
            # Keine Überschreibung!
            if os.path.exists(target):
                target = os.path.join(SAFE_TRASH, self.unique_name(fname))
            try:
                shutil.move(fpath, target)
                moved.append((fpath, target))
                log_event(f"Download in Papierkorb: {fpath} -> {target}", "DownloadsManager", "INFO")
            except Exception as e:
                log_event(f"Fehler beim Papierkorb: {fpath} ({e})", "DownloadsManager", "ERROR")
        self.refresh_filelist()
        def undo():
            for src, dst in moved:
                if os.path.exists(dst):
                    shutil.move(dst, src)
                    log_event(f"Papierkorb-Undo: {dst} -> {src}", "DownloadsManager", "UNDO")
            self.refresh_filelist()
        if moved:
            self.undo_manager.add(UndoAction(undo, description="Downloads in Papierkorb verschoben"))
            QMessageBox.information(self, "Papierkorb", f"{len(moved)} Datei(en) verschoben (Papierkorb).")

    def undo_action(self):
        msg = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", msg)
        self.refresh_filelist()

    def unique_name(self, fname):
        base, ext = os.path.splitext(fname)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base}_{ts}{ext}"

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from undo_mudschikato import UndoManager
    app = QApplication([])
    undo_mgr = UndoManager()
    win = DownloadsManagerWidget(undo_mgr)
    win.show()
    app.exec()
