"""
mainwindow_mudschikato.py
-------------------------
Zentrales Hauptfenster für Mudschikato – Struktur & Hilfstool 2025
- Alle Module laienfreundlich als Tab
- Dashboard als Startansicht
- Undo/Logging zentral verfügbar
- Theme-/Settings-Modul integriert
- Wiki-/Info-Modul integriert
- Downloads-Manager integriert
- Keine Codeeingabe für User nötig
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QAction, QMessageBox
)
from logging_mudschikato import log_event
from undo_mudschikato import UndoManager
from dashboard_mudschikato import DashboardWidget
from contextmenu_mudschikato import DateiListe
from feedback_mudschikato import FeedbackWidget
from todo_mudschikato import ToDoWidget
from filemanager_mudschikato import FileManagerWidget
from imagepreview_mudschikato import ImagePreviewWidget
from mediaplayer_mudschikato import MediaPlayerWidget
from kalender_mudschikato import KalenderWidget
from settings_mudschikato import SettingsWidget
from wiki_mudschikato import WikiWidget
from downloadsmanager_mudschikato import DownloadsManagerWidget

class MainMudschikato(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mudschikato Struktur & Hilfstool 2025")
        self.resize(1320, 870)
        self.undo_manager = UndoManager()

        # Zentrales Tab-Interface für alle Module
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 1. Dashboard als Start-Tab
        self.dashboard_tab = DashboardWidget()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # 2. Einstellungen/Theme
        self.settings_tab = SettingsWidget(self.undo_manager, self)
        self.tabs.addTab(self.settings_tab, "Einstellungen")

        # 3. Wiki-/Info-Modul
        self.wiki_tab = WikiWidget(self.undo_manager)
        self.tabs.addTab(self.wiki_tab, "Wiki/Info")

        # 4. Kalender
        self.kalender_tab = KalenderWidget()
        self.tabs.addTab(self.kalender_tab, "Kalender")

        # 5. Dateiliste/Kontextmenü
        self.filelist_tab = DateiListe(self.undo_manager)
        self.tabs.addTab(self.filelist_tab, "Dateiliste")

        # 6. ToDo-Liste
        self.todo_tab = ToDoWidget(self.undo_manager)
        self.tabs.addTab(self.todo_tab, "ToDo")

        # 7. Feedback/Notizen
        self.feedback_tab = FeedbackWidget(self.undo_manager)
        self.tabs.addTab(self.feedback_tab, "Feedback/Notizen")

        # 8. Dateimanager
        self.fm_tab = FileManagerWidget(self.undo_manager)
        self.tabs.addTab(self.fm_tab, "Dateimanager")

        # 9. Bildvorschau
        self.img_tab = ImagePreviewWidget(self.undo_manager)
        self.tabs.addTab(self.img_tab, "Bildvorschau")

        # 10. Medienplayer
        self.mediaplayer_tab = MediaPlayerWidget(self.undo_manager)
        self.tabs.addTab(self.mediaplayer_tab, "Medienplayer")

        # 11. Downloads-Manager
        self.downloads_tab = DownloadsManagerWidget(self.undo_manager)
        self.tabs.addTab(self.downloads_tab, "Downloads-Manager")

        # Menüleiste: Undo, Dashboard, Einstellungen, Wiki, Info, Exit
        menubar = self.menuBar()
        action_undo = QAction("Undo", self)
        action_undo.triggered.connect(self.handle_undo)
        menubar.addAction(action_undo)

        action_dashboard = QAction("Dashboard", self)
        action_dashboard.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        menubar.addAction(action_dashboard)

        action_settings = QAction("Einstellungen", self)
        action_settings.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        menubar.addAction(action_settings)

        action_wiki = QAction("Wiki/Info", self)
        action_wiki.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        menubar.addAction(action_wiki)

        action_downloads = QAction("Downloads-Manager", self)
        action_downloads.triggered.connect(lambda: self.tabs.setCurrentIndex(11))
        menubar.addAction(action_downloads)

        action_exit = QAction("Beenden", self)
        action_exit.triggered.connect(self.close)
        menubar.addAction(action_exit)

        action_info = QAction("Info", self)
        action_info.triggered.connect(self.show_info)
        menubar.addAction(action_info)

        log_event("Mudschikato-Hauptfenster gestartet.", "MainWindow", "INFO")

    def handle_undo(self):
        msg = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", msg)
        log_event("Undo ausgelöst aus Hauptmenü", "MainWindow", "INFO")

    def show_info(self):
        QMessageBox.information(
            self, "Über Mudschikato",
            "Mudschikato Struktur & Hilfstool 2025\n"
            "Version: Basis\n"
            "Entwickelt von VATER PPPOPPI / provoware.de"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainMudschikato()
    win.show()
    sys.exit(app.exec())
