#!/usr/bin/env python3
import sys
import time
import threading
import re
from collections import deque
from typing import Optional
from threading import Lock

from PySide6.QtCore import QObject, Signal, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox,
    QMessageBox, QComboBox, QScrollArea, QLineEdit,
    QGridLayout, QPlainTextEdit
)

import serial
import serial.tools.list_ports

# ----------------------------
# ROS 2 (Jazzy) imports
# ----------------------------
import rclpy
from rclpy.node import Node
from std_msgs.msg import String as RosString

# ----------------------------
# ROS topic names
# ----------------------------
ROS_TOPIC_REQUEST = "finger_pattern_request"   # UI -> vision laptop
ROS_TOPIC_PATTERN = "finger_pattern"           # vision laptop -> UI
ROS_TOPIC_ACK = "finger_pattern_ack"           # UI -> vision laptop (ACK + STATE + STATUS)
ROS_TOPIC_CMD = "finger_control_cmd"           # vision laptop -> UI (Grab / Idle? / State?)

PATTERN_RE = re.compile(r"^[01]{5}$")
STATE_RE = re.compile(r".*\[STATE\]\s+([A-Z_]+)\s*$")
FSR_RE = re.compile(r"^(?:\d+\s*,\s*)?FSR Live:\s*")
CURRENT_RE = re.compile(r"^\d+\s*,\s*\d+\s*,.*mA.*$")

ALLOWED_CMD_RE = re.compile(r"^(?:[01]{5}|2|3)$")

START_CMD_TO_MCU = "2"
RESET_CMD_TO_MCU = "3"


# ----------------------------
# Port helpers
# ----------------------------
def list_candidate_ports():
    ports = list(serial.tools.list_ports.comports())
    return [p.device for p in ports if ("ttyUSB" in p.device) or ("ttyACM" in p.device)]


def find_stm32_port():
    ports = list_candidate_ports()
    return ports[0] if ports else None


def classify_mcu_line(s: str) -> str:
    if not s:
        return "status"
    if STATE_RE.match(s):
        return "fsm"
    if FSR_RE.match(s):
        return "fsr"
    if CURRENT_RE.match(s) and (",") in s:
        return "current"
    return "status"


# ----------------------------
# Finger selection widget
# ----------------------------
class FingerTableWidget(QWidget):
    def __init__(self, finger_names):
        super().__init__()
        self.finger_names = finger_names

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        self.pattern_label = QLabel("Pattern: (none)")
        self.pattern_label.setAlignment(Qt.AlignCenter)
        self.pattern_label.setObjectName("patternCaption")

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(6)

        self._name_labels = []
        self._dot_labels = []

        for col, name in enumerate(self.finger_names):
            name_lbl = QLabel(name)
            name_lbl.setAlignment(Qt.AlignCenter)
            name_lbl.setObjectName("fingerName")
            self._name_labels.append(name_lbl)

            dot_lbl = QLabel("●")
            dot_lbl.setAlignment(Qt.AlignCenter)
            dot_lbl.setObjectName("fingerDot")
            self._dot_labels.append(dot_lbl)

            grid.addWidget(name_lbl, 0, col)
            grid.addWidget(dot_lbl, 1, col)

        root.addWidget(self.pattern_label)
        root.addLayout(grid)
        self.set_pattern(None)

    def set_pattern(self, pat: Optional[str]):
        if pat is None or not PATTERN_RE.match(pat):
            self.pattern_label.setText("Pattern: (none)")
            for dot in self._dot_labels:
                dot.setStyleSheet("color: #b0bec5; font-size: 22px;")
            return

        self.pattern_label.setText(f"Pattern: {pat}")
        for i, ch in enumerate(pat):
            if ch == "1":
                self._dot_labels[i].setStyleSheet("color: #2e7d32; font-size: 22px;")
            else:
                self._dot_labels[i].setStyleSheet("color: #c62828; font-size: 22px;")


# ----------------------------
# Serial manager
# ----------------------------
class SerialManager(QObject):
    sig_connected = Signal(str)
    sig_disconnected = Signal()
    sig_error = Signal(str)
    sig_rx_line = Signal(str)
    sig_log_line = Signal(str)

    def __init__(self):
        super().__init__()
        self._ser = None
        self._stop = False
        self._error_latched = False

    def is_connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    def connect_port(self, port: str, baud: int = 115200):
        if self.is_connected():
            self.sig_log_line.emit("Serial already connected.")
            return
        try:
            self._ser = serial.Serial(port, baud, timeout=0.2, exclusive=True)
            time.sleep(2.0)
            try:
                self._ser.reset_input_buffer()
            except Exception:
                pass

            self._stop = False
            self._error_latched = False
            threading.Thread(target=self._reader_loop, daemon=True).start()

            self.sig_connected.emit(port)
            self.sig_log_line.emit(f"Connected: {port} @ {baud} (exclusive)")
        except Exception as e:
            self._ser = None
            self.sig_error.emit(f"Serial connect failed: {e}")

    def disconnect_port(self):
        self._stop = True
        try:
            if self._ser:
                try:
                    self._ser.close()
                except Exception:
                    pass
        finally:
            self._ser = None

        self.sig_disconnected.emit()
        self.sig_log_line.emit("Disconnected.")

    def write_line_lf(self, text: str):
        if not self.is_connected():
            self.sig_error.emit("Not connected to serial.")
            return
        try:
            payload = (text + "\n").encode("utf-8", errors="replace")
            self._ser.write(payload)
            self._ser.flush()
            shown = text.replace("\r", "\\r").replace("\n", "\\n")
            self.sig_log_line.emit(f"TX: '{shown}' ending=LF bytes={payload!r}")
        except Exception as e:
            if not self._error_latched:
                self._error_latched = True
                self.sig_error.emit(f"Serial write failed: {e}")
            self.disconnect_port()

    def _reader_loop(self):
        while not self._stop:
            try:
                if not self._ser:
                    break
                raw = self._ser.readline()
                if not raw:
                    continue
                s = raw.decode("utf-8", errors="replace").strip()
                if not s:
                    continue
                self.sig_rx_line.emit(s)
                self.sig_log_line.emit(f"RX: {s}")

            except (serial.SerialException, OSError) as e:
                if not self._error_latched:
                    self._error_latched = True
                    self.sig_error.emit(f"Serial disconnected (device removed?): {e}")
                self.disconnect_port()
                break
            except Exception as e:
                if self._stop:
                    break
                if not self._error_latched:
                    self._error_latched = True
                    self.sig_error.emit(f"Serial read error: {e}")
                self.disconnect_port()
                break


