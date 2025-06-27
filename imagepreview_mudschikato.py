"""
imagepreview_mudschikato.py
---------------------------
Einfache Bildvorschau für Mudschikato.
- Zeigt Bilder (jpg/png/jpeg) eines gewählten Ordners als Miniatur
- Durchblättern, Bild umbenennen
- Undo für letzte 5 Umbenennungen
- Logging aller Aktionen
"""

import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget, QListWidgetItem, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage
from logging_mudschikato import log_event
from undo_mudschikato import UndoManager, UndoAction

class ImagePreviewWidget(QWidget):
    def __init__(self, undo_manager: UndoManager):
        super().__init__()
        self.undo_manager = undo_manager
        self.setWindowTitle("Mudschikato Bildvorschau")
        self.resize(600, 480)
        self.layout = QVBoxLayout()
        
        btn_ly = QHBoxLayout()
        self.btn_choose = QPushButton("Bilder-Ordner wählen")
        self.btn_choose.clicked.connect(self.choose_dir)
        btn_ly.addWidget(self.btn_choose)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_action)
        btn_ly.addWidget(self.btn_undo)
        self.layout.addLayout(btn_ly)
        
        self.imglist = QListWidget()
        self.imglist.currentItemChanged.connect(self.show_image)
        self.layout.addWidget(self.imglist)
        
        img_ly = QHBoxLayout()
        self.img_label = QLabel("Kein Bild gewählt")
        self.img_label.setMinimumSize(220, 220)
        img_ly.addWidget(self.img_label)
        rename_ly = QVBoxLayout()
        self.rename_field = QLineEdit()
        self.rename_field.setPlaceholderText("Neuer Bildname (ohne Endung)")
        self.btn_rename = QPushButton("Umbenennen")
        self.btn_rename.clicked.connect(self.rename_image)
        rename_ly.addWidget(self.rename_field)
        rename_ly.addWidget(self.btn_rename)
        img_ly.addLayout(rename_ly)
        self.layout.addLayout(img_ly)
        self.setLayout(self.layout)
        
        self.dirpath = None
        self.images = []
    
    def choose_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Bilder-Ordner wählen")
        if folder:
            self.dirpath = folder
            self.load_images()
    
    def load_images(self):
        self.imglist.clear()
        self.images = []
        if not self.dirpath or not os.path.isdir(self.dirpath):
            return
        for fname in os.listdir(self.dirpath):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                self.images.append(fname)
                self.imglist.addItem(QListWidgetItem(fname))
    
    def show_image(self, curr, prev):
        if not curr:
            self.img_label.setText("Kein Bild gewählt")
            self.img_label.setPixmap(QPixmap())
            return
        fname = curr.text()
        fpath = os.path.join(self.dirpath, fname)
        if os.path.isfile(fpath):
            img = QPixmap(fpath)
            if not img.isNull():
                img = img.scaled(220, 220, aspectRatioMode=1)
                self.img_label.setPixmap(img)
            else:
                self.img_label.setText("Kann Bild nicht anzeigen.")
        else:
            self.img_label.setText("Datei nicht gefunden.")
        self.rename_field.setText(os.path.splitext(fname)[0])
    
    def rename_image(self):
        curr = self.imglist.currentItem()
        if not curr or not self.dirpath:
            QMessageBox.warning(self, "Fehler", "Kein Bild ausgewählt.")
            return
        oldname = curr.text()
        newname = self.rename_field.text().strip()
        if not newname:
            QMessageBox.warning(self, "Fehler", "Neuer Name fehlt.")
            return
        oldpath = os.path.join(self.dirpath, oldname)
        ext = os.path.splitext(oldname)[1]
        newfile = newname + ext
        newpath = os.path.join(self.dirpath, newfile)
        if os.path.exists(newpath):
            QMessageBox.warning(self, "Fehler", "Dateiname existiert bereits.")
            return
        try:
            os.rename(oldpath, newpath)
            log_event(f"Bild umbenannt: {oldname} -> {newfile}", "ImagePreview", "INFO")
            curr.setText(newfile)
            self.load_images()
            # Undo: Rückumbenennen
            def undo():
                if os.path.exists(newpath):
                    os.rename(newpath, oldpath)
                    log_event(f"Undo: Bild rückbenannt: {newfile} -> {oldname}", "Undo", "INFO")
                self.load_images()
            self.undo_manager.add(UndoAction(undo, description=f"Bild {oldname} umbenannt"))
            QMessageBox.information(self, "Umbenennen", "Bild wurde umbenannt.")
        except Exception as e:
            log_event(f"Fehler beim Umbenennen: {e}", "ImagePreview", "ERROR")
            QMessageBox.critical(self, "Fehler", f"Bild konnte nicht umbenannt werden:\n{e}")
    
    def undo_action(self):
        result = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", result)

if __name__ == "__main__":
    app = QApplication([])
    undo_mgr = UndoManager()
    win = ImagePreviewWidget(undo_mgr)
    win.show()
    app.exec()
