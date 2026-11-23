import os
import sys
import platform
import subprocess
from datetime import datetime

import psutil
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QAction, QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QLineEdit, QListWidget, QListWidgetItem,
    QDialog, QTextEdit, QFileDialog, QMenu, QMessageBox, QProgressBar,
    QScrollArea, QSizePolicy
)

APP_NAME = "AMH-OS"
VERSION = "2.0.0"

STYLE = """
* { font-family: 'Segoe UI'; }
QWidget { color: #eef3ff; }
QDialog, QWidget#appPanel { background: #101827; }
QFrame#taskbar { background: rgba(9, 14, 27, 238); border-top: 1px solid #34415d; }
QPushButton { border: 0; }
QPushButton#task { background: transparent; color: #dce7ff; padding: 8px 12px; border-radius: 8px; }
QPushButton#task:hover, QPushButton#task[active="true"] { background: #293957; }
QPushButton#start { background: #263b60; color: white; border-radius: 9px; padding: 8px 14px; font-weight: 700; }
QPushButton#start:hover { background: #345487; }
QFrame#startMenu { background: #111b2d; border: 1px solid #526486; border-radius: 14px; }
QLineEdit { background: #1a2940; border: 1px solid #3b4e6d; border-radius: 8px; padding: 10px; color: white; }
QListWidget { background: transparent; border: 0; }
QListWidget::item { padding: 10px; border-radius: 8px; }
QListWidget::item:hover { background: #263b5d; }
QPushButton#appButton { background: rgba(16, 28, 50, 160); border: 1px solid rgba(160, 190, 255, 35); border-radius: 12px; padding: 12px; text-align: left; }
QPushButton#appButton:hover { background: rgba(50, 76, 119, 210); border: 1px solid #83a9ed; }
QLabel#appTitle { font-size: 20px; font-weight: 700; }
QLabel#muted { color: #9eacc5; }
QPushButton#action { background: #2d65c8; color: white; border-radius: 8px; padding: 9px 14px; }
QPushButton#action:hover { background: #3979e8; }
QPushButton#subtle { background: #23324a; color: #e7efff; border: 1px solid #3a4d6b; border-radius: 8px; padding: 8px 12px; }
QTextEdit { background: #09111e; color: #d7e5ff; border: 1px solid #33445f; border-radius: 8px; padding: 8px; }
QProgressBar { background: #26354d; border: 0; border-radius: 5px; height: 9px; text-align: center; }
QProgressBar::chunk { background: #5b9bff; border-radius: 5px; }
"""

APPS = [
    ("📁", "File Explorer", "Browse files and folders"),
    ("⌨️", "Terminal", "Open PowerShell"),
    ("📊", "System Monitor", "Live CPU, memory and disk"),
    ("⚙️", "Settings", "AMH-OS system information"),
    ("ℹ️", "About AMH-OS", "Version and project details"),
]

class DesktopCanvas(QWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#101b3b"))
        grad.setColorAt(0.48, QColor("#263c82"))
        grad.setColorAt(1.0, QColor("#11142e"))
        p.fillRect(self.rect(), grad)
        # Abstract orbital rings and soft light forms, drawn locally (no wallpaper download).
        p.setPen(QPen(QColor(124, 157, 255, 38), 2))
        center = QPoint(int(self.width() * .67), int(self.height() * .42))
        for r in (145, 205, 270):
            p.drawEllipse(center, r, r)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(87, 122, 255, 28))
        p.drawEllipse(QPoint(int(self.width() * .78), int(self.height() * .72)), 240, 180)
        p.setBrush(QColor(182, 111, 255, 24))
        p.drawEllipse(QPoint(int(self.width() * .22), int(self.height() * .18)), 190, 150)
        p.setPen(QColor(235, 241, 255, 220))
        p.setFont(QFont("Segoe UI", 25, QFont.Weight.Bold))
        p.drawText(36, self.height() - 76, "AMH-OS")
        p.setPen(QColor(205, 219, 255, 155))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(38, self.height() - 52, "A desktop environment in progress  •  v2.0")

