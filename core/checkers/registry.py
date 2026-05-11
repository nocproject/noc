# ----------------------------------------------------------------------
# Works witch check on Group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from collections import defaultdict
from typing import List, Dict, Tuple, Iterable, Set

# NOC Modules
from noc.core.checkers.base import Check, CheckResult


class DiagnosticCheckRegister:
    """
    Register diagnostic checks for processed result
    """

    def __init__(self, logger=None):
        self.logger: logging.Logger = logger
        self.checks: Dict[str, Check] = {}
        self.w_checks: Dict[str, List[Check]] = defaultdict(list)  # Wildcard checks
        self.check_diagnostic_map: Dict[str, Set[str]] = defaultdict(set)
        self.affected_diagnostics: Dict[str, List[str]] = defaultdict(set)
        self.results: Dict[str, List[CheckResult]] = defaultdict(list)
        self.loaded: bool = False

    @property
    def is_loaded(self) -> bool:
        """Loaded all checks flag"""
        return self.loaded

    def add_checks(self, checks: List[Check], diagnostic: str):
        """Add check config"""
        for c in checks:
            self.checks[c.key] = c
            if c.has_wildcard:
                self.w_checks[c.name].append(c)
            self.check_diagnostic_map[c.key].add(diagnostic)

    def add_result(self, key: str, result: CheckResult):
        """Add result"""
        # Set TTL from config
        # result.ttl = result.ttl or self.checks[key].ttl or None
        self.results[key].append(result)
        for diag in self.check_diagnostic_map.get(key, []):
            self.affected_diagnostics[diag].add(result)

    def update_result(self, result: CheckResult):
        """Update check result"""
        if result.key not in self.checks and result.check not in self.w_checks:
            # Result for unknown Check
            self.logger.debug(
                "[%s|%s] Diagnostic not enabled: %s", result.check, result.key, self.checks
            )
            return
        # Add TTL
        if result.key in self.checks:
            self.add_result(result.key, result)
        if result.check not in self.w_checks:
            return
        # Processed wildcard
        for c in self.w_checks[result.check]:
            if c.is_match(result):
                self.add_result(c.key, result)

    def get_diagnostic_checks(self, diagnostic: str) -> List[CheckResult]:
        """Getting Active checks"""
        r = []
        for key in self.affected_diagnostics.get(diagnostic, []):
            if key in self.results:
                r += self.results[key]
        return r

    # def get_diagnostic_checks(
    #    self, diagnostic: str, allow_partial: bool = True
    # ) -> List[CheckResult]:
    #    """Getting Active checks"""
    #    r, partial = [], False
    #    for key in self.check_diagnostics.get(diagnostic, []):
    #        if key not in self.results:
    #            partial |= True
    #        else:
    #            r += self.results[key]
    #    if partial and not allow_partial:
    #        # Raise ?
    #        raise ValueError("Partial Result")
    #    return r

    def reset_result(self):
        """Reset processed result"""
        self.results = defaultdict(list)

    def iter_affected_diagnostics(self) -> Iterable[Tuple[str, List[CheckResult]]]:
        """Iter over Status Affected Diagnostics"""
        for d in self.affected_diagnostics:
            yield d, self.affected_diagnostics[d]
        self.affected_diagnostics = defaultdict(set)