# ----------------------------
# ROS worker
# ----------------------------
class RosPatternNode(Node):
    def __init__(self, outbound_queue: deque, q_lock: Lock,
                 sig_pattern_cb, sig_log_cb, sig_status_cb, sig_event_cb, sig_cmd_cb):
        super().__init__("ui_pattern_client")

        self._out_q = outbound_queue
        self._q_lock = q_lock
        self._sig_pattern_cb = sig_pattern_cb
        self._sig_log_cb = sig_log_cb
        self._sig_status_cb = sig_status_cb
        self._sig_event_cb = sig_event_cb
        self._sig_cmd_cb = sig_cmd_cb

        self.req_pub = self.create_publisher(RosString, ROS_TOPIC_REQUEST, 10)
        self.ack_pub = self.create_publisher(RosString, ROS_TOPIC_ACK, 10)

        self.sub_pattern = self.create_subscription(RosString, ROS_TOPIC_PATTERN, self._on_pattern, 10)
        self.sub_cmd = self.create_subscription(RosString, ROS_TOPIC_CMD, self._on_cmd, 10)

        self.timer = self.create_timer(0.05, self._flush_outbound)

        self._sig_log_cb(
            f"[ROS] Node started. pub={ROS_TOPIC_REQUEST}, sub={ROS_TOPIC_PATTERN}, cmd_sub={ROS_TOPIC_CMD}, out_pub={ROS_TOPIC_ACK}"
        )

        self._last_pattern_time = 0.0
        self._status_timer = self.create_timer(0.5, self._publish_status)

    def _flush_outbound(self):
        msg_to_send = None
        with self._q_lock:
            if self._out_q:
                msg_to_send = self._out_q.popleft()

        if msg_to_send is None:
            return

        m = RosString()
        m.data = msg_to_send

        if msg_to_send == "REQ":
            self.req_pub.publish(m)
            self._sig_log_cb(f"[ROS] Published request: {msg_to_send!r}")
            try:
                self._sig_event_cb("request_sent", msg_to_send)
            except Exception:
                pass
            return

        # Everything else -> ACK topic (ACK/STATE/STATUS/AUTO)
        self.ack_pub.publish(m)
        self._sig_log_cb(f"[ROS] Published out: {msg_to_send!r}")

        try:
            if msg_to_send.startswith("ACK:"):
                self._sig_event_cb("ack_sent", msg_to_send[4:])
            elif msg_to_send.startswith("STATE:"):
                self._sig_event_cb("state_sent", msg_to_send[6:])
            elif msg_to_send.startswith("STATUS:"):
                self._sig_event_cb("status_sent", msg_to_send[7:])
            elif msg_to_send.startswith("AUTO:"):
                self._sig_event_cb("auto_sent", msg_to_send[5:])
            else:
                self._sig_event_cb("out_sent", msg_to_send)
        except Exception:
            pass

    def _on_pattern(self, msg: RosString):
        data = (msg.data or "").strip()
        self._last_pattern_time = time.monotonic()
        self._sig_log_cb(f"[ROS] RX pattern: {data!r}")
        try:
            self._sig_event_cb("pattern_received", data)
        except Exception:
            pass
        self._sig_pattern_cb(data)

    def _on_cmd(self, msg: RosString):
        data = (msg.data or "").strip()
        if not data:
            return
        self._sig_log_cb(f"[ROS] RX cmd: {data!r}")
        try:
            self._sig_event_cb("cmd_received", data)
        except Exception:
            pass
        self._sig_cmd_cb(data)

    def _publish_status(self):
        pubs_on_pattern = 0
        subs_on_request = 0
        try:
            pubs_on_pattern = self.count_publishers(ROS_TOPIC_PATTERN)
        except Exception:
            pubs_on_pattern = -1

        try:
            subs_on_request = self.count_subscribers(ROS_TOPIC_REQUEST)
        except Exception:
            subs_on_request = -1

        now = time.monotonic()
        age = (now - self._last_pattern_time) if self._last_pattern_time > 0 else None

        status = {
            "pubs_on_pattern": pubs_on_pattern,
            "subs_on_request": subs_on_request,
            "last_pattern_age_s": age,
        }
        self._sig_status_cb(status)


