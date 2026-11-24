import json, logging, os, platform, sys, traceback, time
from datetime import datetime
from pathlib import Path
import psutil
import serial
from serial.tools import list_ports
from PySide6.QtCore import Qt, QTimer, QProcess, QUrl
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QTextCursor, QDesktopServices
from core.serial_protocol import LineBuffer
from core.calculator import evaluate_expression
from apps.processing_suite import ProcessingSuiteMixin

from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QDialog,QLabel,QPushButton,
 QVBoxLayout,QHBoxLayout,QGridLayout,QFrame,QLineEdit,QListWidget,QListWidgetItem,
 QTextEdit,QMessageBox,QFileDialog,QProgressBar,QComboBox,QCheckBox,QMenu,
 QTableWidget,QTableWidgetItem,QHeaderView)

VERSION = "10.2"
VERSION_NUM = 10
ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("APPDATA", str(Path.home()))) / "AMH-OS"
DATA.mkdir(parents=True, exist_ok=True)
LOG_PATH = DATA / "amh-os.log"
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
APPS = [("📁","File Explorer"),("🌐","Internet"),("📶","Connectivity Hub"),("⌨️","Terminal"),("📊","System Monitor"),
        ("📝","Notes"),("🧮","Calculator"),("⚙️","Settings"),("ℹ️","About AMH-OS")]
if VERSION_NUM >= 5: APPS.insert(5,("🔌","Serial Monitor"))
if VERSION_NUM >= 6: APPS.insert(6,("🧩","Hardware Center"))
if VERSION_NUM >= 7: APPS.insert(7,("🎨","Appearance"))
if VERSION_NUM >= 8: APPS.insert(8,("🛠️","Diagnostics"))
if VERSION_NUM >= 10:
    APPS.extend([
        ("📈","Workload Monitor"),("🗓️","Task Scheduler"),
        ("🧠","Resource Manager"),("🚀","Task Dispatcher"),
        ("📋","Result Manager"),("🛡️","Recovery Manager")
    ])

STYLE = """
* { font-family:'Segoe UI'; }
QWidget { color:#edf3ff; }
QDialog,QWidget#panel { background:#111a2b; }
QFrame#taskbar { background:#090f1d; border-top:1px solid #34425e; }
QFrame#popup { background:#111c30; border:1px solid #52688d; border-radius:14px; }
QPushButton { border:0; }
QPushButton#start { background:#294675; border-radius:9px; padding:9px 15px; font-weight:700; }
QPushButton#task,QPushButton#subtle { background:#23324a; border-radius:8px; padding:8px 12px; }
QPushButton#icon { background:rgba(12,23,45,145); border:1px solid #52688d; border-radius:10px; padding:10px; }
QPushButton#icon:hover,QPushButton#task:hover { background:#385582; }
QPushButton#action { background:#2d65c8; border-radius:8px; padding:9px 14px; }
QLineEdit,QComboBox { background:#1a2940; border:1px solid #3b4e6d; border-radius:8px; padding:9px; }
QListWidget { background:transparent; border:0; }
QListWidget::item { padding:9px; border-radius:8px; }
QListWidget::item:hover { background:#263b5d; }
QTextEdit { background:#09111e; border:1px solid #33445f; border-radius:8px; padding:8px; }
QProgressBar { background:#26354d; border:0; border-radius:5px; height:9px; }
QProgressBar::chunk { background:#5b9bff; border-radius:5px; }
QLabel#muted { color:#9eacc5; }
"""

class Wallpaper(QWidget):
    def paintEvent(self,event):
        p=QPainter(self); g=QLinearGradient(0,0,self.width(),self.height())
        g.setColorAt(0,QColor("#0c1730")); g.setColorAt(.55,QColor("#263f83")); g.setColorAt(1,QColor("#11152e"))
        p.fillRect(self.rect(),g); p.setPen(QColor(140,170,255,35))
        for r in (130,205,280):
            p.drawEllipse(int(self.width()*.72-r),int(self.height()*.4-r),r*2,r*2)
        p.setPen(QColor("#f0f4ff")); p.setFont(QFont("Segoe UI",26,QFont.Weight.Bold))
        p.drawText(32,self.height()-78,"AMH-OS")
        p.setPen(QColor(210,224,255,170)); p.setFont(QFont("Segoe UI",10))
        p.drawText(34,self.height()-54,"Your workspace. Your system.  •  Desktop v"+VERSION)

