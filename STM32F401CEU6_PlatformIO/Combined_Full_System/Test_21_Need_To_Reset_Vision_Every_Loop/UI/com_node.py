#!/usr/bin/env python3
"""
Vision -> Controller UI COM Node (ROS 2 Jazzy)

UPDATED to sync with your Controller UI code:

Controller UI now publishes on /finger_pattern_ack:
  RESET:UI_RESET_PRESSED

Required behavior added here:
- When RESET:UI_RESET_PRESSED is received on /finger_pattern_ack:
    1) Clear/forget any pending request and any auto-grab pending state
    2) Treat controller as NOT_IDLE (or UNKNOWN) until a new STATE arrives (we'll set UNKNOWN)
    3) Publish an acknowledgement back to controller UI on /finger_control_cmd:
         "reset_ack_rx"
    4) Publish updated /controller/state and /gripper/ideal_state

Everything else remains the same.
"""

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String as RosString
from std_msgs.msg import Bool as RosBool

TOPIC_SHAPE_LABEL = "/shape_label"
TOPIC_GRAB_READY  = "/grab_ready"

ROS_TOPIC_REQUEST = "/finger_pattern_request"
ROS_TOPIC_PATTERN = "/finger_pattern"
ROS_TOPIC_ACK     = "/finger_pattern_ack"
ROS_TOPIC_CMD     = "/finger_control_cmd"

# ---- Pattern mapping (updated names) ----
PATTERN_MAP = {
    "cylinder":          "11111",
    "planar":            "11110",  # flat -> planar
    "sphere":            "11111",
    "slender_cylinder":  "00111",  # thin -> slender_cylinder
    "cuboid":            "11111",
}

NO_OBJECT_PATTERN = "00000"
DEFAULT_PATTERN   = "11110"

# ✅ NEW: reset event from controller UI (your UI sends RESET:UI_RESET_PRESSED)
RESET_EVENT_PREFIX = "RESET:"
RESET_EVENT_PAYLOAD = "UI_RESET_PRESSED"
RESET_ACK_TO_CONTROLLER_UI = "reset_ack_rx"


