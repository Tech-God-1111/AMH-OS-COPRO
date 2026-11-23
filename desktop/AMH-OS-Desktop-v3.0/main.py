import ast, operator, os, platform, subprocess, sys
from datetime import datetime
import psutil
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
 QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLineEdit, QListWidget, QListWidgetItem,
 QDialog, QTextEdit, QFileDialog, QMenu, QMessageBox, QProgressBar)

VERSION = "3.0.0"
APPS = [("📁","File Explorer"),("⌨️","Terminal"),("📊","System Monitor"),
        ("📝","Notes"),("🧮","Calculator"),("⚙️","Settings"),("ℹ️","About AMH-OS")]
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
QLineEdit { background:#1a2940; border:1px solid #3b4e6d; border-radius:8px; padding:10px; }
QListWidget { background:transparent; border:0; }
QListWidget::item { padding:10px; border-radius:8px; }
QListWidget::item:hover { background:#263b5d; }
QTextEdit { background:#09111e; border:1px solid #33445f; border-radius:8px; padding:8px; }
QProgressBar { background:#26354d; border:0; border-radius:5px; height:9px; }
QProgressBar::chunk { background:#5b9bff; border-radius:5px; }
QLabel#muted { color:#9eacc5; }
"""
class Wallpaper(QWidget):
    def paintEvent(self, event):
        p=QPainter(self); g=QLinearGradient(0,0,self.width(),self.height())
        g.setColorAt(0,QColor("#0c1730")); g.setColorAt(.5,QColor("#263f83")); g.setColorAt(1,QColor("#11152e"))
        p.fillRect(self.rect(),g); p.setPen(QColor(140,170,255,35))
        for r in (130,200,270):
            p.drawEllipse(int(self.width()*.72-r),int(self.height()*.4-r),r*2,r*2)
        p.setPen(QColor("#f0f4ff")); p.setFont(QFont("Segoe UI",26,QFont.Weight.Bold))
        p.drawText(32,self.height()-78,"AMH-OS")
        p.setPen(QColor(210,224,255,170)); p.setFont(QFont("Segoe UI",10))
        p.drawText(34,self.height()-54,"Your workspace. Your system.  •  Desktop v3.0")

class AppWindow(QDialog):
    def __init__(self,title,parent,size=(720,470)):
        super().__init__(parent); self.setWindowTitle(title); self.setWindowFlags(Qt.WindowType.Window)
        self.resize(*size); self.setObjectName("panel"); self.setStyleSheet(STYLE)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,True)

class Desktop(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("AMH-OS v3.0")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.Window)
        self.windows={}; self.tasks={}; self.notes_text=""
        self.wall=Wallpaper(); self.setCentralWidget(self.wall)
        root=QVBoxLayout(self.wall); root.setContentsMargins(18,18,18,0)
        icons=QGridLayout(); icons.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        for i,(glyph,name) in enumerate(APPS[:6]):
            b=QPushButton(glyph+"\n"+name); b.setObjectName("icon"); b.setFixedSize(118,78)
            b.clicked.connect(lambda checked=False,n=name:self.open_app(n)); icons.addWidget(b,i//2,i%2)
        root.addLayout(icons); root.addStretch()
        bar=QFrame(); bar.setObjectName("taskbar"); bar.setFixedHeight(60); row=QHBoxLayout(bar)
        self.start=QPushButton("◈  Start"); self.start.setObjectName("start"); self.start.clicked.connect(self.start_menu); row.addWidget(self.start)
        self.task_area=QHBoxLayout(); row.addLayout(self.task_area,1)
        quick=QPushButton("◉ Quick"); quick.setObjectName("subtle"); quick.clicked.connect(self.quick_panel); row.addWidget(quick)
        self.clock=QLabel(); self.clock.setMinimumWidth(175); self.clock.setAlignment(Qt.AlignmentFlag.AlignCenter); row.addWidget(self.clock)
        root.addWidget(bar); self.timer=QTimer(self); self.timer.timeout.connect(lambda:self.clock.setText(datetime.now().strftime("%a %d %b  •  %I:%M:%S %p"))); self.timer.start(1000)
        self.clock.setText(datetime.now().strftime("%a %d %b  •  %I:%M:%S %p"))
        self.wall.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); self.wall.customContextMenuRequested.connect(self.desktop_menu)

    def desktop_menu(self,pos):
        m=QMenu(self); m.addAction("Refresh desktop",self.wall.update); m.addAction("New note",lambda:self.open_app("Notes"))
        m.addAction("Open Settings",lambda:self.open_app("Settings")); m.addSeparator(); m.addAction("About AMH-OS",lambda:self.open_app("About AMH-OS"))
        m.exec(self.wall.mapToGlobal(pos))

    def popup(self,object_name,geometry):
        w=QFrame(self); w.setObjectName("popup"); w.setStyleSheet(STYLE); w.setGeometry(*geometry); return w

    def start_menu(self):
        if hasattr(self,"start_popup") and self.start_popup:
            self.start_popup.close()
        p=self.popup("popup",(16,self.height()-520,385,490)); self.start_popup=p; box=QVBoxLayout(p)
        h=QLabel("AMH-OS"); h.setStyleSheet("font-size:24px;font-weight:800"); box.addWidget(h)
        search=QLineEdit(); search.setPlaceholderText("Search apps..."); box.addWidget(search)
        listing=QListWidget()
        for glyph,name in APPS:
            it=QListWidgetItem(glyph+"   "+name); it.setData(Qt.ItemDataRole.UserRole,name); listing.addItem(it)
        box.addWidget(listing,1)
        foot=QHBoxLayout(); foot.addWidget(QLabel("Desktop v3.0")); foot.addStretch()
        power=QPushButton("Exit"); power.setObjectName("subtle"); power.clicked.connect(self.close); foot.addWidget(power); box.addLayout(foot)
        search.textChanged.connect(lambda q:self.filter_apps(listing,q))
        listing.itemDoubleClicked.connect(lambda it:(self.open_app(it.data(Qt.ItemDataRole.UserRole)),p.close()))
        p.show(); p.raise_(); search.setFocus()

    def filter_apps(self,listing,q):
        for i in range(listing.count()): listing.item(i).setHidden(q.casefold() not in listing.item(i).text().casefold())

    def quick_panel(self):
        if hasattr(self,"quick_popup") and self.quick_popup: self.quick_popup.close()
        p=self.popup("popup",(self.width()-330,self.height()-300,310,270)); self.quick_popup=p; box=QVBoxLayout(p)
        h=QLabel("Quick settings"); h.setStyleSheet("font-size:20px;font-weight:700"); box.addWidget(h)
        for name in ("Wi-Fi preview","Bluetooth preview","Night light preview"):
            b=QPushButton("○  "+name); b.setObjectName("subtle"); b.setCheckable(True)
            b.clicked.connect(lambda checked,btn=b,n=name:btn.setText(("✓  " if checked else "○  ")+n)); box.addWidget(b)
        note=QLabel("Preview controls only; they do not change Windows settings."); note.setWordWrap(True); note.setObjectName("muted"); box.addWidget(note)
        p.show(); p.raise_()

    def open_app(self,name):
        if name in self.windows and self.windows[name].isVisible():
            w=self.windows[name]
            if w.isMinimized(): w.showNormal()
            w.raise_(); w.activateWindow(); return
        builder={"File Explorer":self.file_explorer,"Terminal":self.terminal,"System Monitor":self.monitor,
                 "Notes":self.notes,"Calculator":self.calculator,"Settings":self.settings,"About AMH-OS":self.about}.get(name)
        if not builder:return
        w=builder(); self.windows[name]=w
        b=QPushButton(name); b.setObjectName("task"); b.clicked.connect(lambda checked=False,n=name:self.focus_app(n))
        self.task_area.addWidget(b); self.tasks[name]=b
        w.destroyed.connect(lambda obj=None,n=name:self.remove_task(n)); w.show(); w.raise_(); w.activateWindow()

    def focus_app(self,name):
        w=self.windows.get(name)
        if w:
            if w.isMinimized():w.showNormal()
            w.raise_();w.activateWindow()

    def remove_task(self,name):
        self.windows.pop(name,None); b=self.tasks.pop(name,None)
        if b:self.task_area.removeWidget(b);b.deleteLater()

    def file_explorer(self):
        w=AppWindow("File Explorer",self,(820,530)); box=QVBoxLayout(w); box.addWidget(QLabel("📁  File Explorer"))
        path=QLineEdit(os.path.expanduser("~")); box.addWidget(path); listing=QListWidget(); box.addWidget(listing,1)
        def load(d):
            listing.clear();path.setText(d)
            try:
                for e in sorted(os.scandir(d),key=lambda x:(not x.is_dir(),x.name.casefold())):
                    it=QListWidgetItem(("📁  " if e.is_dir() else "📄  ")+e.name);it.setData(Qt.ItemDataRole.UserRole,e.path);listing.addItem(it)
            except OSError as ex:QMessageBox.warning(w,"File Explorer",str(ex))
        def open_item(it):
            target=it.data(Qt.ItemDataRole.UserRole)
            if os.path.isdir(target):load(target)
            else:
                try:os.startfile(target)
                except OSError as ex:QMessageBox.warning(w,"Open file",str(ex))
        controls=QHBoxLayout(); home=QPushButton("Home");home.setObjectName("subtle")
        choose=QPushButton("Choose folder");choose.setObjectName("action");controls.addWidget(home);controls.addWidget(choose);box.insertLayout(2,controls)
        home.clicked.connect(lambda:load(os.path.expanduser("~")))
        choose.clicked.connect(lambda:(lambda d:load(d) if d else None)(QFileDialog.getExistingDirectory(w,"Choose folder",path.text())))
        path.returnPressed.connect(lambda:load(path.text()));listing.itemDoubleClicked.connect(open_item);load(path.text());return w

    def terminal(self):
        w=AppWindow("AMH-OS Terminal",self,(800,510));box=QVBoxLayout(w);box.addWidget(QLabel("⌨️  PowerShell Terminal"))
        out=QTextEdit();out.setReadOnly(True);out.setPlainText("AMH-OS Terminal v3.0\nWindows PowerShell session\n");box.addWidget(out,1)
        cmd=QLineEdit();cmd.setPlaceholderText("PowerShell command...");box.addWidget(cmd)
        def run():
            text=cmd.text().strip()
            if not text:return
            cmd.clear();out.append("\nPS> "+text)
            try:
                r=subprocess.run(["powershell.exe","-NoProfile","-Command",text],capture_output=True,text=True,timeout=30)
                out.append(r.stdout or "");out.append(r.stderr or "");out.append("[exit code: "+str(r.returncode)+"]")
            except Exception as ex:out.append(str(ex))
        cmd.returnPressed.connect(run);return w

    def monitor(self):
        w=AppWindow("System Monitor",self,(620,420));box=QVBoxLayout(w);box.addWidget(QLabel("📊  System Monitor"))
        labels={};bars={}
        for key,title in (("cpu","CPU"),("mem","Memory"),("disk","System drive")):
            box.addWidget(QLabel(title));labels[key]=QLabel("--");box.addWidget(labels[key]);bars[key]=QProgressBar();bars[key].setRange(0,100);box.addWidget(bars[key])
        timer=QTimer(w)
        def refresh():
            vals={"cpu":psutil.cpu_percent(),"mem":psutil.virtual_memory().percent,"disk":psutil.disk_usage(os.path.abspath(os.sep)).percent}
            for k,v in vals.items():labels[k].setText(f"{v:.1f}%");bars[k].setValue(int(v))
        timer.timeout.connect(refresh);timer.start(1000);refresh();return w

    def notes(self):
        w=AppWindow("Notes",self,(620,470));box=QVBoxLayout(w);box.addWidget(QLabel("📝  Notes"))
        edit=QTextEdit();edit.setPlainText(self.notes_text);edit.setPlaceholderText("Write a note for this session...");box.addWidget(edit,1)
        save=QPushButton("Save for this session");save.setObjectName("action")
        save.clicked.connect(lambda:(setattr(self,"notes_text",edit.toPlainText()),QMessageBox.information(w,"Notes","Saved for this session.")))
        box.addWidget(save);return w

    def calculator(self):
        w=AppWindow("Calculator",self,(430,230));box=QVBoxLayout(w);box.addWidget(QLabel("🧮  Calculator"))
        entry=QLineEdit();entry.setPlaceholderText("Example: (12 + 4) * 3");box.addWidget(entry);result=QLabel("Enter an expression");box.addWidget(result)
        ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow,ast.USub:operator.neg}
        def calc():
            try:
                def ev(n):
                    if isinstance(n,ast.Expression):return ev(n.body)
                    if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
                    if isinstance(n,ast.BinOp) and type(n.op) in ops:return ops[type(n.op)](ev(n.left),ev(n.right))
                    if isinstance(n,ast.UnaryOp) and type(n.op) in ops:return ops[type(n.op)](ev(n.operand))
                    raise ValueError("Only basic arithmetic is allowed")
                result.setText(str(ev(ast.parse(entry.text(),mode="eval"))))
            except Exception as ex:result.setText("Invalid expression: "+str(ex))
        b=QPushButton("Calculate");b.setObjectName("action");b.clicked.connect(calc);entry.returnPressed.connect(calc);box.addWidget(b);return w

    def settings(self):
        w=AppWindow("Settings",self,(650,440));box=QVBoxLayout(w);box.addWidget(QLabel("⚙️  Settings"))
        for k,v in (("Version",VERSION),("Mode","Windows-hosted desktop shell"),("Host",platform.node()),("OS",platform.platform()),("Python",platform.python_version()),("Hardware","ESP32 integration is a future milestone")):
            h=QLabel(k);h.setStyleSheet("font-weight:700;color:#8db7ff");box.addWidget(h);lab=QLabel(v);lab.setWordWrap(True);lab.setObjectName("muted");box.addWidget(lab)
        return w

    def about(self):
        w=AppWindow("About AMH-OS",self,(540,330));box=QVBoxLayout(w)
        h=QLabel("◈  AMH-OS");h.setStyleSheet("font-size:30px;font-weight:800");box.addWidget(h)
        d=QLabel("Desktop Environment • Version "+VERSION+"\n\nVersion 3.0 adds desktop context actions, Quick Settings preview, Notes, Calculator, app search and taskbar switching. This is a Windows-hosted prototype, not a standalone bootable OS.")
        d.setWordWrap(True);d.setObjectName("muted");box.addWidget(d);return w

    def keyPressEvent(self,event):
        if event.key()==Qt.Key.Key_F11:self.showNormal() if self.isFullScreen() else self.showFullScreen()
        elif event.key()==Qt.Key.Key_Escape:
            for attr in ("start_popup","quick_popup"):
                p=getattr(self,attr,None)
                if p:p.close();setattr(self,attr,None)
        elif event.key()==Qt.Key.Key_Q and event.modifiers()==(Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.ShiftModifier):self.close()
        else:super().keyPressEvent(event)

def main():
    app=QApplication(sys.argv);app.setApplicationName("AMH-OS");app.setStyle("Fusion");app.setStyleSheet(STYLE)
    desk=Desktop();desk.showFullScreen();sys.exit(app.exec())
if __name__=="__main__":main()
