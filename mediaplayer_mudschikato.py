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
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QFileDialog, QSlider, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
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
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.current_index = -1
        self.is_paused = False
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_position)
        self.player.mediaStatusChanged.connect(self.handle_media_status)

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
            log_event(f"Song nach oben verschoben: {item.text()}", "MediaPlayer", "INFO")

            def undo(item=item, orig=row):
                idx = self.playlist.row(item)
                if idx != -1:
                    self.playlist.takeItem(idx)
                    self.playlist.insertItem(orig, item)
                    self.playlist.setCurrentRow(orig)
                    self.save_playlist()
                    log_event(f"Song-Zurückverschiebung (Undo): {item.text()}", "MediaPlayer", "UNDO")
            self.undo_manager.add(UndoAction(undo, description="Song hoch verschoben"))

    def move_down(self):
        row = self.playlist.currentRow()
        if row < self.playlist.count() - 1 and row >= 0:
            item = self.playlist.takeItem(row)
            self.playlist.insertItem(row + 1, item)
            self.playlist.setCurrentRow(row + 1)
            self.save_playlist()
            log_event(f"Song nach unten verschoben: {item.text()}", "MediaPlayer", "INFO")

            def undo(item=item, orig=row):
                idx = self.playlist.row(item)
                if idx != -1:
                    self.playlist.takeItem(idx)
                    self.playlist.insertItem(orig, item)
                    self.playlist.setCurrentRow(orig)
                    self.save_playlist()
                    log_event(f"Song-Zurückverschiebung (Undo): {item.text()}", "MediaPlayer", "UNDO")
            self.undo_manager.add(UndoAction(undo, description="Song runter verschoben"))

    def play_selected(self):
        if self.playlist.count() == 0:
            QMessageBox.information(self, "Info", "Playlist ist leer.")
            return
        idx = self.playlist.currentRow()
        if idx < 0:
            idx = 0
            self.playlist.setCurrentRow(0)
        self.current_index = idx
        filepath = self.playlist.item(idx).text()
        self.player.setSource(QUrl.fromLocalFile(filepath))
        self.player.play()
        self.is_paused = False
        self.update_timer.start(500)
        log_event(f"Abspielen: {filepath}", "MediaPlayer", "INFO")

    def play_next(self):
        if self.playlist.count() == 0:
            return
        next_idx = (self.current_index + 1) % self.playlist.count()
        self.playlist.setCurrentRow(next_idx)
        self.play_selected()

    def play_prev(self):
        if self.playlist.count() == 0:
            return
        prev_idx = (self.current_index - 1) % self.playlist.count()
        self.playlist.setCurrentRow(prev_idx)
        self.play_selected()

    def pause_audio(self):
        state = self.player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.is_paused = True
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.player.play()
            self.is_paused = False

    def update_position(self):
        pos = self.player.position() // 1000
        self.label_pos.setText(f"Position: {pos // 60:02d}:{pos % 60:02d}")

    def set_volume(self):
        vol = self.slider_vol.value() / 100
        self.audio_output.setVolume(vol)

    def save_playlist(self):
        with open(PLAYLISTDATEI, "w", encoding="utf-8") as f:
            for i in range(self.playlist.count()):
                f.write(self.playlist.item(i).text() + "\n")

    def load_playlist(self):
        self.playlist.clear()
        if not os.path.exists(PLAYLISTDATEI):
            return
        with open(PLAYLISTDATEI, "r", encoding="utf-8") as f:
            for line in f:
                path = line.strip()
                if path:
                    self.playlist.addItem(path)

    def undo_action(self):
        result = self.undo_manager.undo()
        QMessageBox.information(self, "Undo", result)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_next()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    undo_mgr = UndoManager()
    win = MediaPlayerWidget(undo_mgr)
    win.show()
    sys.exit(app.exec())
