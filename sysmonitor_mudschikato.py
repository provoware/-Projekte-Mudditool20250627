"""
sysmonitor_mudschikato.py
-------------------------
Einfaches Systemmonitor-Modul für Mudschikato.
- Zeigt CPU-Auslastung, RAM-Nutzung, Festplattenaktivität
- Intervall einstellbar (1-60s)
- Anzeigen individuell an/abschaltbar
- GUI, laienfreundlich, robust
"""

import psutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QSpinBox
)
from PyQt6.QtCore import QTimer

class SysMonitorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Systemmonitor")
        self.resize(360, 220)
        self.layout = QVBoxLayout()

        # Einstellungen
        opts = QHBoxLayout()
        opts.addWidget(QLabel("Intervall (Sekunden):"))
        self.interval_box = QSpinBox()
        self.interval_box.setRange(1, 60)
        self.interval_box.setValue(3)
        opts.addWidget(self.interval_box)

        self.chk_cpu = QCheckBox("CPU-Auslastung anzeigen")
        self.chk_cpu.setChecked(True)
        opts.addWidget(self.chk_cpu)

        self.chk_ram = QCheckBox("RAM-Nutzung anzeigen")
        self.chk_ram.setChecked(True)
        opts.addWidget(self.chk_ram)

        self.chk_disk = QCheckBox("Festplattenaktivität anzeigen")
        self.chk_disk.setChecked(True)
        opts.addWidget(self.chk_disk)

        self.layout.addLayout(opts)

        # Labels für Werte
        self.label_cpu = QLabel("CPU: ... %")
        self.label_ram = QLabel("RAM: ... MB / ... MB")
        self.label_disk = QLabel("Disk: ... MB gelesen, ... MB geschrieben")
        self.layout.addWidget(self.label_cpu)
        self.layout.addWidget(self.label_ram)
        self.layout.addWidget(self.label_disk)

        # Start/Stop Button
        btn_ly = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_monitor)
        btn_ly.addWidget(self.btn_start)
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_monitor)
        self.btn_stop.setEnabled(False)
        btn_ly.addWidget(self.btn_stop)
        self.layout.addLayout(btn_ly)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.prev_disk = psutil.disk_io_counters()
        self.disk_read = 0
        self.disk_write = 0

    def start_monitor(self):
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.timer.start(self.interval_box.value() * 1000)

    def stop_monitor(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.timer.stop()

    def update_info(self):
        # CPU
        if self.chk_cpu.isChecked():
            cpu = psutil.cpu_percent(interval=None)
            self.label_cpu.setText(f"CPU: {cpu:.1f} %")
            self.label_cpu.show()
        else:
            self.label_cpu.hide()
        # RAM
        if self.chk_ram.isChecked():
            mem = psutil.virtual_memory()
            self.label_ram.setText(f"RAM: {mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB")
            self.label_ram.show()
        else:
            self.label_ram.hide()
        # Disk
        if self.chk_disk.isChecked():
            disk = psutil.disk_io_counters()
            read = (disk.read_bytes - self.prev_disk.read_bytes) / (1024*1024)
            write = (disk.write_bytes - self.prev_disk.write_bytes) / (1024*1024)
            self.label_disk.setText(f"Disk: {read:.2f} MB gelesen, {write:.2f} MB geschrieben")
            self.label_disk.show()
            self.prev_disk = disk
        else:
            self.label_disk.hide()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    win = SysMonitorWidget()
    win.show()
    app.exec()