class AppWindow(QDialog):
    def __init__(self,title,parent,size=(720,470)):
        super().__init__(parent); self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window); self.resize(*size)
        self.setObjectName("panel"); self.setStyleSheet(STYLE)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,True)

class Desktop(ProcessingSuiteMixin, QMainWindow):
    APP_WINDOW = AppWindow
    APP_STYLE = STYLE
    def __init__(self):
        super().__init__(); self.setWindowTitle("AMH-OS Desktop v"+VERSION)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.Window)
        self.windows={}; self.tasks={}; self.popup_widget=None
        self.wall=Wallpaper(); self.setCentralWidget(self.wall)
        root=QVBoxLayout(self.wall); root.setContentsMargins(18,18,18,0)
        icons=QGridLayout(); icons.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        for i,(glyph,name) in enumerate(APPS):
            b=QPushButton(glyph+"\n"+name); b.setObjectName("icon"); b.setFixedSize(122,78)
            b.clicked.connect(lambda checked=False,n=name:self.open_app(n))
            icons.addWidget(b,i//3,i%3)
        root.addLayout(icons); root.addStretch()
        bar=QFrame(); bar.setObjectName("taskbar"); bar.setFixedHeight(60); row=QHBoxLayout(bar)
        self.start=QPushButton("◈  Start"); self.start.setObjectName("start")
        self.start.clicked.connect(self.toggle_start); row.addWidget(self.start)
        self.task_area=QHBoxLayout(); row.addLayout(self.task_area,1)
        quick=QPushButton("◉ Quick"); quick.setObjectName("subtle")
        quick.clicked.connect(self.toggle_quick); row.addWidget(quick)
        self.clock=QLabel(); self.clock.setMinimumWidth(180); self.clock.setAlignment(Qt.AlignmentFlag.AlignCenter); row.addWidget(self.clock)
        root.addWidget(bar)
        self.clock_timer=QTimer(self); self.clock_timer.timeout.connect(self.refresh_clock); self.clock_timer.start(1000); self.refresh_clock()
        self.wall.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.wall.customContextMenuRequested.connect(self.desktop_menu)
        logging.info("AMH-OS %s desktop initialized",VERSION)

    def refresh_clock(self):
        self.clock.setText(datetime.now().strftime("%a %d %b  •  %I:%M:%S %p"))

    def desktop_menu(self,pos):
        menu=QMenu(self); menu.addAction("Refresh desktop",self.wall.update)
        menu.addAction("Open Settings",lambda:self.open_app("Settings"))
        menu.addAction("New note",lambda:self.open_app("Notes"))
        menu.addSeparator(); menu.addAction("About AMH-OS",lambda:self.open_app("About AMH-OS"))
        menu.exec(self.wall.mapToGlobal(pos))

    def toggle_start(self):
        if self.popup_widget and self.popup_widget.isVisible():
            self.popup_widget.close(); self.popup_widget=None; return
        p=QFrame(self); p.setObjectName("popup"); p.setStyleSheet(STYLE)
        p.setGeometry(14,self.height()-520,390,490); self.popup_widget=p
        box=QVBoxLayout(p); heading=QLabel("AMH-OS"); heading.setStyleSheet("font-size:24px;font-weight:800"); box.addWidget(heading)
        search=QLineEdit(); search.setPlaceholderText("Search applications..."); box.addWidget(search)
        listing=QListWidget()
        for glyph,name in APPS:
            it=QListWidgetItem(glyph+"   "+name); it.setData(Qt.ItemDataRole.UserRole,name); listing.addItem(it)
        box.addWidget(listing,1)
        footer=QHBoxLayout(); footer.addWidget(QLabel("Desktop v"+VERSION)); footer.addStretch()
        exit_btn=QPushButton("Exit"); exit_btn.setObjectName("subtle"); exit_btn.clicked.connect(self.close); footer.addWidget(exit_btn); box.addLayout(footer)
        search.textChanged.connect(lambda q:self.filter_apps(listing,q))
        listing.itemDoubleClicked.connect(lambda it:(self.open_app(it.data(Qt.ItemDataRole.UserRole)),p.close()))
        p.show(); p.raise_(); search.setFocus()

    def filter_apps(self,listing,q):
        for i in range(listing.count()):
            listing.item(i).setHidden(q.casefold() not in listing.item(i).text().casefold())

    def toggle_quick(self):
        if self.popup_widget and self.popup_widget.isVisible():
            self.popup_widget.close(); self.popup_widget=None; return
        p=QFrame(self); p.setObjectName("popup"); p.setStyleSheet(STYLE)
        p.setGeometry(self.width()-330,self.height()-290,310,260); self.popup_widget=p
        box=QVBoxLayout(p); h=QLabel("Quick settings"); h.setStyleSheet("font-size:20px;font-weight:700"); box.addWidget(h)
        for name in ("Wi-Fi preview","Bluetooth preview","Night light preview"):
            b=QPushButton("○  "+name); b.setObjectName("subtle"); b.setCheckable(True)
            b.clicked.connect(lambda checked,btn=b,n=name:btn.setText(("✓  " if checked else "○  ")+n)); box.addWidget(b)
        note=QLabel("Preview toggles only; Windows settings are not changed."); note.setWordWrap(True); note.setObjectName("muted"); box.addWidget(note)
        p.show(); p.raise_()

    def open_app(self,name):
        if name == "Internet":
            if not QDesktopServices.openUrl(QUrl("https://www.google.com")):
                QMessageBox.warning(self,"Browser unavailable","Windows could not open the default browser.")
            return
        existing=self.windows.get(name)
        if existing:
            existing.showNormal(); existing.raise_(); existing.activateWindow(); return
        builders={"File Explorer":self.file_explorer,"Terminal":self.terminal,"System Monitor":self.monitor,
                  "Notes":self.notes,"Calculator":self.calculator,"Settings":self.settings,"About AMH-OS":self.about,"Connectivity Hub":self.connectivity_hub}
        if VERSION_NUM>=5: builders["Serial Monitor"]=self.serial_monitor
        if VERSION_NUM>=6: builders["Hardware Center"]=self.hardware_center
        if VERSION_NUM>=7: builders["Appearance"]=self.appearance
        if VERSION_NUM>=8: builders["Diagnostics"]=self.diagnostics
        if VERSION_NUM>=10:
            builders.update({
                "Workload Monitor":self.workload_monitor,
                "Task Scheduler":self.task_scheduler,
                "Resource Manager":self.resource_manager,
                "Task Dispatcher":self.task_dispatcher,
                "Result Manager":self.result_manager,
                "Recovery Manager":self.recovery_manager
            })
        if name not in builders:return
        try: w=builders[name]()
        except Exception as exc:
            logging.exception("Could not open %s",name); QMessageBox.critical(self,"Application error",f"{name} could not open:\n{exc}"); return
        self.windows[name]=w
        task=QPushButton(name); task.setObjectName("task"); task.clicked.connect(lambda checked=False,n=name:self.focus_app(n))
        self.task_area.addWidget(task); self.tasks[name]=task
        w.destroyed.connect(lambda obj=None,n=name:self.remove_task(n))
        w.show(); w.raise_(); w.activateWindow(); logging.info("Opened app: %s",name)

    def focus_app(self,name):
        w=self.windows.get(name)
        if w: w.showNormal(); w.raise_(); w.activateWindow()

    def remove_task(self,name):
        self.windows.pop(name,None); b=self.tasks.pop(name,None)
        if b: self.task_area.removeWidget(b); b.deleteLater()

    def file_explorer(self):
        w=AppWindow("File Explorer",self,(820,530)); box=QVBoxLayout(w)
        box.addWidget(QLabel("📁  File Explorer")); path=QLineEdit(str(Path.home())); box.addWidget(path)
        controls=QHBoxLayout(); home=QPushButton("Home"); home.setObjectName("subtle")
        choose=QPushButton("Choose folder"); choose.setObjectName("action"); controls.addWidget(home); controls.addWidget(choose); box.addLayout(controls)
        listing=QListWidget(); box.addWidget(listing,1)
        def load(directory):
            listing.clear()
            try:
                p=Path(directory).expanduser().resolve(); path.setText(str(p))
                for entry in sorted(p.iterdir(),key=lambda x:(not x.is_dir(),x.name.casefold())):
                    item=QListWidgetItem(("📁  " if entry.is_dir() else "📄  ")+entry.name)
                    item.setData(Qt.ItemDataRole.UserRole,str(entry)); listing.addItem(item)
            except Exception as exc: QMessageBox.warning(w,"File Explorer",str(exc))
        def open_item(item):
            target=Path(item.data(Qt.ItemDataRole.UserRole))
            if target.is_dir(): load(target)
            else:
                try: os.startfile(str(target))
                except Exception as exc: QMessageBox.warning(w,"Open file",str(exc))
        home.clicked.connect(lambda:load(Path.home()))
        choose.clicked.connect(lambda:(lambda d:load(d) if d else None)(QFileDialog.getExistingDirectory(w,"Choose folder",path.text())))
        path.returnPressed.connect(lambda:load(path.text())); listing.itemDoubleClicked.connect(open_item)
        load(Path.home()); return w

    def terminal(self):
        w=AppWindow("AMH-OS Terminal",self,(800,510)); box=QVBoxLayout(w)
        box.addWidget(QLabel("⌨️  Windows PowerShell"))
        warning=QLabel("Commands run on your Windows account with its normal permissions. This is not a sandbox.")
        warning.setWordWrap(True); warning.setObjectName("muted"); box.addWidget(warning)
        output=QTextEdit(); output.setReadOnly(True)
        output.setPlainText("AMH-OS Terminal v"+VERSION+"\nCommands execute in Windows PowerShell.\n")
        box.addWidget(output,1)
        command=QLineEdit(); command.setPlaceholderText("Enter a PowerShell command...")
        box.addWidget(command)
        process=QProcess(w)
        process.setProgram("powershell.exe")
        def append_bytes(data):
            if data:
                output.moveCursor(QTextCursor.MoveOperation.End)
                output.insertPlainText(bytes(data).decode("utf-8",errors="replace"))
        def read_stdout(): append_bytes(process.readAllStandardOutput())
        def read_stderr(): append_bytes(process.readAllStandardError())
        def finished(exit_code,exit_status):
            read_stdout(); read_stderr()
            output.append(f"\n[PowerShell finished — exit code {exit_code}]")
            command.setEnabled(True); command.setFocus()
        def failed(error):
            output.append("\n[PowerShell process error] "+process.errorString())
            command.setEnabled(True)
        process.readyReadStandardOutput.connect(read_stdout)
        process.readyReadStandardError.connect(read_stderr)
        process.finished.connect(finished)
        process.errorOccurred.connect(failed)
        def run():
            text=command.text().strip()
            if not text:return
            if process.state()!=QProcess.ProcessState.NotRunning:
                output.append("[A command is already running.]"); return
            answer=QMessageBox.question(
                w,"Run PowerShell command?",
                "This command will execute on Windows with your current user permissions:\n\n"+text+
                "\n\nOnly continue if you trust this command.",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if answer!=QMessageBox.StandardButton.Yes:return
            command.clear(); command.setEnabled(False)
            output.append("\nPS> "+text+"\n")
            process.setArguments(["-NoLogo","-NoProfile","-Command",text])
            process.start()
        command.returnPressed.connect(run)
        return w

    def monitor(self):
        w=AppWindow("System Monitor",self,(620,420)); box=QVBoxLayout(w); box.addWidget(QLabel("📊  System Monitor"))
        labels={}; bars={}
        for key,title in (("cpu","CPU usage"),("mem","Memory usage"),("disk","System drive")):
            box.addWidget(QLabel(title)); labels[key]=QLabel("--"); box.addWidget(labels[key])
            bars[key]=QProgressBar(); bars[key].setRange(0,100); box.addWidget(bars[key])
        timer=QTimer(w)
        def refresh():
            values={"cpu":psutil.cpu_percent(),"mem":psutil.virtual_memory().percent,"disk":psutil.disk_usage(os.path.abspath(os.sep)).percent}
            for key,value in values.items(): labels[key].setText(f"{value:.1f}%"); bars[key].setValue(int(value))
        timer.timeout.connect(refresh); timer.start(1000); refresh(); return w

    def notes(self):
        w=AppWindow("Notes",self,(650,500)); box=QVBoxLayout(w); box.addWidget(QLabel("📝  Notes"))
        editor=QTextEdit(); note_file=DATA/"notes.txt"
        try: editor.setPlainText(note_file.read_text(encoding="utf-8") if note_file.exists() else "")
        except OSError: editor.setPlainText("")
        editor.setPlaceholderText("Write your notes..."); box.addWidget(editor,1)
        save=QPushButton("Save notes"); save.setObjectName("action")
        def save_notes():
            try: note_file.write_text(editor.toPlainText(),encoding="utf-8"); QMessageBox.information(w,"Notes","Notes saved to your user data folder.")
            except OSError as exc: QMessageBox.critical(w,"Save failed",str(exc))
        save.clicked.connect(save_notes); box.addWidget(save); return w

    def calculator(self):
        w=AppWindow("Calculator",self,(430,230)); box=QVBoxLayout(w); box.addWidget(QLabel("🧮  Calculator"))
        entry=QLineEdit(); entry.setPlaceholderText("Example: (12 + 4) * 3"); box.addWidget(entry)
        result=QLabel("Enter an expression"); box.addWidget(result)
        def calc():
            try: result.setText(str(evaluate_expression(entry.text())))
            except Exception as exc: result.setText("Invalid expression: "+str(exc))
        btn=QPushButton("Calculate"); btn.setObjectName("action")
        btn.clicked.connect(calc); entry.returnPressed.connect(calc); box.addWidget(btn)
        return w

    def connectivity_hub(self):
        w=AppWindow("Connectivity Hub",self,(680,480))
        box=QVBoxLayout(w)
        title=QLabel("📶  Connectivity Hub")
        title.setStyleSheet("font-size:22px;font-weight:800")
        box.addWidget(title)
        note=QLabel("AMH-OS uses your Windows network and Bluetooth adapters. These controls open the native Windows panels, so your existing drivers, saved networks and pairing settings stay in control.")
        note.setWordWrap(True); note.setObjectName("muted"); box.addWidget(note)

        def panel(title_text,description,settings_uri,button_text):
            frame=QFrame(); frame.setObjectName("popup")
            layout=QVBoxLayout(frame)
            heading=QLabel(title_text); heading.setStyleSheet("font-size:17px;font-weight:700")
            detail=QLabel(description); detail.setWordWrap(True); detail.setObjectName("muted")
            action=QPushButton(button_text); action.setObjectName("action")
            action.clicked.connect(lambda checked=False,u=settings_uri:
                QDesktopServices.openUrl(QUrl(u)))
            layout.addWidget(heading); layout.addWidget(detail); layout.addWidget(action)
            box.addWidget(frame)

        panel("📡  Wi-Fi",
              "View nearby wireless networks, connect or disconnect, and manage your Wi-Fi adapter in Windows.",
              "ms-settings:network-wifi","Open Wi-Fi settings")
        panel("ᛒ  Bluetooth",
              "Turn Bluetooth on or off, pair devices, and manage connected keyboards, headphones and other accessories in Windows.",
              "ms-settings:bluetooth","Open Bluetooth settings")
        panel("🌐  Network status",
              "Open Windows network status and troubleshoot your internet connection.",
              "ms-settings:network-status","Open network status")
        box.addStretch()
        footer=QLabel("Note: Wi-Fi and Bluetooth availability depends on the adapters and drivers installed on this PC.")
        footer.setWordWrap(True); footer.setObjectName("muted"); box.addWidget(footer)
        return w

    def settings(self):
        w=AppWindow("Settings",self,(650,430)); box=QVBoxLayout(w); box.addWidget(QLabel("⚙️  Settings"))
        for key,value in (("Version",VERSION),("Mode","Windows-hosted desktop environment"),("Host",platform.node()),
                          ("Operating system",platform.platform()),("Python",platform.python_version()),
                          ("User data",str(DATA)),("Hardware","USB serial tools are available in later release branches.")):
            label=QLabel(key); label.setStyleSheet("font-weight:700;color:#8db7ff"); box.addWidget(label)
            value_label=QLabel(value); value_label.setWordWrap(True); value_label.setObjectName("muted"); box.addWidget(value_label)
        return w

    def about(self):
        w=AppWindow("About AMH-OS",self,(540,330)); box=QVBoxLayout(w)
        title=QLabel("◈  AMH-OS"); title.setStyleSheet("font-size:30px;font-weight:800"); box.addWidget(title)
        desc=QLabel("Desktop Environment • Version "+VERSION+"\n\nA Python/PySide6 desktop shell running on Windows. It is a prototype, not a standalone bootable operating system.")
        desc.setWordWrap(True); desc.setObjectName("muted"); box.addWidget(desc); return w

    def serial_monitor(self):
        w=AppWindow("Serial Monitor",self,(760,520)); box=QVBoxLayout(w); box.addWidget(QLabel("🔌  USB Serial Monitor"))
        row=QHBoxLayout(); ports=QComboBox(); baud=QComboBox(); baud.addItems(["115200","9600","57600","230400"])
        refresh=QPushButton("Refresh ports"); refresh.setObjectName("subtle"); connect=QPushButton("Connect"); connect.setObjectName("action")
        row.addWidget(ports,1); row.addWidget(baud); row.addWidget(refresh); row.addWidget(connect); box.addLayout(row)
        output=QTextEdit(); output.setReadOnly(True); box.addWidget(output,1)
        sendrow=QHBoxLayout(); command=QLineEdit(); command.setPlaceholderText("Send text (newline appended)")
        send=QPushButton("Send"); send.setObjectName("action"); sendrow.addWidget(command,1); sendrow.addWidget(send); box.addLayout(sendrow)
        state={"port":None}
        def scan():
            ports.clear()
            for p in list_ports.comports(): ports.addItem(f"{p.device} — {p.description}",p.device)
        def toggle():
            try:
                if state["port"]:
                    state["port"].close(); state["port"]=None; connect.setText("Connect"); output.append("[Disconnected]")
                else:
                    dev=ports.currentData()
                    if not dev: raise RuntimeError("No COM port selected.")
                    state["port"]=serial.Serial(dev,int(baud.currentText()),timeout=0)
                    connect.setText("Disconnect"); output.append("[Connected to "+dev+"]")
            except Exception as exc: QMessageBox.warning(w,"Serial connection",str(exc))
        def transmit():
            try:
                if not state["port"]: raise RuntimeError("Connect to a COM port first.")
                state["port"].write((command.text()+"\n").encode("utf-8")); output.append("> "+command.text()); command.clear()
            except Exception as exc: QMessageBox.warning(w,"Serial send",str(exc))
        def poll():
            port=state["port"]
            if port and port.is_open:
                try:
                    waiting=port.in_waiting
                    if waiting:
                        data=port.read(waiting)
                        if data:
                            output.moveCursor(QTextCursor.MoveOperation.End)
                            output.insertPlainText(data.decode("utf-8",errors="replace"))
                except Exception as exc:
                    output.append("\n[Read error] "+str(exc))
                    try: port.close()
                    except Exception: pass
                    state["port"]=None; connect.setText("Connect")
        refresh.clicked.connect(scan); connect.clicked.connect(toggle); send.clicked.connect(transmit); command.returnPressed.connect(transmit)
        timer=QTimer(w); timer.timeout.connect(poll); timer.start(50)
        def cleanup():
            if state["port"]:
                try: state["port"].close()
                except Exception: pass
        w.destroyed.connect(cleanup); scan(); return w

    def hardware_center(self):
        w=AppWindow("Hardware Center",self,(760,540)); box=QVBoxLayout(w)
        box.addWidget(QLabel("🧩  AMH-OS Hardware Center"))
        intro=QLabel("Connect to an ESP32-S3 USB bridge running the AMH newline-delimited JSON protocol.")
        intro.setWordWrap(True); intro.setObjectName("muted"); box.addWidget(intro)
        row=QHBoxLayout(); port=QComboBox(); port.setMinimumWidth(230)
        baud=QComboBox(); baud.addItems(["115200","9600","57600","230400"])
        scan=QPushButton("Refresh ports"); scan.setObjectName("subtle")
        connect_btn=QPushButton("Connect"); connect_btn.setObjectName("action")
        row.addWidget(port,1); row.addWidget(baud); row.addWidget(scan); row.addWidget(connect_btn); box.addLayout(row)
        status=QLabel("Disconnected — select the ESP32-S3 COM port.")
        status.setObjectName("muted"); box.addWidget(status)
        output=QTextEdit(); output.setReadOnly(True)
        output.setPlaceholderText("Connection messages and JSON responses appear here.")
        box.addWidget(output,1)
        buttons=QHBoxLayout(); actions={}
        for cmd in ("identify","ping","status"):
            button=QPushButton(cmd.title()); button.setObjectName("action")
            button.setEnabled(False); buttons.addWidget(button); actions[cmd]=button
        box.addLayout(buttons)
        state={"serial":None,"lines":LineBuffer(512),"pending_id":None,
               "pending_cmd":None,"pending_since":0.0,"next_id":0}
        def log(message):
            output.append(str(message)); output.moveCursor(QTextCursor.MoveOperation.End)
        def set_connected(connected,device=""):
            connect_btn.setText("Disconnect" if connected else "Connect")
            port.setEnabled(not connected); baud.setEnabled(not connected); scan.setEnabled(not connected)
            for button in actions.values(): button.setEnabled(connected)
            status.setText(("Connected to "+device+" — ready for commands") if connected
                           else "Disconnected — select the ESP32-S3 COM port.")
        def scan_ports():
            previous=port.currentData()
            port.blockSignals(True); port.clear()
            found=list(list_ports.comports())
            for item in found: port.addItem(f"{item.device} — {item.description}",item.device)
            if previous:
                index=port.findData(previous)
                if index>=0: port.setCurrentIndex(index)
            port.blockSignals(False)
            if not found: status.setText("No serial ports found. Connect the ESP32-S3 and refresh.")
            elif not state["serial"]: status.setText(f"Found {len(found)} serial port(s). Select the ESP32-S3 port.")
            return len(found)
        def disconnect_device(message="[Disconnected]"):
            device=state["serial"]; state["serial"]=None
            state["lines"].reset(); state["pending_id"]=None; state["pending_cmd"]=None
            if device:
                try: device.close()
                except Exception: pass
            set_connected(False); log(message)
        def connect_device():
            connection=None
            try:
                device=port.currentData()
                if not device: raise RuntimeError("No COM port selected. Connect the ESP32-S3 and refresh ports.")
                connection=serial.Serial(device,int(baud.currentText()),timeout=0,write_timeout=1)
                connection.dtr=False; connection.rts=False
                state["serial"]=connection; state["lines"].reset()
                state["pending_id"]=None; state["pending_cmd"]=None
                set_connected(True,device)
                log(f"[Connected to {device} at {baud.currentText()} baud]")
                log("[Waiting for a compatible newline-delimited JSON bridge]")
            except Exception as exc:
                if connection is not None:
                    try: connection.close()
                    except Exception: pass
                state["serial"]=None; set_connected(False)
                status.setText("Connection failed: "+str(exc)); log("[Connection error] "+str(exc))
        def toggle_connection():
            if state["serial"]: disconnect_device()
            else: connect_device()
        def send_cmd(cmd):
            device=state["serial"]
            if not device or not device.is_open:
                status.setText("Not connected. Connect to the ESP32-S3 first."); return
            if state["pending_id"] is not None:
                status.setText("A command is already waiting for a response."); return
            try:
                state["next_id"]=(state["next_id"]+1)%1000000
                request_id=state["next_id"]
                payload=json.dumps({"id":request_id,"cmd":cmd},separators=(",",":"))+"\n"
                device.write(payload.encode("utf-8"))
                state["pending_id"]=request_id; state["pending_cmd"]=cmd
                state["pending_since"]=time.monotonic()
                status.setText(f"Sent {cmd}; waiting for device response…")
                log("> "+payload.rstrip("\n"))
            except Exception as exc: disconnect_device("[Write failed] "+str(exc))
        def handle_line(line):
            if not line.strip(): return
            try:
                reply=json.loads(line)
                if not isinstance(reply,dict): raise ValueError("JSON response must be an object")
                reply_id=reply.get("id")
                if state["pending_id"] is not None and str(reply_id)==str(state["pending_id"]):
                    status.setText(f"Received response to {state['pending_cmd']}.")
                    state["pending_id"]=None; state["pending_cmd"]=None
                log("< "+json.dumps(reply,ensure_ascii=False))
            except (ValueError,TypeError) as exc: log("[Invalid JSON response] "+str(exc)+" — "+line)
        def poll_serial():
            device=state["serial"]
            if device and device.is_open:
                try:
                    waiting=device.in_waiting
                    if waiting:
                        chunk=device.read(waiting)
                        for raw in state["lines"].feed(chunk):
                            handle_line(raw.decode("utf-8",errors="replace"))
                        if state["lines"].discarded_frames:
                            log("[Warning] Oversized serial frame discarded.")
                            state["lines"].discarded_frames=0
                    if state["pending_id"] is not None and time.monotonic()-state["pending_since"]>3.0:
                        cmd=state["pending_cmd"]
                        state["pending_id"]=None; state["pending_cmd"]=None
                        status.setText(f"No response to {cmd}. Check the bridge firmware and protocol.")
                        log(f"[Timeout] No JSON response received for {cmd} within 3 seconds.")
                except Exception as exc: disconnect_device("[Serial read error] "+str(exc))
        scan.clicked.connect(scan_ports); connect_btn.clicked.connect(toggle_connection)
        for cmd,button in actions.items(): button.clicked.connect(lambda checked=False,c=cmd:send_cmd(c))
        timer=QTimer(w); timer.timeout.connect(poll_serial); timer.start(30)
        def cleanup():
            timer.stop(); device=state.get("serial")
            if device:
                try: device.close()
                except Exception: pass
                state["serial"]=None
        w.destroyed.connect(cleanup); scan_ports()
        return w

    def appearance(self):
        w=AppWindow("Appearance",self,(500,300)); box=QVBoxLayout(w); box.addWidget(QLabel("🎨  Appearance"))
        box.addWidget(QLabel("Choose a desktop accent preset (preview for future theme work)."))
        choice=QComboBox(); choice.addItems(["Ocean blue","Midnight","Violet"]); box.addWidget(choice)
        info=QLabel("Theme preferences are stored in this release as a preview only."); info.setWordWrap(True); info.setObjectName("muted"); box.addWidget(info)
        return w

    def diagnostics(self):
        w=AppWindow("Diagnostics",self,(700,480)); box=QVBoxLayout(w); box.addWidget(QLabel("🛠️  AMH-OS Diagnostics"))
        report=QTextEdit(); report.setReadOnly(True); box.addWidget(report,1)
        report.setPlainText("\n".join([f"AMH-OS {VERSION}",f"Python {platform.python_version()}",platform.platform(),
            f"CPU cores: {psutil.cpu_count()}",f"RAM: {psutil.virtual_memory().total//(1024**3)} GB",
            f"Log file: {LOG_PATH}",f"User data: {DATA}"]))
        btn=QPushButton("Open log folder"); btn.setObjectName("action")
        btn.clicked.connect(lambda:os.startfile(str(DATA))); box.addWidget(btn); return w


    # v10.0 processing-suite applications are interface-first prototypes.
    # Live processor telemetry and task execution will be added in later stages.
    def keyPressEvent(self,event):
        if event.key()==Qt.Key.Key_F11: self.showNormal() if self.isFullScreen() else self.showFullScreen()
        elif event.key()==Qt.Key.Key_Escape and self.popup_widget:
            self.popup_widget.close(); self.popup_widget=None
        elif event.key()==Qt.Key.Key_Q and event.modifiers()==(Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.ShiftModifier): self.close()
        else: super().keyPressEvent(event)

def exception_hook(exc_type,exc_value,exc_tb):
    logging.critical("Unhandled exception",exc_info=(exc_type,exc_value,exc_tb))
    traceback.print_exception(exc_type,exc_value,exc_tb)
    sys.__excepthook__(exc_type,exc_value,exc_tb)

def main():
    sys.excepthook=exception_hook
    app=QApplication(sys.argv); app.setApplicationName("AMH-OS"); app.setStyle("Fusion"); app.setStyleSheet(STYLE)
    desktop=Desktop(); desktop.showFullScreen()
    logging.info("Event loop starting")
    return app.exec()

if __name__=="__main__":
    try: sys.exit(main())
    except Exception:
        logging.exception("Fatal startup failure"); raise
