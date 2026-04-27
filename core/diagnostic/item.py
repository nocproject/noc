# ----------------------------------------------------------------------
# Diagnostic types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Iterable, Tuple, Union, Dict, Any

# Third-party modules
from pydantic import BaseModel, PrivateAttr

# NOC modules
from noc.core.checkers.base import Check, CheckResult, DataItem
from noc.core.models.inputsources import InputSource
from noc.core.handler import get_handler
from .handler import DiagnosticHandler
from .types import DiagnosticState, DiagnosticConfig, CheckStatus, DiagnosticValue


DIAGNOSTIC_CHECK_STATE: Dict[bool, DiagnosticState] = {
    True: DiagnosticState("enabled"),
    False: DiagnosticState("failed"),
}


class DiagnosticItem(BaseModel):
    """Class for Diagnostic Result description"""

    diagnostic: str
    state: DiagnosticState = DiagnosticState("unknown")
    checks: Optional[List[CheckStatus]] = None
    # scope: Literal["access", "all", "discovery", "default"] = "default"
    # policy: str = "ANY
    reason: Optional[str] = None
    changed: Optional[datetime.datetime] = None
    is_dirty: bool = False
    _config: Optional[DiagnosticConfig] = PrivateAttr()
    _handler: Optional[DiagnosticHandler] = PrivateAttr()

    def __init__(self, cfg: Optional[DiagnosticConfig] = None, **data):
        super().__init__(**data)
        self._config: DiagnosticConfig = cfg

    def __eq__(self, other: Union["DiagnosticItem", "DiagnosticValue"]) -> bool:
        """Compare diagnostic by value"""
        if self.diagnostic != other.diagnostic:
            return False
        return (
            self.state == other.state
            and self.checks == other.checks
            and self.reason == other.reason
            and self.changed == other.changed
        )

    @property
    def config(self):
        return self._config

    @property
    def show_in_display(self) -> bool:
        """Show Diagnostic Value on Display"""
        if (
            self.config.show_in_display
            and self.config.hide_enable
            and self.state == DiagnosticState.enabled
        ):
            return False
        return self.config.show_in_display

    @property
    def workflow_event(self) -> Optional[str]:
        if not self.config.workflow_event:
            return None
        if self.state not in (DiagnosticState.enabled, DiagnosticState.blocked):
            return self.config.workflow_event
        return None

    @property
    def is_active(self) -> bool:
        """
        Check diagnostic has worked: Enabled or Failed state
        """
        return self.state in (DiagnosticState.enabled, DiagnosticState.failed)

    @property
    def is_failed(self) -> bool:
        """Diagnostic on Failed state"""
        return self.state == DiagnosticState.failed

    @property
    def is_changed(self) -> bool:
        """Detect item changed"""
        return self.is_dirty

    def reset_changed(self):
        """Reset changed flag"""
        self.is_dirty = False

    @classmethod
    def from_config(
        cls,
        cfg: DiagnosticConfig,
        value: Optional[DiagnosticValue] = None,
    ) -> "DiagnosticItem":
        """Create item from config"""
        if cfg.blocked:
            state = DiagnosticState.blocked
        elif not value or value.state == DiagnosticState.blocked:
            state = cfg.default_state
        else:
            state = value.state
        return DiagnosticItem(
            cfg=cfg,
            diagnostic=cfg.diagnostic,
            state=state,
            checks=value.checks if value else None,
            reason=cfg.reason or None,
            changed=value.changed if value else None,
        )

    def reset(self, reason="Reset by"):
        """Reset diagnostic: clean checks and set default state"""
        if self.config.blocked:
            self.state = DiagnosticState.blocked
            self.reason = self.config.reason
        else:
            self.state = self.config.default_state
            self.reason = reason
        self.checks = []
        self.changed = datetime.datetime.now().replace(microsecond=0)

    def get_handler(self, logger=None) -> DiagnosticHandler:
        """Getting Diagnostic handler"""
        if not hasattr(self, "_handler"):
            h = get_handler(self.config.diagnostic_handler)
            if not h:
                raise AttributeError("Unknown Diagnostic Handler")
            try:
                self._handler = h(config=self.config, logger=logger)
            except TypeError as e:
                raise AttributeError(str(e))
        return self._handler

    def iter_checks(
        self,
        logger=None,
        **kwargs,
    ) -> Iterable[Tuple[Check, ...]]:
        """Iterate over configured checks"""
        if not self.config.diagnostic_handler and not self.config.checks:
            return
        elif not self.config.diagnostic_handler:
            yield tuple(self.config.checks)
            return
        h = self.get_handler(logger=logger)
        yield from h.iter_checks(**kwargs)

    def get_check_status(self) -> Tuple[Optional[DiagnosticState], Optional[str]]:
        """
        Calculate check status, ANY or ALL policy apply
        """
        if self.config.diagnostic_handler:
            h = self.get_handler()
            return h.get_check_status(self.checks)
        now = datetime.datetime.now()
        state = None
        # Check Expired
        for c in self.checks or []:
            if c.skipped:
                continue
            if c.is_expired(now):
                if not state:
                    state = self.config.default_state
                continue
            if not c.status and self.config.state_policy == "ALL":
                state = DiagnosticState.failed
                break
            if c.status and self.config.state_policy == "ANY":
                state = DiagnosticState.enabled
                break
        if self.config.state_policy == "ANY" and self.checks and state is None:
            state = DiagnosticState.failed
        # DiagnosticState
        return state, None

    def update_checks(
        self,
        checks: List[CheckResult],
        source: Optional[InputSource] = InputSource.UNKNOWN,
    ) -> Tuple[List[CheckStatus], List[DataItem]]:
        """Processed checks result and Update Item checks status"""
        if self.config.diagnostic_handler:
            h = self.get_handler()
            updated, data = h.process_result(checks, source=source)
        else:
            updated, data = [CheckStatus.from_result(c, source=source) for c in checks], []
        # Update status
        status = {c.name: c.status for c in self.checks or []}
        # Set is_dirty
        changed = False
        for c in updated or []:
            if c.name not in status or c.status != status[c.name]:
                changed = True
                break
        if changed:
            self.checks = updated
            # self.data = data
            self.is_dirty |= True
        return changed, data

    def get_object_form(self) -> Dict[str, Any]:
        """Displayed form"""
        return {
            "name": self.diagnostic[:6],
            "description": self.config.display_description,
            "state": self.state.value,
            "state__label": self.state.value,
            "details": [
                {
                    "name": c.name,
                    "state": {True: "OK", False: "Error"}[c.status],
                    "error": c.error,
                }
                for c in self.checks or []
                if not c.skipped
            ],
            "reason": self.reason or "",
        }

    def get_value(self) -> DiagnosticValue:
        """Return Diagnostic Value for save. Move to Model"""
        return DiagnosticValue(
            diagnostic=self.diagnostic,
            state=self.state,
            checks=self.checks,
            reason=self.reason or None,
            changed=self.changed,
        )
