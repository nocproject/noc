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


class DiagnosticEvent(str, enum.Enum):
    disable = "disable"
    fail = "fail"
    ok = "ok"
    allow = "allow"
    expire = "expire"

    def get_state(self, state: "DiagnosticState") -> Optional["DiagnosticState"]:
        if state.value not in EVENT_TRANSITION[self.value]:
            print("Not allowed transition")
            return
        return DiagnosticState(EVENT_TRANSITION[self.value][state.value])

    @classmethod
    def print_transitions(cls):
        for event in EVENT_TRANSITION:
            event = DiagnosticEvent(event)
            for state1, state2 in EVENT_TRANSITION[event.value].items():
                print(f"{event}:  {DiagnosticState(state1)} ---> {DiagnosticState(state2)}")


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
    checks: Optional[List[str]] = None  # CheckItem name, param
    dependent: Optional[List[str]] = None  # Dependency diagnostic
    policy: str = "ANY"
    blocked: bool = False  # Block by config
    reason: Optional[str] = None


DIAGNOSTIC_CHECK_STATE: Dict[bool, DiagnosticState] = {
    True: DiagnosticState("enabled"),
    False: DiagnosticState("failed"),
}