class AppWindow(QDialog):
    def __init__(self, title, parent=None, size=(760, 500)):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window)
        self.resize(*size)
        self.setStyleSheet(STYLE)
        self.setObjectName("appPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

class AMHDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMH-OS Desktop v2.0")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.showFullScreen()
        self.windows = {}
        self.task_buttons = {}
        self.start_menu = None
        self._build_desktop()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

    def _build_desktop(self):
        self.canvas = DesktopCanvas()
        self.setCentralWidget(self.canvas)
        layout = QVBoxLayout(self.canvas)
        layout.setContentsMargins(18, 18, 18, 0)
        layout.setSpacing(0)

        top = QHBoxLayout()
        top.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        for glyph, name in [("🖥️", "This PC"), ("📁", "File Explorer"), ("⌨️", "Terminal"), ("📊", "System Monitor")]:
            btn = QPushButton(glyph + "\n" + name)
            btn.setObjectName("appButton")
            btn.setFixedSize(118, 76)
            btn.clicked.connect(lambda checked=False, app=name: self.open_app(app))
            top.addWidget(btn)
            top.addSpacing(8)
        top.addStretch()
        layout.addLayout(top)
        layout.addStretch()

        taskbar = QFrame()
        taskbar.setObjectName("taskbar")
        taskbar.setFixedHeight(58)
        row = QHBoxLayout(taskbar)
        row.setContentsMargins(12, 5, 12, 5)
        row.setSpacing(8)

        self.start_btn = QPushButton("◈  Start")
        self.start_btn.setObjectName("start")
        self.start_btn.clicked.connect(self.toggle_start_menu)
        row.addWidget(self.start_btn)

        self.task_area = QHBoxLayout()
        self.task_area.setSpacing(4)
        row.addLayout(self.task_area, 1)

        self.status_label = QLabel("●  AMH-OS ready")
        self.status_label.setStyleSheet("color:#8de0bd; padding:0 10px;")
        row.addWidget(self.status_label)

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.clock_label.setMinimumWidth(150)
        row.addWidget(self.clock_label)
        layout.addWidget(taskbar)

    def _update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%a, %d %b   %I:%M:%S %p"))

    def toggle_start_menu(self):
        if self.start_menu and self.start_menu.isVisible():
            self.start_menu.close()
            self.start_menu = None
            return
        menu = QFrame(self)
        menu.setObjectName("startMenu")
        menu.setStyleSheet(STYLE)
        menu.setGeometry(18, self.height() - 510, 370, 480)
        box = QVBoxLayout(menu)
        box.setContentsMargins(18, 18, 18, 18)
        heading = QLabel("AMH-OS")
        heading.setStyleSheet("font-size:22px;font-weight:700;")
        box.addWidget(heading)
        search = QLineEdit()
        search.setPlaceholderText("Search apps...")
        box.addWidget(search)
        listing = QListWidget()
        for glyph, name, desc in APPS:
            item = QListWidgetItem(glyph + "   " + name + "\n       " + desc)
            item.setData(Qt.ItemDataRole.UserRole, name)
            listing.addItem(item)
        box.addWidget(listing, 1)
        bottom = QHBoxLayout()
        hint = QLabel("v2.0  •  Prototype")
        hint.setObjectName("muted")
        bottom.addWidget(hint)
        bottom.addStretch()
        quit_btn = QPushButton("Power")
        quit_btn.setObjectName("subtle")
        quit_btn.clicked.connect(self.power_menu)
        bottom.addWidget(quit_btn)
        box.addLayout(bottom)
        search.textChanged.connect(lambda text: self._filter_apps(listing, text))
        listing.itemDoubleClicked.connect(lambda item: (self.open_app(item.data(Qt.ItemDataRole.UserRole)), menu.close()))
        menu.show()
        menu.raise_()
        self.start_menu = menu

    def _filter_apps(self, listing, text):
        query = text.lower().strip()
        for i in range(listing.count()):
            item = listing.item(i)
            item.setHidden(query not in item.text().lower())

    def power_menu(self):
        menu = QMenu(self)
        menu.addAction("Lock (prototype)", lambda: QMessageBox.information(self, "AMH-OS", "Lock screen is planned for a later version."))
        menu.addAction("Exit AMH-OS", self.close)
        menu.exec(self.mapToGlobal(self.start_btn.geometry().topLeft()))

    def open_app(self, name):
        if name == "This PC":
            name = "File Explorer"
        if name in self.windows and self.windows[name].isVisible():
            self.windows[name].showNormal()
            self.windows[name].raise_()
            self.windows[name].activateWindow()
            return
        builders = {
            "File Explorer": self._file_explorer,
            "Terminal": self._terminal,
            "System Monitor": self._system_monitor,
            "Settings": self._settings,
            "About AMH-OS": self._about,
        }
        if name not in builders:
            return
        win = builders[name]()
        self.windows[name] = win
        task = QPushButton(name)
        task.setObjectName("task")
        task.clicked.connect(lambda checked=False, app=name: self._focus_app(app))
        self.task_area.addWidget(task)
        self.task_buttons[name] = task
        win.destroyed.connect(lambda obj=None, app=name: self._remove_task(app))
        win.show()
        win.raise_()
        win.activateWindow()

    def _focus_app(self, name):
        win = self.windows.get(name)
        if win and win.isVisible():
            if win.isMinimized():
                win.showNormal()
            win.raise_()
            win.activateWindow()

    def _remove_task(self, name):
        self.windows.pop(name, None)
        button = self.task_buttons.pop(name, None)
        if button:
            self.task_area.removeWidget(button)
            button.deleteLater()

    def _file_explorer(self):
        win = AppWindow("File Explorer", self, (820, 540))
        box = QVBoxLayout(win)
        title = QLabel("📁  File Explorer")
        title.setObjectName("appTitle")
        box.addWidget(title)
        path = QLineEdit(os.path.expanduser("~"))
        box.addWidget(path)
        listing = QListWidget()
        box.addWidget(listing, 1)
        def load_dir(directory):
            listing.clear()
            path.setText(directory)
            try:
                for entry in sorted(os.scandir(directory), key=lambda e: (not e.is_dir(), e.name.lower())):
                    prefix = "📁  " if entry.is_dir() else "📄  "
                    item = QListWidgetItem(prefix + entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, entry.path)
                    listing.addItem(item)
            except OSError as exc:
                QMessageBox.warning(win, "File Explorer", str(exc))
        def open_selected(item):
            target = item.data(Qt.ItemDataRole.UserRole)
            if os.path.isdir(target):
                load_dir(target)
            else:
                try:
                    os.startfile(target)
                except Exception as exc:
                    QMessageBox.warning(win, "Cannot open file", str(exc))
        controls = QHBoxLayout()
        back = QPushButton("Home")
        back.setObjectName("subtle")
        browse = QPushButton("Choose folder")
        browse.setObjectName("action")
        controls.addWidget(back)
        controls.addWidget(browse)
        controls.addStretch()
        box.insertLayout(2, controls)
        back.clicked.connect(lambda: load_dir(os.path.expanduser("~")))
        browse.clicked.connect(lambda: (lambda d: load_dir(d) if d else None)(QFileDialog.getExistingDirectory(win, "Choose folder", path.text())))
        listing.itemDoubleClicked.connect(open_selected)
        path.returnPressed.connect(lambda: load_dir(path.text()))
        load_dir(path.text())
        return win

    def _terminal(self):
        win = AppWindow("AMH-OS Terminal", self, (820, 520))
        box = QVBoxLayout(win)
        title = QLabel("⌨️  Terminal")
        title.setObjectName("appTitle")
        box.addWidget(title)
        output = QTextEdit()
        output.setReadOnly(True)
        output.setPlainText("AMH-OS Terminal v2.0\\nWindows PowerShell session\\nType a command below and press Enter.\\n")
        box.addWidget(output, 1)
        command = QLineEdit()
        command.setPlaceholderText("Enter PowerShell command...")
        box.addWidget(command)
        def run_command():
            text = command.text().strip()
            if not text:
                return
            command.clear()
            output.append("\\nPS> " + text)
            try:
                result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", text],
                                        capture_output=True, text=True, timeout=30,
                                        cwd=os.path.expanduser("~"))
                output.append(result.stdout or "")
                if result.stderr:
                    output.append(result.stderr)
                output.append("[exit code: " + str(result.returncode) + "]")
            except Exception as exc:
                output.append(str(exc))
        command.returnPressed.connect(run_command)
        return win

    def _system_monitor(self):
        win = AppWindow("System Monitor", self, (650, 430))
        box = QVBoxLayout(win)
        title = QLabel("📊  System Monitor")
        title.setObjectName("appTitle")
        box.addWidget(title)
        labels = {}
        bars = {}
        for key, label_text in [("cpu", "CPU usage"), ("memory", "Memory usage"), ("disk", "System drive usage")]:
            box.addWidget(QLabel(label_text))
            label = QLabel("--")
            labels[key] = label
            box.addWidget(label)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bars[key] = bar
            box.addWidget(bar)
        detail = QLabel(platform.platform())
        detail.setObjectName("muted")
        box.addWidget(detail)
        timer = QTimer(win)
        def refresh():
            values = {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage(os.path.abspath(os.sep)).percent,
            }
            for key, value in values.items():
                labels[key].setText(f"{value:.1f}%")
                bars[key].setValue(int(value))
        timer.timeout.connect(refresh)
        timer.start(1000)
        refresh()
        return win

    def _settings(self):
        win = AppWindow("Settings", self, (650, 440))
        box = QVBoxLayout(win)
        title = QLabel("⚙️  Settings")
        title.setObjectName("appTitle")
        box.addWidget(title)
        for heading, value in [
            ("Operating environment", "AMH-OS Desktop is currently running as a desktop shell on Windows."),
            ("Version", VERSION),
            ("Host system", platform.platform()),
            ("Python", platform.python_version()),
            ("Project", "Tech-God-1111 / AMH-OS-COPRO"),
            ("Hardware roadmap", "ESP32-S3 and ESP32-WROOM coprocessor integration is planned for a later milestone."),
        ]:
            h = QLabel(heading)
            h.setStyleSheet("font-weight:700;color:#8db7ff;")
            v = QLabel(value)
            v.setWordWrap(True)
            v.setObjectName("muted")
            box.addWidget(h)
            box.addWidget(v)
        box.addStretch()
        return win

    def _about(self):
        win = AppWindow("About AMH-OS", self, (520, 330))
        box = QVBoxLayout(win)
        title = QLabel("◈  AMH-OS")
        title.setStyleSheet("font-size:30px;font-weight:800;")
        box.addWidget(title)
        box.addWidget(QLabel("Desktop Environment  •  Version " + VERSION))
        text = QLabel("A Python / PySide6 desktop-shell prototype featuring a full-screen desktop, shortcuts, Start menu, taskbar, app windows, File Explorer, Terminal and System Monitor. It is not yet a standalone bootable operating system.")
        text.setWordWrap(True)
        text.setObjectName("muted")
        box.addWidget(text)
        box.addStretch()
        close = QPushButton("Close")
        close.setObjectName("action")
        close.clicked.connect(win.close)
        box.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)
        return win

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key.Key_Escape:
            if self.start_menu and self.start_menu.isVisible():
                self.start_menu.close()
                self.start_menu = None
        elif event.key() == Qt.Key.Key_Q and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self.close()
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    desktop = AMHDesktop()
    desktop.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