class RosWorker(QObject):
    sig_log = Signal(str)
    sig_pattern = Signal(str)
    sig_ready = Signal(bool)
    sig_status = Signal(dict)
    sig_event = Signal(str, str)
    sig_cmd = Signal(str)

    def __init__(self):
        super().__init__()
        self._thread = None
        self._running = False

        self._out_q = deque()
        self._q_lock = Lock()

        self._executor = None
        self._node = None

    def start(self):
        if self._running:
            return
        self._running = True

        def runner():
            try:
                rclpy.init(args=None)
                self._executor = rclpy.executors.SingleThreadedExecutor()

                self._node = RosPatternNode(
                    outbound_queue=self._out_q,
                    q_lock=self._q_lock,
                    sig_pattern_cb=lambda s: self.sig_pattern.emit(s),
                    sig_log_cb=lambda s: self.sig_log.emit(s),
                    sig_status_cb=lambda d: self.sig_status.emit(d),
                    sig_event_cb=lambda ev, payload: self.sig_event.emit(ev, payload),
                    sig_cmd_cb=lambda s: self.sig_cmd.emit(s),
                )
                self._executor.add_node(self._node)
                self.sig_ready.emit(True)
                self._executor.spin()
            except Exception as e:
                self.sig_log.emit(f"[ROS] ERROR: {e}")
                self.sig_ready.emit(False)
            finally:
                try:
                    if self._executor and self._node:
                        self._executor.remove_node(self._node)
                        self._node.destroy_node()
                except Exception:
                    pass
                try:
                    if rclpy.ok():
                        rclpy.shutdown()
                except Exception:
                    pass
                self._running = False

        self._thread = threading.Thread(target=runner, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            if self._executor:
                self._executor.shutdown()
        except Exception:
            pass
        self._running = False

    def _queue_out(self, msg: str):
        with self._q_lock:
            self._out_q.append(msg)

    def request_pattern(self):
        self._queue_out("REQ")

    def publish_ack(self, pat: str):
        self._queue_out(f"ACK:{pat}")

    def publish_state_idle(self):
        self._queue_out("STATE:Idle")

    def publish_state_not_idle(self):
        self._queue_out("STATE:Not Idle")

    def publish_state_unknown(self):
        self._queue_out("STATE:Unknown")

    def publish_status(self, text: str):
        if not text.startswith("STATUS:"):
            text = "STATUS:" + text
        self._queue_out(text)

    # ✅ NEW: Auto mode ON/OFF announce (sent on ROS_TOPIC_ACK so receiver already listens there)
    def publish_auto_mode(self, on: bool):
        self._queue_out("AUTO:On" if on else "AUTO:Off")


# ----------------------------
# UI
# ----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.serial_mgr = SerialManager()

        self.ros = RosWorker()
        self.ros.start()

        # Modes
        self.manual_mode_on = False
        self.auto_mode_on = False

        # ROS status vars
        self._ros_local_ok = False
        self._ros_status_dict = {"pubs_on_pattern": 0, "subs_on_request": 0, "last_pattern_age_s": None}

        # transient ROS event text (second line)
        self._ros_event_text = ""
        self._ros_event_color = "#455a64"
        self._ros_event_timer = QTimer(self)
        self._ros_event_timer.setSingleShot(True)
        self._ros_event_timer.timeout.connect(self._clear_ros_event)

        self._latest_pattern: Optional[str] = None
        self._pattern_sent_to_mcu: bool = False
        self._waiting_for_pattern = False

        # Track MCU FSM state
        self._last_state: Optional[str] = None
        self._pending_idle_publish_after_reset = False

        self.setWindowTitle("Robotic End Effector Control UI (Serial + ROS2 Pattern)")
        self.setMinimumWidth(1050)

        # queues
        self._rx_q = deque(maxlen=5000)
        self._log_q = deque(maxlen=5000)

        self._flush_timer = QTimer(self)
        self._flush_timer.setInterval(50)
        self._flush_timer.timeout.connect(self._flush_queues)
        self._flush_timer.start()

        self._state_flash_timer = QTimer(self)
        self._state_flash_timer.setSingleShot(True)
        self._state_flash_timer.timeout.connect(self._end_state_flash)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setSpacing(12)

        title = QLabel("Robotic End Effector Control Panel")
        title.setObjectName("title")
        root.addWidget(title)

        # ---------------- Mode Selection ----------------
        mode_group = QGroupBox("Mode Selection")
        mode_layout = QHBoxLayout()

        self.btn_manual_mode = QPushButton("Manual Mode")
        self.btn_auto_mode = QPushButton("Auto Mode")

        self.btn_manual_mode.setCheckable(True)
        self.btn_auto_mode.setCheckable(True)

        self.mode_status = QLabel("Mode: OFF (select Manual or Auto)")
        self.mode_status.setObjectName("modeStatus")

        mode_layout.addWidget(self.btn_manual_mode)
        mode_layout.addWidget(self.btn_auto_mode)
        mode_layout.addWidget(self.mode_status, stretch=1)
        mode_group.setLayout(mode_layout)
        root.addWidget(mode_group)

        # ---------------- Connection ----------------
        conn_group = QGroupBox("Connection (MCU Serial)")
        conn_layout = QHBoxLayout()

        self.port_combo = QComboBox()
        self.btn_refresh_ports = QPushButton("Refresh Ports")
        self.btn_auto = QPushButton("Auto-Detect")
        self.btn_connect = QPushButton("Connect")
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setEnabled(False)

        self.port_status = QLabel("Status: Not connected")
        self.port_status.setObjectName("portStatus")

        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.port_combo, stretch=1)
        conn_layout.addWidget(self.btn_refresh_ports)
        conn_layout.addWidget(self.btn_auto)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.btn_disconnect)
        conn_layout.addWidget(self.port_status, stretch=2)
        conn_group.setLayout(conn_layout)
        root.addWidget(conn_group)

        # =========================
        # Manual Mode Section
        # =========================
        self.manual_group = QGroupBox("Manual Mode Controls")
        manual_layout = QVBoxLayout()

        ros_group = QGroupBox("Vision Pattern (Manual)")
        ros_layout = QHBoxLayout()
        self.btn_request_pattern_manual = QPushButton("Request Pattern (ROS)")
        self.btn_send_pattern_mcu = QPushButton("Send Pattern to MCU")
        self.btn_send_pattern_mcu.setEnabled(False)
        ros_layout.addWidget(self.btn_request_pattern_manual)
        ros_layout.addWidget(self.btn_send_pattern_mcu)
        ros_group.setLayout(ros_layout)
        manual_layout.addWidget(ros_group)

        ctrl_group = QGroupBox("Controls (Manual)")
        ctrl_layout = QHBoxLayout()
        self.btn_start = QPushButton("  Start Grasping  ")
        self.btn_reset_open_manual = QPushButton("  Reset/Open  ")
        self.btn_clear = QPushButton("Clear UI")
        ctrl_layout.addWidget(self.btn_start)
        ctrl_layout.addWidget(self.btn_reset_open_manual)
        ctrl_layout.addStretch(1)
        ctrl_layout.addWidget(self.btn_clear)
        ctrl_group.setLayout(ctrl_layout)
        manual_layout.addWidget(ctrl_group)

        tx_group = QGroupBox("Manual Send (Debug) — Only allowed: 5-bit pattern OR 2 OR 3")
        tx_layout = QHBoxLayout()
        self.tx_input = QLineEdit()
        self.tx_input.setPlaceholderText("Type 00000..11111, or 2, or 3 then Enter")
        self.btn_send = QPushButton("Send")
        tx_layout.addWidget(QLabel("Command:"))
        tx_layout.addWidget(self.tx_input, stretch=2)
        tx_layout.addWidget(self.btn_send)
        tx_group.setLayout(tx_layout)
        manual_layout.addWidget(tx_group)

        self.manual_group.setLayout(manual_layout)
        root.addWidget(self.manual_group)

        # =========================
        # Auto Mode Section
        # =========================
        self.auto_group = QGroupBox("Auto Mode Controls")
        auto_layout = QHBoxLayout()

        self.btn_request_pattern_auto = QPushButton("Request Pattern (Auto)")
        self.btn_reset_open_auto = QPushButton("Reset/Open (Auto)")
        self.btn_reset_open_auto.setToolTip("Sends reset/open command to MCU and will publish STATE:Idle when MCU reports IDLE.")

        self.ros_status = QLabel("ROS: starting...")
        self.ros_status.setObjectName("rosStatus")
        self.ros_status.setTextFormat(Qt.RichText)

        auto_layout.addWidget(self.btn_request_pattern_auto)
        auto_layout.addWidget(self.btn_reset_open_auto)
        auto_layout.addWidget(self.ros_status, stretch=1)
        self.auto_group.setLayout(auto_layout)
        root.addWidget(self.auto_group)

        # ---------------- Active fingers + FSM state ----------------
        info_group = QGroupBox("Grasp Selection + FSM State")
        info_layout = QHBoxLayout()

        self.active_fingers_widget = FingerTableWidget(["Little", "Ring", "Middle", "Index", "Thumb"])

        self.fsm_state_label = QLabel("Waiting for MCU state...")
        self.fsm_state_label.setAlignment(Qt.AlignCenter)
        self.fsm_state_label.setMinimumHeight(90)
        self.fsm_state_label.setObjectName("fsmStateLabel")

        info_layout.addWidget(self._wrap_box("Active Fingers", self.active_fingers_widget), stretch=1)
        info_layout.addWidget(self._wrap_box("FSM State", self.fsm_state_label), stretch=1)
        info_group.setLayout(info_layout)
        root.addWidget(info_group)

        # ---------------- FSR / Current / Status / Debug ----------------
        fsr_group = QGroupBox("FSR Values (FSR Live: ...)")
        fsr_layout = QVBoxLayout()
        self.fsr_box = QPlainTextEdit()
        self.fsr_box.setReadOnly(True)
        self.fsr_box.setUndoRedoEnabled(False)
        self.fsr_box.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.fsr_box.setMinimumHeight(160)
        self.fsr_box.setMaximumBlockCount(100)
        fsr_layout.addWidget(self.fsr_box)
        fsr_group.setLayout(fsr_layout)
        root.addWidget(fsr_group)

        cur_group = QGroupBox("Current Values (millis,pulse, ...)")
        cur_layout = QVBoxLayout()
        self.current_box = QPlainTextEdit()
        self.current_box.setReadOnly(True)
        self.current_box.setUndoRedoEnabled(False)
        self.current_box.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.current_box.setMinimumHeight(160)
        self.current_box.setMaximumBlockCount(100)
        cur_layout.addWidget(self.current_box)
        cur_group.setLayout(cur_layout)
        root.addWidget(cur_group)

        status_group = QGroupBox("MCU Status / Other Messages")
        status_layout = QVBoxLayout()
        self.status_box = QPlainTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setUndoRedoEnabled(False)
        self.status_box.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.status_box.setMinimumHeight(180)
        self.status_box.setMaximumBlockCount(150)
        status_layout.addWidget(self.status_box)
        status_group.setLayout(status_layout)
        root.addWidget(status_group)

        log_group = QGroupBox("Debug Log (Serial + ROS)")
        log_layout = QVBoxLayout()
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setUndoRedoEnabled(False)
        self.log_box.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.log_box.setMinimumHeight(160)
        self.log_box.setMaximumBlockCount(200)
        log_layout.addWidget(self.log_box)
        log_group.setLayout(log_layout)
        root.addWidget(log_group)

        scroll.setWidget(content)
        win_layout = QVBoxLayout(self)
        win_layout.addWidget(scroll)

        self.apply_theme()

        # ---------------- signals (mode) ----------------
        self.btn_manual_mode.clicked.connect(self.toggle_manual_mode)
        self.btn_auto_mode.clicked.connect(self.toggle_auto_mode)

        # ---------------- signals (serial) ----------------
        self.btn_refresh_ports.clicked.connect(self.refresh_ports)
        self.btn_auto.clicked.connect(self.auto_detect_port)
        self.btn_connect.clicked.connect(self.connect_serial)
        self.btn_disconnect.clicked.connect(self.disconnect_serial)

        self.btn_start.clicked.connect(self.start_grasp_guarded)
        self.btn_reset_open_manual.clicked.connect(self.reset_open_pressed)
        self.btn_reset_open_auto.clicked.connect(self.reset_open_pressed)
        self.btn_clear.clicked.connect(self.clear_ui)

        self.btn_send.clicked.connect(self.send_from_ui)
        self.tx_input.returnPressed.connect(self.send_from_ui)

        self.serial_mgr.sig_connected.connect(self.on_serial_connected)
        self.serial_mgr.sig_disconnected.connect(self.on_serial_disconnected)
        self.serial_mgr.sig_error.connect(self.on_error)
        self.serial_mgr.sig_rx_line.connect(self._enqueue_rx_line)
        self.serial_mgr.sig_log_line.connect(self._enqueue_log_line)

        # ---------------- signals (ROS) ----------------
        self.btn_request_pattern_manual.clicked.connect(self.request_pattern_ros_manual)
        self.btn_send_pattern_mcu.clicked.connect(self.send_ros_pattern_to_mcu)
        self.btn_request_pattern_auto.clicked.connect(self.request_pattern_ros_auto)

        self.ros.sig_log.connect(self._enqueue_log_line)
        self.ros.sig_ready.connect(self.on_ros_ready)
        self.ros.sig_pattern.connect(self.on_ros_pattern_received)
        self.ros.sig_status.connect(self.on_ros_status)
        self.ros.sig_event.connect(self.on_ros_event)
        self.ros.sig_cmd.connect(self.on_ros_cmd_received)

        self.refresh_ports()
        self.active_fingers_widget.set_pattern(None)
        self._set_state_display("Waiting for MCU state...", is_boot=True)

        self._update_ros_status_label()
        self._apply_mode_ui()

    def closeEvent(self, event):
        try:
            self.ros.stop()
        except Exception:
            pass
        super().closeEvent(event)

    # ✅ helper: check if ROS remote peers exist (same logic as label)
    def _ros_connected_to_peer(self) -> bool:
        if not self._ros_local_ok:
            return False
        pubs = self._ros_status_dict.get("pubs_on_pattern", 0)
        subs = self._ros_status_dict.get("subs_on_request", 0)
        have_remote_pattern_pub = (pubs is not None and pubs >= 1)
        have_remote_request_sub = (subs is not None and subs >= 1)
        return bool(have_remote_pattern_pub and have_remote_request_sub)

    # ---------------- Mode helpers ----------------
    def toggle_manual_mode(self):
        want_on = self.btn_manual_mode.isChecked()
        if want_on:
            self.btn_auto_mode.blockSignals(True)
            self.btn_auto_mode.setChecked(False)
            self.btn_auto_mode.blockSignals(False)
            self.manual_mode_on = True
            self.auto_mode_on = False
            self._enqueue_log_line("[UI] Manual Mode ENABLED.")
            self._set_ros_event("mode", "Manual ON", "#0b3d91")

            # Optional: announce auto is OFF (only if ROS connected)
            if self._ros_connected_to_peer():
                self.ros.publish_auto_mode(False)
                self._enqueue_log_line("[ROS] Published AUTO:Off (manual enabled).")
                self._set_ros_event("auto", "AUTO:Off sent", "#455a64")
        else:
            self.manual_mode_on = False
            self._enqueue_log_line("[UI] Manual Mode DISABLED.")
            self._set_ros_event("mode", "Manual OFF", "#455a64")
        self._apply_mode_ui()

    def toggle_auto_mode(self):
        want_on = self.btn_auto_mode.isChecked()
        if want_on:
            self.btn_manual_mode.blockSignals(True)
            self.btn_manual_mode.setChecked(False)
            self.btn_manual_mode.blockSignals(False)
            self.auto_mode_on = True
            self.manual_mode_on = False
            self._enqueue_log_line("[UI] Auto Mode ENABLED.")
            self._set_ros_event("mode", "Auto ON", "#6a1b9a")

            # ✅ NEW: when Auto Mode enabled, announce to other laptop if ROS connected
            if self._ros_connected_to_peer():
                self.ros.publish_auto_mode(True)
                self._enqueue_log_line("[ROS] Published AUTO:On (auto enabled).")
                self._set_ros_event("auto", "AUTO:On sent", "#6a1b9a")
            else:
                self._enqueue_log_line("[ROS] Auto ON not sent (ROS not connected to peer).")
                self._set_ros_event("auto", "AUTO:On not sent (no ROS peer)", "#f57c00")
        else:
            self.auto_mode_on = False
            self._enqueue_log_line("[UI] Auto Mode DISABLED.")
            self._set_ros_event("mode", "Auto OFF", "#455a64")

            # Optional: announce auto is OFF (only if ROS connected)
            if self._ros_connected_to_peer():
                self.ros.publish_auto_mode(False)
                self._enqueue_log_line("[ROS] Published AUTO:Off (auto disabled).")
                self._set_ros_event("auto", "AUTO:Off sent", "#455a64")
        self._apply_mode_ui()

    def _apply_mode_ui(self):
        if self.manual_mode_on:
            self.mode_status.setText("Mode: MANUAL (ON)")
        elif self.auto_mode_on:
            self.mode_status.setText("Mode: AUTO (ON)")
        else:
            self.mode_status.setText("Mode: OFF (select Manual or Auto)")

        self.manual_group.setEnabled(self.manual_mode_on)
        self.auto_group.setEnabled(self.auto_mode_on)

    # ---------------- ROS label helpers ----------------
    def _set_ros_event(self, _ev: str, text: str, color: str):
        self._ros_event_text = text
        self._ros_event_color = color
        self._update_ros_status_label()
        self._ros_event_timer.start(2000)

    def _clear_ros_event(self):
        self._ros_event_text = ""
        self._ros_event_color = "#455a64"
        self._update_ros_status_label()

    def _update_ros_status_label(self):
        if not self._ros_local_ok:
            base_msg = "ROS: not started / init failed"
            base_color = "#c62828"
        else:
            pubs = self._ros_status_dict.get("pubs_on_pattern", 0)
            subs = self._ros_status_dict.get("subs_on_request", 0)
            age = self._ros_status_dict.get("last_pattern_age_s", None)

            have_remote_pattern_pub = (pubs is not None and pubs >= 1)
            have_remote_request_sub = (subs is not None and subs >= 1)

            if have_remote_pattern_pub and have_remote_request_sub:
                base_msg = "ROS: connected (no pattern yet)" if age is None else f"ROS: connected (last pattern {age:.1f}s ago)"
                base_color = "#2e7d32"
            elif have_remote_request_sub and not have_remote_pattern_pub:
                base_msg = "ROS: request link OK, but no pattern publisher found"
                base_color = "#f57c00"
            elif have_remote_pattern_pub and not have_remote_request_sub:
                base_msg = "ROS: pattern publisher found, but no request subscriber found"
                base_color = "#f57c00"
            else:
                base_msg = "ROS: local OK, but no remote peer detected"
                base_color = "#c62828"

        if self._ros_event_text:
            html = (
                f"<div style='font-weight:900; color:{base_color};'>{base_msg}</div>"
                f"<div style='font-weight:900; color:{self._ros_event_color};'>{self._ros_event_text}</div>"
            )
        else:
            html = f"<div style='font-weight:900; color:{base_color};'>{base_msg}</div>"

        self.ros_status.setText(html)

    # ---------------- queues/log ----------------
    def _enqueue_log_line(self, s: str):
        self._log_q.append(s)

    def _enqueue_rx_line(self, s: str):
        self._rx_q.append(s)

    # ---------------- ROS callbacks ----------------
    def on_ros_ready(self, ok: bool):
        self._ros_local_ok = bool(ok)
        if not ok:
            self._enqueue_log_line("[ROS] Not ready. Did you source ROS 2 Jazzy before running this UI?")
        self._update_ros_status_label()

    def on_ros_status(self, d: dict):
        self._ros_status_dict = d or self._ros_status_dict
        self._update_ros_status_label()

    def on_ros_event(self, ev: str, payload: str):
        ev = (ev or "").strip()
        payload = (payload or "").strip()

        if ev == "request_sent":
            self._set_ros_event(ev, "Request sent → vision", "#1565c0")
        elif ev == "pattern_received":
            self._set_ros_event(ev, f"Pattern RX: {payload}", "#2e7d32")
        elif ev == "ack_sent":
            self._set_ros_event(ev, f"ACK sent ({payload})", "#6a1b9a")
        elif ev == "state_sent":
            self._set_ros_event(ev, f"STATE sent ({payload})", "#00838f")
        elif ev == "status_sent":
            self._set_ros_event(ev, f"STATUS sent ({payload})", "#37474f")
        elif ev == "auto_sent":
            self._set_ros_event(ev, f"AUTO sent ({payload})", "#6a1b9a")
        elif ev == "cmd_received":
            self._set_ros_event(ev, f"CMD RX: {payload}", "#4e342e")
        else:
            self._set_ros_event(ev, f"ROS: {ev}", "#455a64")

    # ---------------- request pattern (manual/auto) ----------------
    def request_pattern_ros_manual(self):
        if not self.manual_mode_on:
            QMessageBox.warning(self, "Mode off", "Enable Manual Mode first.")
            return
        self._waiting_for_pattern = True
        self._pattern_sent_to_mcu = False
        self.btn_send_pattern_mcu.setEnabled(False)
        self.ros.request_pattern()
        self._enqueue_log_line("[MANUAL] Requested pattern (ROS).")

    def request_pattern_ros_auto(self):
        if not self.auto_mode_on:
            QMessageBox.warning(self, "Mode off", "Enable Auto Mode first.")
            return
        self._waiting_for_pattern = True
        self._pattern_sent_to_mcu = False
        self.btn_send_pattern_mcu.setEnabled(False)
        self.ros.request_pattern()
        self._enqueue_log_line("[AUTO] Requested pattern (ROS).")

    def on_ros_pattern_received(self, pat: str):
        if not self._waiting_for_pattern:
            self._enqueue_log_line(f"[UI] Ignored ROS pattern (not requested): {pat}")
            return

        pat = (pat or "").strip()
        if not PATTERN_RE.match(pat):
            self._enqueue_log_line(f"[UI] BLOCKED ROS pattern (not 5-bit): {pat!r}")
            self._set_ros_event("pattern_bad", "Pattern rejected (not 5-bit)", "#c62828")
            return

        self._waiting_for_pattern = False
        self._latest_pattern = pat
        self._pattern_sent_to_mcu = False

        self.active_fingers_widget.set_pattern(pat)
        self._enqueue_log_line(f"[UI] Pattern stored: {pat}")

        if self.auto_mode_on:
            self.ros.publish_ack(pat)
            self._enqueue_log_line(f"[AUTO] Published ACK:{pat}")

            self._publish_state_reply(reason="after ACK")

            if self.serial_mgr.is_connected():
                self.serial_mgr.write_line_lf(pat)
                self._pattern_sent_to_mcu = True
                self._enqueue_log_line(f"[AUTO] Sent pattern to MCU immediately: {pat}")
                self._set_ros_event("auto", "Auto: ACK+STATE sent; pattern→MCU", "#6a1b9a")
            else:
                self._enqueue_log_line("[AUTO] MCU not connected. Pattern saved for later.")
                self._set_ros_event("auto", "Auto: ACK+STATE sent; no serial", "#f57c00")

        else:
            self.btn_send_pattern_mcu.setEnabled(True)
            self.ros.publish_ack(pat)
            self._enqueue_log_line(f"[MANUAL] Published ACK:{pat}")

    # ---------------- AUTO: respond to CMD ----------------
    def on_ros_cmd_received(self, cmd: str):
        cmd_raw = (cmd or "").strip()
        cmd_norm = cmd_raw.lower().strip()

        if not self.auto_mode_on:
            self._enqueue_log_line(f"[UI] ROS CMD ignored (auto mode off): {cmd_raw}")
            self._set_ros_event("cmd", "CMD ignored (auto OFF)", "#455a64")
            return

        if cmd_norm in ("idle?", "state?", "idle", "state"):
            self._publish_state_reply(reason=f"on cmd {cmd_raw!r}")
            return

        if cmd_norm == "grab":
            self._enqueue_log_line("[AUTO] CMD Grab received.")
            self._handle_auto_grab()
            return

        self._enqueue_log_line(f"[AUTO] CMD unknown: {cmd_raw}")
        self.ros.publish_status(f"STATUS:UnknownCmd({cmd_raw})")
        self._set_ros_event("cmd", f"Unknown CMD: {cmd_raw}", "#c62828")

    def _publish_state_reply(self, reason: str = ""):
        st = (self._last_state or "").strip().upper()
        if self._last_state is None:
            self.ros.publish_state_unknown()
            self._enqueue_log_line(f"[AUTO] Published STATE:Unknown ({reason})")
            self._set_ros_event("state", "Reply STATE: Unknown", "#8e24aa")
            return

        if st == "IDLE":
            self.ros.publish_state_idle()
            self._enqueue_log_line(f"[AUTO] Published STATE:Idle ({reason})")
            self._set_ros_event("state", "Reply STATE: Idle", "#00838f")
        else:
            self.ros.publish_state_not_idle()
            self._enqueue_log_line(f"[AUTO] Published STATE:Not Idle ({reason})")
            self._set_ros_event("state", f"Reply STATE: Not Idle ({st})", "#00838f")

    def _handle_auto_grab(self):
        if not self._latest_pattern or not PATTERN_RE.match(self._latest_pattern):
            self._enqueue_log_line("[AUTO] Grab blocked: no valid pattern stored.")
            self.ros.publish_status("STATUS:GrabBlocked(NoPattern)")
            self._set_ros_event("grab", "Grab blocked: No pattern", "#c62828")
            return

        if self._last_state is None:
            self._enqueue_log_line("[AUTO] Grab blocked: MCU state unknown (no [STATE] received yet).")
            self.ros.publish_status("STATUS:GrabBlocked(StateUnknown)")
            self._set_ros_event("grab", "Grab blocked: State Unknown", "#8e24aa")
            self.ros.publish_state_unknown()
            return

        if (self._last_state or "").strip().upper() != "IDLE":
            self._enqueue_log_line(f"[AUTO] Grab blocked: state is {self._last_state}, not IDLE.")
            self.ros.publish_status("STATUS:GrabBlocked(NotIdle)")
            self._set_ros_event("grab", f"Grab blocked: Not Idle ({self._last_state})", "#f57c00")
            return

        if not self.serial_mgr.is_connected():
            self._enqueue_log_line("[AUTO] Grab blocked: MCU serial not connected.")
            self.ros.publish_status("STATUS:GrabBlocked(NoSerial)")
            self._set_ros_event("grab", "Grab blocked: No serial", "#c62828")
            return

        if not self._pattern_sent_to_mcu:
            self.serial_mgr.write_line_lf(self._latest_pattern)
            self._pattern_sent_to_mcu = True
            self._enqueue_log_line(f"[AUTO] Sent pattern to MCU: {self._latest_pattern}")

        self._send_allowed(START_CMD_TO_MCU)
        self._enqueue_log_line(f"[AUTO] Sent Start ({START_CMD_TO_MCU}) to MCU.")
        self.ros.publish_status("STATUS:GrabStarted")
        self._set_ros_event("grab", f"Grab started (sent {START_CMD_TO_MCU})", "#2e7d32")

    # ---------------- Manual: send pattern to MCU ----------------
    def send_ros_pattern_to_mcu(self):
        if self._latest_pattern is None:
            QMessageBox.warning(self, "No pattern", "No ROS pattern received yet.")
            return
        if not self._ensure_connected():
            return

        self.serial_mgr.write_line_lf(self._latest_pattern)
        self._pattern_sent_to_mcu = True
        self._enqueue_log_line(f"[MANUAL] Sent pattern to MCU: {self._latest_pattern}")

    # ---------------- Reset/Open behavior (works in both modes) ----------------
    def reset_open_pressed(self):
        if not self._ensure_connected():
            return
        self.serial_mgr.write_line_lf(RESET_CMD_TO_MCU)
        self._pending_idle_publish_after_reset = True
        self._enqueue_log_line(f"[UI] Reset/Open sent to MCU ({RESET_CMD_TO_MCU}). Waiting for MCU to report IDLE...")
        if self.auto_mode_on:
            self._set_ros_event("reset", "Reset sent; waiting for IDLE…", "#1565c0")

    # ---------------- MCU state display ----------------
    def _state_color(self, st: str) -> str:
        st = (st or "").strip().upper()
        return {
            "IDLE": "#eef7ff",
            "RESETTING": "#fff8e1",
            "CLOSING_FAST": "#e8f5e9",
            "CLOSING_SLOW": "#f1f8e9",
            "TIGHTEN": "#fff3e0",
            "HOLD": "#ede7f6",
            "SETTLE": "#eceff1",
            "RECOVER": "#e3f2fd",
        }.get(st, "#f5f5f5")

    def _set_state_display(self, st: str, is_boot: bool = False):
        safe = (st or "").strip()
        bg = self._state_color(safe)

        if safe:
            self._last_state = safe

        self.fsm_state_label.setText(safe if safe else "—")

        if not is_boot:
            self.fsm_state_label.setStyleSheet(
                f"QLabel {{ background: {bg}; border: 2px solid #90a4ae; border-radius: 10px; padding: 8px; "
                f"font-size: 26px; font-weight: 800; }}"
            )
            self._state_flash_timer.start(250)
        else:
            self.fsm_state_label.setStyleSheet(
                f"QLabel {{ background: {bg}; border: 1px solid #cfd8dc; border-radius: 10px; padding: 8px; "
                f"font-size: 26px; font-weight: 800; }}"
            )

        if self._pending_idle_publish_after_reset and safe.strip().upper() == "IDLE":
            self._pending_idle_publish_after_reset = False
            if self.auto_mode_on:
                self.ros.publish_state_idle()
                self._enqueue_log_line("[AUTO] MCU reached IDLE after reset -> published STATE:Idle.")
                self._set_ros_event("state", "STATE sent: Idle (after reset)", "#00838f")

    def _end_state_flash(self):
        current = self._last_state or ""
        bg = self._state_color(current)
        self.fsm_state_label.setStyleSheet(
            f"QLabel {{ background: {bg}; border: 1px solid #cfd8dc; border-radius: 10px; padding: 8px; "
            f"font-size: 26px; font-weight: 800; }}"
        )

    # ---------------- Flush queues ----------------
    def _flush_queues(self):
        pulled = []
        for _ in range(min(400, len(self._rx_q))):
            pulled.append(self._rx_q.popleft())

        log_pulled = []
        for _ in range(min(400, len(self._log_q))):
            log_pulled.append(self._log_q.popleft())

        if not pulled and not log_pulled:
            return

        fsr_lines = []
        cur_lines = []
        status_lines = []
        new_state = None

        for s in pulled:
            kind = classify_mcu_line(s)
            if kind == "fsr":
                fsr_lines.append(s)
            elif kind == "current":
                cur_lines.append(s)
            elif kind == "fsm":
                m = STATE_RE.match(s)
                if m:
                    new_state = m.group(1)
                status_lines.append(s)
            else:
                status_lines.append(s)

        if fsr_lines:
            self.fsr_box.appendPlainText("\n".join(fsr_lines))
        if cur_lines:
            self.current_box.appendPlainText("\n".join(cur_lines))
        if status_lines:
            self.status_box.appendPlainText("\n".join(status_lines))
        if log_pulled:
            self.log_box.appendPlainText("\n".join(log_pulled))

        if new_state:
            self._set_state_display(new_state)

    # ---------------- UI helpers ----------------
    def _wrap_box(self, title: str, widget: QWidget) -> QWidget:
        box = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        box.setLayout(layout)
        return box

    def clear_ui(self):
        self.active_fingers_widget.set_pattern(None)
        self._set_state_display("Waiting for MCU state...", is_boot=True)
        self.fsr_box.clear()
        self.current_box.clear()
        self.status_box.clear()
        self.log_box.clear()
        self._latest_pattern = None
        self._pattern_sent_to_mcu = False
        self.btn_send_pattern_mcu.setEnabled(False)
        self._clear_ros_event()

    # ---------------- Serial connection ----------------
    def refresh_ports(self):
        self.port_combo.clear()
        ports = list_candidate_ports()
        if not ports:
            self.port_combo.addItem("(no ttyUSB/ttyACM found)")
            self.port_combo.setEnabled(False)
        else:
            self.port_combo.setEnabled(True)
            for p in ports:
                self.port_combo.addItem(p)
        self._enqueue_log_line("Ports refreshed.")

    def auto_detect_port(self):
        port = find_stm32_port()
        if not port:
            self.on_error("No serial port detected.")
            return
        idx = self.port_combo.findText(port)
        if idx < 0:
            self.port_combo.addItem(port)
            idx = self.port_combo.findText(port)
        self.port_combo.setCurrentIndex(idx)
        self._enqueue_log_line(f"Auto-detected port: {port}")

    def connect_serial(self):
        if not self.port_combo.isEnabled():
            self.on_error("No valid serial port selected.")
            return
        port = self.port_combo.currentText().strip()
        self.serial_mgr.connect_port(port, 115200)

    def disconnect_serial(self):
        self.serial_mgr.disconnect_port()

    def on_serial_connected(self, port: str):
        self.port_status.setText(f"Status: Connected to {port}")
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        self._enqueue_log_line("Connected to MCU.")

        if self.auto_mode_on and self._latest_pattern and PATTERN_RE.match(self._latest_pattern) and not self._pattern_sent_to_mcu:
            self.serial_mgr.write_line_lf(self._latest_pattern)
            self._pattern_sent_to_mcu = True
            self._enqueue_log_line(f"[AUTO] Serial connected -> sent stored pattern to MCU: {self._latest_pattern}")
            self._set_ros_event("auto", "Auto: pattern→MCU after connect", "#6a1b9a")

    def on_serial_disconnected(self):
        self.port_status.setText("Status: Not connected")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)

    def _ensure_connected(self) -> bool:
        if not self.serial_mgr.is_connected():
            QMessageBox.warning(self, "Not connected", "Connect to STM32 first.")
            return False
        return True

    def _sanitize_cmd(self, raw: str) -> str:
        if raw is None:
            return ""
        raw = raw.replace("\x00", "").strip()
        return "".join(ch for ch in raw if ch in "0123")

    def _send_allowed(self, text: str):
        if not self._ensure_connected():
            return

        cleaned = self._sanitize_cmd(text)
        if cleaned != text.strip():
            self._enqueue_log_line(f"[UI] Cleaned input: {text!r} -> {cleaned!r}")

        if not ALLOWED_CMD_RE.match(cleaned):
            self._enqueue_log_line(f"[UI] BLOCKED: Only allowed: 5-bit pattern OR '2' OR '3'. Got: {cleaned!r}")
            QMessageBox.warning(self, "Blocked", "Only allowed: 00000..11111, or 2, or 3.")
            return

        if PATTERN_RE.match(cleaned):
            self.active_fingers_widget.set_pattern(cleaned)

        if cleaned == RESET_CMD_TO_MCU:
            self.active_fingers_widget.set_pattern(None)

        self.serial_mgr.write_line_lf(cleaned)

    def send_from_ui(self):
        raw = self.tx_input.text()
        if not raw:
            return
        self._send_allowed(raw)
        self.tx_input.clear()

    def start_grasp_guarded(self):
        if not self.manual_mode_on:
            QMessageBox.warning(self, "Mode off", "Enable Manual Mode first.")
            return
        if not self._ensure_connected():
            return
        if not self._pattern_sent_to_mcu:
            QMessageBox.warning(
                self,
                "Pattern not sent",
                "You must Send Pattern to MCU before starting grasp.\n\nWorkflow:\n1) Request Pattern (ROS)\n2) Send Pattern to MCU\n3) Start Grasping"
            )
            return
        self._send_allowed(START_CMD_TO_MCU)

    def on_error(self, msg: str):
        self._enqueue_log_line(f"ERROR: {msg}")

        if not self.serial_mgr.is_connected():
            return

        now = time.time()
        if not hasattr(self, "_last_err_popup_t"):
            self._last_err_popup_t = 0.0
            self._last_err_popup_msg = ""

        if msg == self._last_err_popup_msg and (now - self._last_err_popup_t) < 3.0:
            return
        if (now - self._last_err_popup_t) < 1.2:
            return

        self._last_err_popup_t = now
        self._last_err_popup_msg = msg
        QMessageBox.critical(self, "Error", msg)

    def apply_theme(self):
        self.setStyleSheet("""
        QWidget { background-color: #f4f6f8; color: #111111; font-size: 13px; }
        #title { font-size: 20px; font-weight: bold; color: #0b3d91; margin-bottom: 10px; }
        QGroupBox { border: 1px solid #cfd8dc; border-radius: 10px; margin-top: 10px;
                    padding: 10px; background: white; font-weight: bold; }
        QPlainTextEdit, QComboBox, QLineEdit {
            background: #ffffff; color: #000000; border: 1px solid #cfd8dc;
            border-radius: 6px; padding: 6px;
        }
        QPushButton { background-color: #1976d2; color: white; border-radius: 8px;
                      padding: 10px; font-weight: bold; }
        QPushButton:hover { background-color: #1565c0; }
        QPushButton:pressed { background-color: #0d47a1; }
        QPushButton:disabled { background-color: #90a4ae; color: #f5f5f5; }

        /* mode buttons */
        QPushButton#modeManual, QPushButton#modeAuto { background-color: #546e7a; }
        QPushButton#modeManual:checked { background-color: #2e7d32; }
        QPushButton#modeAuto:checked { background-color: #6a1b9a; }

        #portStatus { color: #2e7d32; font-weight: 700; }
        #modeStatus { color: #0b3d91; font-weight: 900; }
        QLabel#fingerName { font-weight: 700; color: #263238; }
        QLabel#patternCaption { color: #607d8b; font-weight: 700; }
        """)

        self.btn_manual_mode.setObjectName("modeManual")
        self.btn_auto_mode.setObjectName("modeAuto")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
