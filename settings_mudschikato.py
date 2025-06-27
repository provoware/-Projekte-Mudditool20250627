"""
settings_mudschikato.py
-----------------------
Laienfreundliches Theme-/Settings-Modul für Mudschikato.
- Farbmodus (Hell/Dunkel/Benutzerdefiniert)
- Schriftgröße: Normal/Groß/Extra Groß
- Sofort-Vorschau
- Undo, Reset
- Persistenz in settings.json
"""

import os, json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QColorDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QColor, QPalette
from undo_mudschikato import UndoManager, UndoAction

SETTINGSFILE = "mudschikato_settings.json"

# Default Settings
DEFAULT_SETTINGS = {
    "theme": "Hell",
    "bg_color": "#ffffff",
    "fg_color": "#222222",
    "font_size": 10
}

class SettingsWidget(QWidget):
    def __init__(self, undo_manager: UndoManager, mainwindow=None):
        super().__init__()
        self.undo_manager = undo_manager
        self.mainwindow = mainwindow
        self.setWindowTitle("Einstellungen / Theme")
        self.layout = QVBoxLayout()

        # Theme-Auswahl
        self.theme_box = QComboBox()
        self.theme_box.addItems(["Hell", "Dunkel", "Benutzerdefiniert"])
        self.theme_box.currentIndexChanged.connect(self.update_preview)
        self.layout.addWidget(QLabel("Farbmodus:"))
        self.layout.addWidget(self.theme_box)

        # Farbauswahl für Benutzerdefiniert
        self.btn_bg_color = QPushButton("Hintergrundfarbe wählen")
        self.btn_fg_color = QPushButton("Textfarbe wählen")
        self.btn_bg_color.clicked.connect(self.choose_bg_color)
        self.btn_fg_color.clicked.connect(self.choose_fg_color)
        self.layout.addWidget(self.btn_bg_color)
        self.layout.addWidget(self.btn_fg_color)

        # Schriftgröße
        self.font_box = QComboBox()
        self.font_box.addItems(["Normal", "Groß", "Extra Groß"])
        self.font_box.currentIndexChanged.connect(self.update_preview)
        self.layout.addWidget(QLabel("Schriftgröße:"))
        self.layout.addWidget(self.font_box)

        # Vorschau
        self.preview_label = QLabel("Vorschau – Mudschikato Struktur & Hilfstool 2025")
        self.layout.addWidget(self.preview_label)

        # Buttons
        btn_ly = QHBoxLayout()
        self.btn_apply = QPushButton("Übernehmen")
        self.btn_apply.clicked.connect(self.apply_settings)
        btn_ly.addWidget(self.btn_apply)
        self.btn_reset = QPushButton("Zurücksetzen")
        self.btn_reset.clicked.connect(self.reset_settings)
        btn_ly.addWidget(self.btn_reset)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_settings)
        btn_ly.addWidget(self.btn_undo)
        self.layout.addLayout(btn_ly)

        self.setLayout(self.layout)
        # Einstellungen laden
        self.settings = self.load_settings()
        self.last_settings = dict(self.settings)
        self.apply_to_gui(self.settings)
        self.update_preview()

    def load_settings(self):
        if os.path.exists(SETTINGSFILE):
            try:
                with open(SETTINGSFILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return dict(DEFAULT_SETTINGS)

    def save_settings(self):
        with open(SETTINGSFILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f)

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings["bg_color"] = color.name()
            self.update_preview()

    def choose_fg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings["fg_color"] = color.name()
            self.update_preview()

    def update_preview(self):
        # Theme setzen
        theme = self.theme_box.currentText()
        if theme == "Hell":
            self.settings.update({"bg_color": "#ffffff", "fg_color": "#222222"})
        elif theme == "Dunkel":
            self.settings.update({"bg_color": "#222222", "fg_color": "#f0f0f0"})
        # Schriftgröße
        font_size = [10, 13, 17][self.font_box.currentIndex()]
        self.settings["font_size"] = font_size
        # Vorschau setzen
        self.apply_to_gui(self.settings, preview_only=True)

    def apply_to_gui(self, settings, preview_only=False):
        # Nur das eigene Widget (Vorschau) stylen, außer bei Übernehmen
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(settings["bg_color"]))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(settings["fg_color"]))
        self.setPalette(pal)
        font = QFont()
        font.setPointSize(settings["font_size"])
        self.preview_label.setFont(font)
        self.preview_label.setStyleSheet(
            f"color: {settings['fg_color']}; background:{settings['bg_color']};"
        )
        self.setAutoFillBackground(True)
        if not preview_only and self.mainwindow:
            self.mainwindow.setFont(font)
            self.mainwindow.setStyleSheet(
                f"color:{settings['fg_color']}; background:{settings['bg_color']};"
            )

    def apply_settings(self):
        prev = dict(self.last_settings)
        new = dict(self.settings)
        self.save_settings()
        self.apply_to_gui(new)
        if self.mainwindow:
            self.apply_to_all_tabs(new)
        self.last_settings = dict(new)
        def undo():
            self.settings = dict(prev)
            self.save_settings()
            self.apply_to_gui(prev)
            if self.mainwindow:
                self.apply_to_all_tabs(prev)
        self.undo_manager.add(UndoAction(undo, description="Theme-Einstellungen geändert"))
        QMessageBox.information(self, "Übernommen", "Einstellungen übernommen!")
    
    def apply_to_all_tabs(self, settings):
        # Wende Theme und Schriftgröße auf alle Tabs an (vereinfachte Version)
        if not self.mainwindow:
            return
        for i in range(self.mainwindow.tabs.count()):
            w = self.mainwindow.tabs.widget(i)
            w.setFont(QFont("", settings["font_size"]))
            w.setStyleSheet(
                f"color:{settings['fg_color']}; background:{settings['bg_color']};"
            )
        self.mainwindow.setFont(QFont("", settings["font_size"]))
        self.mainwindow.setStyleSheet(
            f"color:{settings['fg_color']}; background:{settings['bg_color']};"
        )

    def reset_settings(self):
        prev = dict(self.settings)
        self.settings = dict(DEFAULT_SETTINGS)
        self.theme_box.setCurrentIndex(0)
        self.font_box.setCurrentIndex(0)
        self.update_preview()
        self.save_settings()
        def undo():
            self.settings = dict(prev)
            self.save_settings()
            self.apply_to_gui(prev)
            if self.mainwindow:
                self.apply_to_all_tabs(prev)
        self.undo_manager.add(UndoAction(undo, description="Einstellungen zurückgesetzt"))
        QMessageBox.information(self, "Zurückgesetzt", "Standard wiederhergestellt!")

    def undo_settings(self):
        msg = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", msg)
        self.update_preview()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from undo_mudschikato import UndoManager
    app = QApplication([])
    undo_mgr = UndoManager()
    sw = SettingsWidget(undo_mgr)
    sw.show()
    app.exec()
