# ----------------------------------------------------------------------
# Diagnostic Handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Tuple, Iterable

# NOC modules
from noc.core.models.inputsources import InputSource
from noc.core.checkers.base import Check, CheckResult, DataItem
from .types import DiagnosticConfig, CheckStatus, DiagnosticState


class DiagnosticHandler:
    """
    Run diagnostic by config and check status
    """

    def __init__(self, config: DiagnosticConfig, logger=None):
        self.config = config
        self.logger = logger

    def get_check_status(
        self,
        checks: List[CheckStatus],
        **kwargs,
    ) -> Tuple[Optional[DiagnosticState], Optional[str]]:
        """Local checks for L Policy Diagnostic Discovery"""
        state = None
        # Default Status
        for c in checks:
            if c.skipped:
                continue
            if not c.status and self.config.state_policy == "ALL":
                state = DiagnosticState.failed
                break
            if c.status and self.config.state_policy == "ANY":
                state = DiagnosticState.enabled
                break
        if self.config.state_policy == "ANY" and checks and state is None:
            state = DiagnosticState.failed
        return state, None

    def iter_checks(self, **kwargs) -> Iterable[Tuple[Check, ...]]:
        """Iterate over checks"""

    def process_result(
        self,
        checks: List[CheckResult],
        source: Optional[InputSource] = InputSource.UNKNOWN,
    ) -> Tuple[List[CheckStatus], List[DataItem]]:
        """Processed checks result and Return Status"""
        return [CheckStatus.from_result(c, source=source) for c in checks], []