class VisionPatternServer(Node):
    def __init__(self):
        super().__init__("vision_pattern_server")

        # ---- params ----
        self.declare_parameter("shape_topic", TOPIC_SHAPE_LABEL)
        self.declare_parameter("grab_ready_topic", TOPIC_GRAB_READY)

        self.declare_parameter("request_topic", ROS_TOPIC_REQUEST)
        self.declare_parameter("pattern_topic", ROS_TOPIC_PATTERN)
        self.declare_parameter("ack_topic", ROS_TOPIC_ACK)
        self.declare_parameter("cmd_topic", ROS_TOPIC_CMD)

        # REQUIRED CHANGE: publish controller state on a dedicated topic
        self.declare_parameter("state_topic", "/controller/state")

        # REQUIRED CHANGE: publish gripper ideal state
        self.declare_parameter("ideal_state_topic", "/gripper/ideal_state")

        self.declare_parameter("stale_timeout_s", 2.0)
        self.declare_parameter("wait_timeout_s", 0.6)
        self.declare_parameter("timer_period_s", 0.05)
        self.declare_parameter("log_every_n_shapes", 1)

        # auto-grab tuning
        self.declare_parameter("ack_fresh_window_s", 60.0)
        self.declare_parameter("grab_resend_period_s", 1.0)
        self.declare_parameter("state_query_period_s", 1.0)

        # ---- read params ----
        self.shape_topic      = str(self.get_parameter("shape_topic").value)
        self.grab_ready_topic = str(self.get_parameter("grab_ready_topic").value)
        self.request_topic    = str(self.get_parameter("request_topic").value)
        self.pattern_topic    = str(self.get_parameter("pattern_topic").value)
        self.ack_topic        = str(self.get_parameter("ack_topic").value)
        self.cmd_topic        = str(self.get_parameter("cmd_topic").value)

        # REQUIRED CHANGE
        self.state_topic      = str(self.get_parameter("state_topic").value)

        # REQUIRED CHANGE
        self.ideal_state_topic = str(self.get_parameter("ideal_state_topic").value)

        self.stale_timeout_s  = float(self.get_parameter("stale_timeout_s").value)
        self.wait_timeout_s   = float(self.get_parameter("wait_timeout_s").value)
        self.timer_period_s   = float(self.get_parameter("timer_period_s").value)
        self.log_every_n_shapes = int(self.get_parameter("log_every_n_shapes").value)

        self.ack_fresh_window_s   = float(self.get_parameter("ack_fresh_window_s").value)
        self.grab_resend_period_s = float(self.get_parameter("grab_resend_period_s").value)
        self.state_query_period_s = float(self.get_parameter("state_query_period_s").value)

        # ---- base pattern state ----
        self._last_shape = None
        self._last_shape_time = 0.0
        self._pending_request = False
        self._req_deadline = 0.0
        self._shape_rx_count = 0

        # ---- auto mode / controller tracking ----
        self._auto_mode = False
        self._remote_state = "UNKNOWN"  # IDLE / NOT_IDLE / UNKNOWN
        self._last_pattern_ack_time = 0.0

        self._grab_ready = False
        self._grab_pending = False
        self._grab_last_send_t = 0.0
        self._grab_ack_received = False

        self._last_state_query_t = 0.0

        # ---- pubs ----
        self.pub_pattern = self.create_publisher(RosString, self.pattern_topic, 10)
        self.pub_cmd     = self.create_publisher(RosString, self.cmd_topic, 10)

        # REQUIRED CHANGE: publish controller state
        self.pub_state   = self.create_publisher(RosString, self.state_topic, 10)

        # REQUIRED CHANGE: publish gripper ideal state
        self.pub_ideal_state = self.create_publisher(RosBool, self.ideal_state_topic, 10)

        # ---- subs ----
        self.sub_shape = self.create_subscription(RosString, self.shape_topic, self._on_shape_label, 10)
        self.sub_req   = self.create_subscription(RosString, self.request_topic, self._on_request, 10)
        self.sub_ack   = self.create_subscription(RosString, self.ack_topic, self._on_ack, 10)
        self.sub_grab_ready = self.create_subscription(RosBool, self.grab_ready_topic, self._on_grab_ready, 10)

        self._timer = self.create_timer(self.timer_period_s, self._on_timer)

        # REQUIRED CHANGE: publish initial state once
        self._publish_state()
        self._publish_ideal_state()

        self.get_logger().info(
            f"[COM] Started {self.get_name()}\n"
            f"[COM] sub shape:      {self.shape_topic}\n"
            f"[COM] sub request:    {self.request_topic}\n"
            f"[COM] pub pattern:    {self.pattern_topic}\n"
            f"[COM] sub ack:        {self.ack_topic}\n"
            f"[COM] pub cmd:        {self.cmd_topic}\n"
            f"[COM] sub grab_ready: {self.grab_ready_topic}\n"
            f"[COM] pub state:      {self.state_topic}\n"
            f"[COM] pub ideal:      {self.ideal_state_topic}\n"
            f"[COM] stale_timeout_s={self.stale_timeout_s} wait_timeout_s={self.wait_timeout_s}\n"
            f"[COM] ack_fresh_window_s={self.ack_fresh_window_s} grab_resend_period_s={self.grab_resend_period_s}\n"
        )

    # ---------- helpers ----------
    def _normalize_shape(self, shape: str) -> str:
        """Rename labels to your new names."""
        if not shape:
            return ""
        s = shape.strip().lower()
        if s == "thin":
            return "slender_cylinder"
        if s == "flat":
            return "planar"
        return s

    def _shape_to_pattern(self, shape: str) -> str:
        if not shape:
            return NO_OBJECT_PATTERN
        s = self._normalize_shape(shape)
        return PATTERN_MAP.get(s, DEFAULT_PATTERN)

    def _pattern_from_last_shape(self) -> str:
        if self._last_shape is None:
            return NO_OBJECT_PATTERN
        age = time.monotonic() - self._last_shape_time
        if age > self.stale_timeout_s:
            return NO_OBJECT_PATTERN
        return self._shape_to_pattern(self._last_shape)

    def _publish_pattern_once(self, pattern: str, reason: str):
        m = RosString()
        m.data = pattern
        self.pub_pattern.publish(m)
        self.get_logger().info(f"[COM] TX {self.pattern_topic}: {pattern} ({reason})")
        self._pending_request = False
        self._req_deadline = 0.0

    def _publish_cmd(self, text: str, reason: str = ""):
        m = RosString()
        m.data = text
        self.pub_cmd.publish(m)
        if reason:
            self.get_logger().info(f"[COM] TX {self.cmd_topic}: {text!r} ({reason})")
        else:
            self.get_logger().info(f"[COM] TX {self.cmd_topic}: {text!r}")

    # REQUIRED CHANGE: publish controller state on dedicated topic
    def _publish_state(self):
        m = RosString()
        m.data = self._remote_state
        self.pub_state.publish(m)

    # REQUIRED CHANGE: publish gripper ideal state on dedicated topic
    def _publish_ideal_state(self):
        m = RosBool()
        m.data = (self._remote_state == "IDLE")
        self.pub_ideal_state.publish(m)

    def _ack_is_fresh(self) -> bool:
        if self._last_pattern_ack_time <= 0:
            return False
        return (time.monotonic() - self._last_pattern_ack_time) <= self.ack_fresh_window_s

    def _maybe_query_state(self, why: str):
        now = time.monotonic()
        if (now - self._last_state_query_t) < self.state_query_period_s:
            return
        self._last_state_query_t = now
        self._publish_cmd("state?", reason=f"need controller state ({why})")

    def _auto_try_grab(self, why: str):
        if not self._auto_mode:
            return
        if not self._grab_ready:
            return

        if self._remote_state == "UNKNOWN":
            self._maybe_query_state("grab_ready but state UNKNOWN")
            return
        if self._remote_state != "IDLE":
            return

        if not self._ack_is_fresh():
            return

        if self._grab_pending:
            return

        self._grab_pending = True
        self._grab_ack_received = False
        self._grab_last_send_t = time.monotonic()
        self._publish_cmd("grab", reason=f"AUTO grab ({why})")

    # ✅ NEW: handle reset event coming from controller UI
    def _handle_controller_reset_event(self, payload: str):
        """
        Controller UI published: RESET:UI_RESET_PRESSED on /finger_pattern_ack
        We will:
          - Clear any pending request state
          - Cancel any auto-grab pending/resend loop
          - Mark controller state UNKNOWN until next STATE arrives
          - Ack back to controller UI on /finger_control_cmd
          - Publish updated /controller/state and /gripper/ideal_state
        """
        self.get_logger().info(f"[COM] Controller RESET event received: {payload!r}")

        # Cancel request wait
        self._pending_request = False
        self._req_deadline = 0.0

        # Cancel auto-grab resend loop
        self._grab_pending = False
        self._grab_ack_received = False
        self._grab_last_send_t = 0.0

        # Reset pattern freshness gate (optional but safer)
        self._last_pattern_ack_time = 0.0

        # State becomes unknown until we get fresh STATE:* from controller UI
        self._remote_state = "UNKNOWN"
        self._publish_state()
        self._publish_ideal_state()

        # Ack back to controller UI (UI listens on /finger_control_cmd)
        self._publish_cmd(RESET_ACK_TO_CONTROLLER_UI, reason="ack controller RESET event")

        # If auto mode is ON and grab_ready is true, we may query state again later
        if self._auto_mode and self._grab_ready:
            self._maybe_query_state("after controller reset")

    # ---------- callbacks ----------
    def _on_shape_label(self, msg: RosString):
        raw = (msg.data or "").strip()
        if not raw:
            return

        shape = self._normalize_shape(raw)
        self._last_shape = shape
        self._last_shape_time = time.monotonic()

        self._shape_rx_count += 1
        if self.log_every_n_shapes <= 1 or (self._shape_rx_count % self.log_every_n_shapes) == 0:
            note = ""
            if self._pending_request:
                note = f" | pending_request=True (deadline in {max(0.0, self._req_deadline - time.monotonic()):.2f}s)"
            self.get_logger().info(f"[COM] RX {self.shape_topic}: {raw!r} -> {shape!r}{note}")

        if self._pending_request:
            pat = self._pattern_from_last_shape()
            self._publish_pattern_once(pat, reason=f"reply-on-label shape='{self._last_shape}'")

    def _on_request(self, msg: RosString):
        data = (msg.data or "").strip().upper()
        self.get_logger().info(f"[COM] RX {self.request_topic}: {data!r}")
        if data != "REQ":
            return

        pat_now = self._pattern_from_last_shape()
        if pat_now != NO_OBJECT_PATTERN:
            self._publish_pattern_once(pat_now, reason=f"immediate-reply shape='{self._last_shape}'")
            return

        now = time.monotonic()
        self._pending_request = True
        self._req_deadline = now + self.wait_timeout_s
        self.get_logger().info("[COM] REQ received — waiting for next /shape_label...")

    def _on_grab_ready(self, msg: RosBool):
        self._grab_ready = bool(msg.data)
        if self._grab_ready:
            self._auto_try_grab("grab_ready TRUE")

    def _on_ack(self, msg: RosString):
        data = (msg.data or "").strip()
        if not data:
            return

        # ✅ NEW: reset event from controller UI
        if data.startswith(RESET_EVENT_PREFIX):
            payload = data[len(RESET_EVENT_PREFIX):].strip()
            # be tolerant: accept any RESET:* but log payload
            if payload == RESET_EVENT_PAYLOAD or payload:
                self._handle_controller_reset_event(payload)
            return

        # --- AUTO switch (from controller laptop UI) ---
        if data.startswith("AUTO:"):
            val = data[5:].strip().lower()

            if val == "on":
                self._auto_mode = True
                self.get_logger().info("[COM] AUTO mode ENABLED (AUTO:On).")
                self._publish_cmd("auto_on_ack", reason="ack AUTO:On received")

            elif val == "off":
                self._auto_mode = False
                self.get_logger().info("[COM] AUTO mode DISABLED (AUTO:Off).")
                self._grab_pending = False
                self._grab_ack_received = False
                self._publish_cmd("auto_off_ack", reason="ack AUTO:Off received")

            return

        # --- state updates from controller laptop UI ---
        if data.startswith("STATE:"):
            st = data[6:].strip().upper()

            if st == "IDLE":
                self._remote_state = "IDLE"
            elif st in ("NOT IDLE", "NOT_IDLE", "NOTIDLE"):
                self._remote_state = "NOT_IDLE"
            else:
                self._remote_state = "UNKNOWN"

            self.get_logger().info(f"[COM] Controller state update: {self._remote_state} (from {data!r})")

            self._publish_state()
            self._publish_ideal_state()

            self._publish_cmd(f"state_rx_{self._remote_state.lower()}", reason="state update received")

            if self._auto_mode and self._grab_ready:
                self._auto_try_grab("state updated")
            return

        # --- pattern ACK time (freshness gate for auto grab) ---
        if data.startswith("ACK:"):
            self._last_pattern_ack_time = time.monotonic()
            pat = data[4:].strip()
            self.get_logger().info(f"[COM] Got pattern ACK: {pat!r} (ack_time updated)")
            self._publish_cmd("ack_rx", reason="pattern ACK received")
            return

        # --- grab acknowledgement ---
        if data.startswith("STATUS:"):
            if "GrabStarted" in data:
                self.get_logger().info(f"[COM] Grab ACK received: {data!r}")
                self._grab_ack_received = True
                self._grab_pending = False
                self._remote_state = "NOT_IDLE"

                self._publish_state()
                self._publish_ideal_state()

                self._publish_cmd("grab_ack_rx", reason="STATUS:GrabStarted received")
            return

    def _on_timer(self):
        # request timeout
        if self._pending_request and time.monotonic() >= self._req_deadline:
            self._publish_pattern_once(NO_OBJECT_PATTERN, reason="timeout waiting for /shape_label")

        # auto resend grab if waiting for ack
        if self._auto_mode and self._grab_pending and not self._grab_ack_received:
            now = time.monotonic()
            if (now - self._grab_last_send_t) >= self.grab_resend_period_s:
                if self._remote_state == "IDLE" and self._grab_ready and self._ack_is_fresh():
                    self._grab_last_send_t = now
                    self._publish_cmd("grab", reason="resend (no ack yet)")
                elif self._remote_state == "UNKNOWN":
                    self._maybe_query_state("resend blocked: state UNKNOWN")


def main():
    rclpy.init()
    node = VisionPatternServer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
