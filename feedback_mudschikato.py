#!/usr/bin/env python3
# feedback_mudschikato.py
# Feedback- und Notizmodul mit Undo-Support (bis 5 Aktionen) und Logging
# Benötigt: PyQt6, Python 3.8+, keine externen Abhängigkeiten

import sys
import json
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QMessageBox
)


class UndoAction:
    """Repräsentiert eine rückgängig gemachte Aktion."""
    def __init__(self, action_type: str, data):
        self.action_type = action_type
        self.data = data


class UndoManager:
    """Speichert bis zu `capacity` Aktionen und liefert sie zum Undo."""
    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self.stack: list[UndoAction] = []

    def push(self, action: UndoAction):
        self.stack.append(action)
        if len(self.stack) > self.capacity:
            self.stack.pop(0)

    def undo(self) -> UndoAction | None:
        if not self.stack:
            return None
        return self.stack.pop()


class FeedbackApp(QWidget):
    """Hauptfenster der Feedback-/Notiz-Anwendung."""
    def __init__(self):
        super().__init__()
        self.data_file = Path('feedback_notes.json')
        self.log_file = Path('mudschikato.log')
        self._init_logger()
        self.notes: list[str] = []
        self._load_notes()
        self.undo_manager = UndoManager(capacity=5)
        self._init_ui()

    def _init_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('FeedbackApp gestartet')

    def _load_notes(self):
        if self.data_file.exists():
            try:
                with self.data_file.open('r', encoding='utf-8') as f:
                    self.notes = json.load(f)
                self.logger.info(f'{len(self.notes)} Notizen geladen')
            except Exception as e:
                self.logger.error(f'Fehler beim Laden der Notizen: {e}')
                self.notes = []
        else:
            self.notes = []

    def _save_notes(self):
        try:
            with self.data_file.open('w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
            self.logger.info(f'{len(self.notes)} Notizen gespeichert')
        except Exception as e:
            self.logger.error(f'Fehler beim Speichern der Notizen: {e}')

    def _init_ui(self):
        self.setWindowTitle('Feedback & Notizen')
        self.resize(400, 300)

        main_layout = QVBoxLayout()
        controls = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText('Neue Notiz eingeben…')

        add_btn = QPushButton('Hinzufügen')
        add_btn.clicked.connect(self._on_add)

        undo_btn = QPushButton('Rückgängig')
        undo_btn.clicked.connect(self._on_undo)

        controls.addWidget(self.input)
        controls.addWidget(add_btn)
        controls.addWidget(undo_btn)

        self.list_widget = QListWidget()
        for note in self.notes:
            self.list_widget.addItem(note)

        main_layout.addLayout(controls)
        main_layout.addWidget(self.list_widget)
        self.setLayout(main_layout)

    def _on_add(self):
        text = self.input.text().strip()
        if not text:
            QMessageBox.warning(self, 'Warnung', 'Bitte zuerst Text eingeben.')
            return
        # Note hinzufügen
        self.notes.append(text)
        self.list_widget.addItem(text)
        self.undo_manager.push(UndoAction('add', text))
        self.logger.info(f'Notiz hinzugefügt: "{text}"')
        self.input.clear()
        self._save_notes()

    def _on_undo(self):
        action = self.undo_manager.undo()
        if not action:
            QMessageBox.information(self, 'Info', 'Keine Aktion zum Rückgängig machen.')
            return
        if action.action_type == 'add':
            note = action.data
            if note in self.notes:
                idx = self.notes.index(note)
                self.notes.pop(idx)
                self.list_widget.takeItem(idx)
                self.logger.info(f'Rückgängig gemacht: Notiz entfernt: "{note}"')
                self._save_notes()
            else:
                self.logger.warning(f'Rückgängig: Notiz nicht gefunden: "{note}"')
        # Hier könnten weitere Aktionstypen ergänzt werden

    def closeEvent(self, event):
        # Vor dem Schließen sichern
        self._save_notes()
        self.logger.info('FeedbackApp beendet')
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = FeedbackApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
