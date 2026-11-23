import sys
import os
import platform
import shutil
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QLineEdit,
    QTextEdit, QFileDialog, QListWidget, QListWidgetItem, QMessageBox,
    QSizePolicy
)

APP_NAME = "AMH-OS"
VERSION = "0.1.0"

STYLE = """
* { font-family: 'Segoe UI'; }
QMainWindow, QWidget#root { background: #0d111b; color: #e8edf7; }
QFrame#sidebar { background: #111827; border-right: 1px solid #263247; }
QLabel#brand { color: #f4f7ff; font-size: 22px; font-weight: 700; }
QLabel#muted { color: #91a0b8; }
QLabel#pageTitle { color: #f4f7ff; font-size: 27px; font-weight: 700; }
QLabel#sectionTitle { color: #f4f7ff; font-size: 16px; font-weight: 650; }
QPushButton#nav {
    text-align: left; padding: 12px 14px; border: 0; border-radius: 9px;
    color: #aab7cc; background: transparent; font-size: 14px;
}
QPushButton#nav:hover { background: #1d293c; color: #ffffff; }
QPushButton#nav[active="true"] { background: #243c63; color: #ffffff; font-weight: 650; }
QFrame#card { background: #151f30; border: 1px solid #26364e; border-radius: 14px; }
QLabel#metric { font-size: 25px; font-weight: 700; color: #f4f7ff; }
QLabel#metricLabel { color: #91a0b8; font-size: 12px; }
QPushButton#primary {
    background: #3978e8; color: white; border: 0; border-radius: 9px;
    padding: 10px 16px; font-weight: 650;
}
QPushButton#primary:hover { background: #4a89f5; }
QPushButton#secondary {
    background: #202d42; color: #dce7fa; border: 1px solid #33445f;
    border-radius: 9px; padding: 9px 14px;
}
QPushButton#secondary:hover { background: #2a3b56; }
QLineEdit, QTextEdit, QListWidget {
    background: #101827; color: #e8edf7; border: 1px solid #2b3a52;
    border-radius: 9px; padding: 9px;
}
QLabel#pill {
    background: #183d35; color: #71e0b4; border-radius: 10px;
    padding: 5px 9px; font-size: 11px; font-weight: 650;
}
"""

def card():
    frame = QFrame()
    frame.setObjectName("card")
    return frame

def muted(text):
    label = QLabel(text)
    label.setObjectName("muted")
    return label

class AMHOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} Desktop")
        self.resize(1240, 790)
        self.setMinimumSize(980, 650)
        self.nav_buttons = {}
        self.pages = QStackedWidget()
        self._build_ui()
        self._show_page("Dashboard")
        self._refresh_system_info()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(235)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 24, 18, 18)
        side.setSpacing(8)

        brand = QLabel("◈  AMH-OS")
        brand.setObjectName("brand")
        side.addWidget(brand)
        version = muted(f"DESKTOP  •  v{VERSION}")
        version.setStyleSheet("font-size: 10px; letter-spacing: 1px;")
        side.addWidget(version)
        side.addSpacing(28)

        for name, glyph in [
            ("Dashboard", "⌂"), ("Devices", "▦"), ("File Manager", "▤"),
            ("Terminal", ">_"), ("Settings", "⚙")
        ]:
            btn = QPushButton(f"{glyph}    {name}")
            btn.setObjectName("nav")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, n=name: self._show_page(n))
            self.nav_buttons[name] = btn
            side.addWidget(btn)

        side.addStretch()
        side.addWidget(muted("PROJECT STATUS"))
        status = QLabel("●  Desktop preview")
        status.setStyleSheet("color:#71e0b4; padding:8px 0;")
        side.addWidget(status)
        side.addWidget(muted("Built with Python + PySide6"))

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 24, 30, 22)
        content_layout.setSpacing(18)

        top = QHBoxLayout()
        self.breadcrumb = QLabel("Dashboard")
        self.breadcrumb.setObjectName("pageTitle")
        top.addWidget(self.breadcrumb)
        top.addStretch()
        self.clock = QLabel()
        self.clock.setStyleSheet("color:#c3cee0; font-size:13px;")
        top.addWidget(self.clock)
        content_layout.addLayout(top)
        content_layout.addWidget(self.pages)

        outer.addWidget(sidebar)
        outer.addWidget(content, 1)
        self.setCentralWidget(root)

        self.pages.addWidget(self._dashboard_page())
        self.pages.addWidget(self._devices_page())
        self.pages.addWidget(self._files_page())
        self.pages.addWidget(self._terminal_page())
        self.pages.addWidget(self._settings_page())

    def _show_page(self, name):
        names = ["Dashboard", "Devices", "File Manager", "Terminal", "Settings"]
        idx = names.index(name)
        self.pages.setCurrentIndex(idx)
        self.breadcrumb.setText(name)
        for key, btn in self.nav_buttons.items():
            btn.setProperty("active", key == name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if name == "Devices":
            self._refresh_ports()

    def _dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("card")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 22, 24, 22)
        left = QVBoxLayout()
        welcome = QLabel("Welcome to your desktop.")
        welcome.setStyleSheet("font-size:23px; font-weight:700; color:#f4f7ff;")
        subtitle = QLabel("Your AMH-OS control center is ready.")
        subtitle.setObjectName("muted")
        left.addWidget(welcome)
        left.addWidget(subtitle)
        hero_layout.addLayout(left)
        hero_layout.addStretch()
        chip = QLabel("●  RUNNING")
        chip.setObjectName("pill")
        hero_layout.addWidget(chip, 0, Qt.AlignVCenter)
        layout.addWidget(hero)

        grid = QGridLayout()
        grid.setSpacing(14)
        self.cpu_value = QLabel("—")
        self.ram_value = QLabel("—")
        self.disk_value = QLabel("—")
        self.host_value = QLabel(platform.system())
        for col, (title, value, hint) in enumerate([
            ("PROCESSOR", self.cpu_value, "Host computer"),
            ("MEMORY", self.ram_value, "RAM usage"),
            ("STORAGE", self.disk_value, "System drive"),
            ("PLATFORM", self.host_value, platform.release())
        ]):
            box = card()
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(18, 16, 18, 16)
            label = QLabel(title)
            label.setObjectName("metricLabel")
            value.setObjectName("metric")
            detail = muted(hint)
            box_layout.addWidget(label)
            box_layout.addSpacing(7)
            box_layout.addWidget(value)
            box_layout.addWidget(detail)
            grid.addWidget(box, 0, col)
        layout.addLayout(grid)

        lower = QHBoxLayout()
        lower.setSpacing(14)

        quick = card()
        ql = QVBoxLayout(quick)
        ql.setContentsMargins(20, 18, 20, 18)
        ql.addWidget(self._section("Quick access"))
        ql.addWidget(muted("Open a workspace"))
        for title, target in [
            ("▦   Device Manager", "Devices"),
            ("▤   File Manager", "File Manager"),
            (">_   Terminal", "Terminal")
        ]:
            b = QPushButton(title)
            b.setObjectName("secondary")
            b.clicked.connect(lambda checked=False, n=target: self._show_page(n))
            ql.addWidget(b)
        ql.addStretch()

        hardware = card()
        hl = QVBoxLayout(hardware)
        hl.setContentsMargins(20, 18, 20, 18)
        hl.addWidget(self._section("AMH-OS hardware"))
        hl.addWidget(muted("Main controller"))
        s3 = QLabel("ESP32-S3  •  Firmware flashed")
        s3.setStyleSheet("font-weight:650; color:#dce7fa;")
        hl.addWidget(s3)
        hl.addSpacing(8)
        hl.addWidget(muted("Coprocessor"))
        copro = QLabel("ESP32-WROOM-32  •  UART link verified")
        copro.setStyleSheet("font-weight:650; color:#71e0b4;")
        hl.addWidget(copro)
        hl.addStretch()
        note = muted("Live desktop-to-board control is a future integration step.")
        note.setWordWrap(True)
        hl.addWidget(note)

        lower.addWidget(quick, 1)
        lower.addWidget(hardware, 1)
        layout.addLayout(lower)
        layout.addStretch()
        return page

    def _section(self, text):
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def _devices_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        intro = card()
        il = QVBoxLayout(intro)
        il.setContentsMargins(20, 18, 20, 18)
        il.addWidget(self._section("Connected serial devices"))
        il.addWidget(muted("Scan Windows COM ports. This is discovery only; desktop-to-firmware commands will be added next."))
        layout.addWidget(intro)

        self.port_list = QListWidget()
        layout.addWidget(self.port_list, 1)
        row = QHBoxLayout()
        refresh = QPushButton("Refresh ports")
        refresh.setObjectName("primary")
        refresh.clicked.connect(self._refresh_ports)
        row.addWidget(refresh)
        row.addStretch()
        layout.addLayout(row)
        return page

    def _refresh_ports(self):
        if not hasattr(self, "port_list"):
            return
        self.port_list.clear()
        try:
            from serial.tools import list_ports
            ports = list(list_ports.comports())
            if not ports:
                self.port_list.addItem("No serial ports detected. Connect a board over USB and refresh.")
            for port in ports:
                self.port_list.addItem(f"{port.device}   —   {port.description}")
        except ImportError:
            self.port_list.addItem("pyserial is not installed. Run: pip install pyserial")

    def _files_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        panel = card()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(20, 18, 20, 18)
        pl.addWidget(self._section("File Manager"))
        pl.addWidget(muted("Browse folders on your Windows computer."))
        row = QHBoxLayout()
        self.path_box = QLineEdit(os.path.expanduser("~"))
        self.path_box.setReadOnly(True)
        browse = QPushButton("Choose folder")
        browse.setObjectName("primary")
        browse.clicked.connect(self._choose_folder)
        row.addWidget(self.path_box, 1)
        row.addWidget(browse)
        pl.addLayout(row)
        self.file_list = QListWidget()
        pl.addWidget(self.file_list, 1)
        layout.addWidget(panel, 1)
        self._load_folder(os.path.expanduser("~"))
        return page

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose a folder", self.path_box.text())
        if folder:
            self._load_folder(folder)

    def _load_folder(self, folder):
        if not hasattr(self, "file_list"):
            return
        self.path_box.setText(folder)
        self.file_list.clear()
        try:
            for name in sorted(os.listdir(folder), key=str.lower):
                full = os.path.join(folder, name)
                prefix = "📁  " if os.path.isdir(full) else "📄  "
                self.file_list.addItem(prefix + name)
        except OSError as exc:
            self.file_list.addItem(f"Unable to read folder: {exc}")

    def _terminal_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        panel = card()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(20, 18, 20, 18)
        pl.addWidget(self._section("AMH-OS Terminal"))
        pl.addWidget(muted("This first preview opens your normal Windows command prompt."))
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setPlainText("AMH-OS Desktop Terminal\\n\\nTerminal integration is planned for a later milestone.")
        pl.addWidget(self.terminal_output, 1)
        launch = QPushButton("Open Windows Terminal")
        launch.setObjectName("primary")
        launch.clicked.connect(self._open_terminal)
        pl.addWidget(launch, 0, Qt.AlignLeft)
        layout.addWidget(panel, 1)
        return page

    def _open_terminal(self):
        import subprocess
        try:
            subprocess.Popen(["cmd.exe"], creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
        except Exception as exc:
            QMessageBox.warning(self, "Could not open terminal", str(exc))

    def _settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        panel = card()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(20, 18, 20, 18)
        pl.addWidget(self._section("About AMH-OS"))
        for line in [
            f"Application: {APP_NAME} Desktop",
            f"Version: {VERSION}",
            "UI framework: Python / PySide6",
            f"Host: {platform.platform()}",
            "Hardware: ESP32-S3 N16R8 + ESP32-WROOM-32",
            "UART protocol: 115200 baud, newline-delimited JSON"
        ]:
            item = QLabel(line)
            item.setStyleSheet("color:#c8d4e7; padding:7px 2px;")
            pl.addWidget(item)
        pl.addStretch()
        layout.addWidget(panel, 1)
        return page

    def _refresh_system_info(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage(os.path.abspath(os.sep)).percent
            self.cpu_value.setText(f"{cpu:.0f}%")
            self.ram_value.setText(f"{ram:.0f}%")
            self.disk_value.setText(f"{disk:.0f}%")
        except ImportError:
            self.cpu_value.setText("N/A")
            self.ram_value.setText("N/A")
            self.disk_value.setText("N/A")

    def _tick(self):
        self.clock.setText(datetime.now().strftime("%A, %d %B  •  %I:%M:%S %p"))
        self._refresh_system_info()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(STYLE)
    window = AMHOSWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
