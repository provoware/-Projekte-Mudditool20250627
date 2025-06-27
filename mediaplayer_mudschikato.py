"""
mediaplayer_mudschikato.py
--------------------------
Einfacher Medienplayer mit Playlist, Undo und persistenter Speicherung.
- Unterstützt mp3, wav, ogg
- Playlist: Songs hinzufügen, löschen, abspielen, Reihenfolge ändern
- Undo für gelöschte Songs (max. 5 Schritte)
- Lautstärkeregelung, Fortschrittsanzeige, nächster/vorheriger Song
- Playlist wird beim Beenden automatisch gespeichert und beim Start geladen
"""

import os
import pygame
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QFileDialog, QSlider, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from logging_mudschikato import log_event
from undo_mudschikato import UndoManager, UndoAction

PLAYLISTDATEI = "mudschikato_playlist.txt"

class MediaPlayerWidget(QWidget):
    def __init__(self, undo_manager: UndoManager):
        super().__init__()
        self.undo_manager = undo_manager
        self.setWindowTitle("Mudschikato Medienplayer")
        self.resize(600, 400)
        self.layout = QVBoxLayout()

        # Playlist-View
        self.playlist = QListWidget()
        self.layout.addWidget(self.playlist)

        # Buttons für Playlist-Aktionen
        btn_ly = QHBoxLayout()
        self.btn_add = QPushButton("Hinzufügen")
        self.btn_add.clicked.connect(self.add_song)
        btn_ly.addWidget(self.btn_add)
        self.btn_del = QPushButton("Entfernen")
        self.btn_del.clicked.connect(self.delete_song)
        btn_ly.addWidget(self.btn_del)
        self.btn_up = QPushButton("▲")
        self.btn_up.clicked.connect(self.move_up)
        btn_ly.addWidget(self.btn_up)
        self.btn_down = QPushButton("▼")
        self.btn_down.clicked.connect(self.move_down)
        btn_ly.addWidget(self.btn_down)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_action)
        btn_ly.addWidget(self.btn_undo)
        self.layout.addLayout(btn_ly)

        # Player Controls
        controls = QHBoxLayout()
        self.btn_prev = QPushButton("⏮")
        self.btn_prev.clicked.connect(self.play_prev)
        controls.addWidget(self.btn_prev)
        self.btn_play = QPushButton("▶")
        self.btn_play.clicked.connect(self.play_selected)
        controls.addWidget(self.btn_play)
        self.btn_pause = QPushButton("⏸")
        self.btn_pause.clicked.connect(self.pause_audio)
        controls.addWidget(self.btn_pause)
        self.btn_next = QPushButton("⏭")
        self.btn_next.clicked.connect(self.play_next)
        controls.addWidget(self.btn_next)
        self.layout.addLayout(controls)

        # Lautstärke und Position
        vol_ly = QHBoxLayout()
        self.label_vol = QLabel("Lautstärke")
        vol_ly.addWidget(self.label_vol)
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(70)
        self.slider_vol.valueChanged.connect(self.set_volume)
        vol_ly.addWidget(self.slider_vol)
        self.layout.addLayout(vol_ly)

        pos_ly = QHBoxLayout()
        self.label_pos = QLabel("Position: 00:00")
        pos_ly.addWidget(self.label_pos)
        self.layout.addLayout(pos_ly)

        self.setLayout(self.layout)

        # Audio-Init
        pygame.mixer.init()
        self.current_index = -1
        self.is_paused = False
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_position)

        # Playlist laden
        self.load_playlist()
        self.set_volume()

    def add_song(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Audio-Dateien wählen", "", "Audio (*.mp3 *.wav *.ogg)")
        if files:
            for f in files:
                self.playlist.addItem(f)
                log_event(f"Song hinzugefügt: {f}", "MediaPlayer", "INFO")
            self.save_playlist()
            # Undo: Alle hinzugefügten Songs entfernen
            def undo():
                for f in files:
                    items = self.playlist.findItems(f, Qt.MatchFlag.MatchExactly)
                    for item in items:
                        self.playlist.takeItem(self.playlist.row(item))
                self.save_playlist()
                log_event(f"Song(s) entfernt (Undo): {files}", "MediaPlayer", "UNDO")
            self.undo_manager.add(UndoAction(undo, description="Song(s) hinzugefügt"))

    def delete_song(self):
        selected = self.playlist.selectedItems()
        if not selected:
            return
        removed = []
        for item in selected:
            idx = self.playlist.row(item)
            text = item.text()
            removed.append((idx, text))
            self.playlist.takeItem(idx)
            log_event(f"Song entfernt: {text}", "MediaPlayer", "INFO")
        self.save_playlist()
        # Undo: Songs zurück an die alten Positionen
        def undo():
            for idx, text in reversed(removed):
                self.playlist.insertItem(idx, text)
            self.save_playlist()
            log_event("Song(s) wiederhergestellt (Undo)", "MediaPlayer", "UNDO")
        self.undo_manager.add(UndoAction(undo, description="Song(s) entfernt"))

    def move_up(self):
        row = self.playlist.currentRow()
        if row > 0:
            item = self.playlist.takeItem(row)
            self.playlist.insertItem(row - 1, item)
            self.playlist.setCurrentRow(row - 1)
            self.save_playlist()
