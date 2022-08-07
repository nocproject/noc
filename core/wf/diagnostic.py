# ----------------------------------------------------------------------
# @diagnostic decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass
from typing import Optional, List, Dict

EVENT_TRANSITION = {
    "disable": {"unknown": "blocked", "enabled": "blocked", "failed": "blocked"},
    "fail": {"unknown": "failed", "enabled": "failed"},
    "ok": {"unknown": "enabled", "failed": "enabled"},
    "allow": {"blocked": "unknown"},
    "expire": {"enabled": "unknown", "failed": "unknown"},
}

# BuiltIn Diagnostics
SNMP_DIAG = "SNMP"
PROFILE_DIAG = "Profile"
CLI_DIAG = "CLI"
HTTP_DIAG = "HTTP"
SYSLOG_DIAG = "SYSLOG"
SNMPTRAP_DIAG = "SNMPTRAP"


class DiagnosticEvent(str, enum.Enum):
    disable = "disable"
    fail = "fail"
    ok = "ok"
    allow = "allow"
    expire = "expire"

    def get_state(self, state: "DiagnosticState") -> Optional["DiagnosticState"]:
        if state.value not in EVENT_TRANSITION[self.value]:
            return
        return DiagnosticState(EVENT_TRANSITION[self.value][state.value])


class DiagnosticState(str, enum.Enum):
    unknown = "unknown"
    blocked = "blocked"
    enabled = "enabled"
    failed = "failed"

    def fire_event(self, event: str) -> "DiagnosticState":
        return DiagnosticEvent(event).get_state(self)

    @property
    def is_blocked(self) -> bool:
        return self.value == "blocked"


@dataclass(frozen=True)
class DiagnosticConfig(object):
    diagnostic: str
    blocked: bool = False  # Block by config
    # Check config
    checks: Optional[List[str]] = None  # CheckItem name, param
    dependent: Optional[List[str]] = None  # Dependency diagnostic
    # ANY - Any check has OK, ALL - ALL checks has OK
    state_policy: str = "ANY"  # Calculate State on checks.
    reason: Optional[str] = None  # Reason current state
    # Discovery Config
    run_policy: str = "A"  # A - Always, M - manual, F - Unknown or Failed, D - Disable
    run_order: str = "B"  # B - Before all discovery, A - After all discovery
    discovery_box: bool = False  # Run on periodic discovery
    discovery_periodic: bool = False  # Run on box discovery
    #
    save_history: bool = False
    # Display Config
    show_in_display: bool = True  # Show diagnostic on UI
    display_description: Optional[str] = None  # Description for show User
    display_order: int = 0  # Order on displayed list
    # FM Config
    alarm_class: Optional[str] = None  # Default AlarmClass for raise alarm


DIAGNOSTIC_CHECK_STATE: Dict[bool, DiagnosticState] = {
    True: DiagnosticState("enabled"),
    False: DiagnosticState("failed"),
}
