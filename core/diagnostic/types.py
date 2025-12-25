# ----------------------------------------------------------------------
# Diagnostic types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
from dataclasses import dataclass
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.checkers.base import Check, CheckResult


class DiagnosticState(str, enum.Enum):
    """
    Diagnostic state class
     * unknown - initial state, with no other calculate
     * blocked - disable diagnostic by settings
     * enabled - checks pass by policy
     * failed - checks not pass by policy
    """

    unknown = "unknown"
    blocked = "blocked"
    enabled = "enabled"
    failed = "failed"

    @property
    def is_blocked(self) -> bool:
        return self.value == "blocked"

    @property
    def is_active(self) -> bool:
        return self.value not in ("blocked", "unknown")


@dataclass(frozen=True)
class CtxItem:
    """"""

    name: str
    value: Optional[str] = None
    capability: Optional[str] = None
    alias: Optional[str] = None
    set_method: Optional[str] = None

    @classmethod
    def from_string(cls, value: str) -> "CtxItem":
        """"""
        name, *v = value.split(":")
        if v:
            # Dynamic gen
            return CtxItem(name=name, value=v[0])
        return CtxItem(name=name)


@dataclass(frozen=True)
class DiagnosticConfig(object):
    """
    Configuration over diagnostic
    Attributes:
        diagnostic: Name configured diagnostic
        blocked: Block by config flag
        default_state: Default DiagnosticState
        checks: Configured diagnostic checks
        diagnostic_handler: Diagnostic result handler
        dependent: Dependency diagnostic
        include_credentials: Add credential to check context
        state_policy: Calculate State on checks. ANY - Any check has OK, ALL - ALL checks has OK
        reason: Reason current state. For blocked state
        check_discovery_policy: D - Disable, R - Discovery Running, L - Local Handler, A - Agent Active, P - Agent Passive
        run_policy: A - Always, M - manual, F - Unknown or Failed, D - Disable
        run_order: S - Before all discovery, E - After all discovery
        discovery_box: Run on Discovery Box
        discovery_periodic: Run on Periodic Discovery
        workflow_enabled_event: Send fire event when set enabled
        workflow_event: Send fire event on Diagnostic in Unknown/Failed state
        show_in_display: Show diagnostic on UI
        display_description: Description for show User
        display_order: Order on displayed list
        alarm_class: Default AlarmClass for raise alarm
    """

    diagnostic: str
    blocked: bool = False
    default_state: DiagnosticState = DiagnosticState.unknown
    # Check config
    checks: Optional[List[Check]] = None
    diagnostic_handler: Optional[str] = None
    dependent: Optional[List[str]] = None
    include_credentials: bool = False
    allow_set_credentials: bool = False
    diagnostic_ctx: Optional[List[CtxItem]] = None
    # Calculate State on checks.
    state_policy: str = "ANY"
    reason: Optional[str] = None
    # Discovery Config
    check_discovery_policy: str = "R"
    run_policy: str = "A"
    run_order: str = "S"
    discovery_box: bool = False
    discovery_periodic: bool = False
    workflow_enabled_event: Optional[str] = None
    workflow_event: Optional[str] = None
    save_history: bool = False
    # Display Config
    show_in_display: bool = True
    hide_enable: bool = False
    display_description: Optional[str] = None
    display_order: int = 0
    # FM Config
    alarm_class: Optional[str] = None
    alarm_labels: Optional[List[str]] = None

    @property
    def is_local_status(self):
        """Check if Local Calculate status"""
        return self.check_discovery_policy == "L"


class CheckStatus(BaseModel):
    """
    Result on execute checks
    Attributes:
        name: Check name
        status: Check execution result, True - OK, False - Fail
        arg0: Check params
        skipped: Check execution was skipped
        error: Error description for Fail status
    """

    name: str
    status: bool
    arg0: Optional[str] = None
    skipped: bool = False
    error: Optional[str] = None
    remote_system: Optional[str] = None

    @classmethod
    def from_result(cls, cr: CheckResult) -> "CheckStatus":
        return CheckStatus(
            name=cr.check,
            status=cr.status,
            skipped=cr.skipped,
            error=cr.error.message if cr.error else None,
            arg0=cr.arg0,
            remote_system=cr.remote_system,
        )


class DiagnosticValue(BaseModel):
    """
    Saved diagnostic state for Model
    """

    diagnostic: str
    state: DiagnosticState = DiagnosticState("unknown")
    checks: Optional[List[CheckStatus]] = None
    # scope: Literal["access", "all", "discovery", "default"] = "default"
    # policy: str = "ANY
    reason: Optional[str] = None
    changed: Optional[datetime.datetime] = None

    def get_check_state(self):
        # Any policy
        return any(c.status for c in self.checks if not c.skipped)
