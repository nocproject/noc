# ----------------------------------------------------------------------
# Diagnostic Handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Any, Tuple, Iterable

# NOC modules
from noc.core.checkers.base import Check, CheckResult
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
        **kwargs,
    ) -> Tuple[DiagnosticState, Optional[str], Dict[str, Any], List[CheckStatus]]:
        """Local checks for L Policy Diagnostic Discovery"""

    def iter_checks(self, **kwargs) -> Iterable[Tuple[Check, ...]]:
        """Iterate over checks"""

    def get_result(
        self, checks: List[CheckResult]
    ) -> Tuple[Optional[bool], Optional[str], Dict[str, Any], List[CheckStatus]]:
        """Getting Diagnostic result"""
        state = None
        data = {}
        for c in checks:
            c = CheckStatus.from_result(c)
            if c.skipped:
                continue
            if not c.status and self.config.state_policy == "ALL":
                state = False
                break
            if c.status and self.config.state_policy == "ANY":
                state = True
                break
        if self.config.state_policy == "ANY" and checks and state is None:
            state = False
        return state, None, data, []
