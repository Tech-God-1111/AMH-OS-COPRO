"""UI mixin for the six interface-first AAPS desktop applications."""

from PySide6.QtWidgets import (
    QVBoxLayout, QGridLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView,
)


class ProcessingSuiteMixin:
    def module_dashboard(self, title, subtitle, metrics, headers, rows, notice):
        w=self.APP_WINDOW(title,self,(850,590)); box=QVBoxLayout(w)
        heading=QLabel(title); heading.setStyleSheet("font-size:23px;font-weight:800"); box.addWidget(heading)
        desc=QLabel(subtitle); desc.setObjectName("muted"); desc.setWordWrap(True); box.addWidget(desc)
        cards=QGridLayout()
        for index,(name,value,detail) in enumerate(metrics):
            card=QFrame(); card.setObjectName("popup"); card.setStyleSheet(self.APP_STYLE)
            layout=QVBoxLayout(card)
            label=QLabel(name); label.setObjectName("muted")
            number=QLabel(value); number.setStyleSheet("font-size:22px;font-weight:800;color:#8db7ff")
            small=QLabel(detail); small.setObjectName("muted"); small.setWordWrap(True)
            layout.addWidget(label); layout.addWidget(number); layout.addWidget(small)
            cards.addWidget(card,index//2,index%2)
        box.addLayout(cards)
        section=QLabel("OVERVIEW"); section.setStyleSheet("font-weight:800;color:#8db7ff;margin-top:8px")
        box.addWidget(section)
        table=QTableWidget(len(rows),len(headers)); table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for r,row in enumerate(rows):
            for c,value in enumerate(row):
                table.setItem(r,c,QTableWidgetItem(str(value)))
        table.setMinimumHeight(190); box.addWidget(table,1)
        note=QLabel(notice); note.setWordWrap(True); note.setObjectName("muted")
        note.setStyleSheet("background:#1a2940;border:1px solid #3b4e6d;border-radius:8px;padding:10px")
        box.addWidget(note)
        return w

    def workload_monitor(self):
        return self.module_dashboard(
            "Workload Monitor","Processor health and workload visibility for the AMH processing cluster.",
            [("ESP32-S3","Awaiting data","Master processor telemetry"),
             ("ESP32-WROOM","Awaiting data","Secondary processor telemetry"),
             ("Arduino Uno #1","Offline","Sub-processor worker"),
             ("Arduino Uno #2","Offline","Sub-processor worker")],
            ["Processor","CPU load","Free memory","Connection"],
            [["ESP32-S3","—","—","Not connected"],
             ["ESP32-WROOM","—","—","Not connected"],
             ["Arduino Uno #1","—","—","Not connected"],
             ["Arduino Uno #2","—","—","Not connected"]],
            "Interface preview only. Live CPU/load and memory readings will appear after the hardware telemetry protocol is implemented."
        )

    def task_scheduler(self):
        return self.module_dashboard(
            "Task Scheduler","Plan, prioritize and track work before the autonomous scheduling engine is connected.",
            [("Queued tasks","0","No jobs submitted"),
             ("Running tasks","0","No active workers"),
             ("Completed today","0","No execution history"),
             ("Scheduling mode","Manual preview","Autonomous mode planned")],
            ["Task ID","Task name","Priority","Preferred target","State"],
            [],
            "The scheduler interface is ready for the next stage. Automatic prioritization, worker selection and queue execution are not active yet."
        )

    def resource_manager(self):
        return self.module_dashboard(
            "Resource Manager","A unified view of processor capacity and resource limits.",
            [("S3 resources","Unknown","Awaiting telemetry"),
             ("WROOM resources","Unknown","Awaiting telemetry"),
             ("Uno #1 capacity","Unknown","ATmega328P worker"),
             ("Uno #2 capacity","Unknown","ATmega328P worker")],
            ["Node","Memory budget","Current usage","Admission state"],
            [["ESP32-S3","Pending telemetry","—","Unknown"],
             ["ESP32-WROOM","Pending telemetry","—","Unknown"],
             ["Arduino Uno #1","2 KB SRAM total","—","Offline"],
             ["Arduino Uno #2","2 KB SRAM total","—","Offline"]],
            "Resource-aware admission control will be implemented after each processor reports reliable capacity data. Uno memory is very limited, so task payloads must remain small."
        )

    def task_dispatcher(self):
        return self.module_dashboard(
            "Task Dispatcher","Prepare jobs for delivery to the best available processor or sub-processor.",
            [("Pending dispatch","0","No jobs waiting"),
             ("Available workers","0","Hardware links not connected"),
             ("Dispatch policy","Automatic","Planned policy"),
             ("Transport","UART","Protocol not configured")],
            ["Task ID","Payload","Selected worker","Dispatch state"],
            [],
            "This is the dispatch console preview. No serial commands are sent and no hardware tasks are launched in v10.0's interface-first stage."
        )

    def result_manager(self):
        return self.module_dashboard(
            "Result Manager","Review task outputs, completion metadata and verification state.",
            [("Results received","0","No worker responses"),
             ("Verified","0","No results to verify"),
             ("Rejected","0","No invalid results"),
             ("Last result","None","Waiting for execution")],
            ["Task ID","Worker","Result summary","Verification","Completed"],
            [],
            "Result collection, checksums, task-ID matching and validation will be added with the task communication protocol."
        )

    def recovery_manager(self):
        return self.module_dashboard(
            "Recovery Manager","Configure and observe timeout handling, retries and worker fault recovery.",
            [("Timeouts","0","No hardware sessions"),
             ("Retry attempts","0","No retry events"),
             ("Failed workers","0","No workers connected"),
             ("Recovery policy","Planned","Not active")],
            ["Policy","Current setting","Purpose"],
            [["Task timeout","To be configured","Detect unresponsive jobs"],
             ["Retry limit","To be configured","Bound repeated attempts"],
             ["Worker health check","To be configured","Detect disconnected workers"],
             ["Result validation","To be configured","Reject incomplete responses"]],
            "Recovery controls are intentionally inactive until task IDs, idempotency rules and hardware communication are implemented."
        )

