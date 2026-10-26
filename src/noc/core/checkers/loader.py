# ----------------------------------------------------------------------
# Checkers loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from itertools import chain

# NOC modules
from noc.core.loader.base import BaseLoader
from noc.sa.interfaces.iping import IPing

from .base import BaseChecker


class CheckersLoader(BaseLoader):
    name = "checkers"
    base_cls = BaseChecker
    base_path = ("core", "checkers")
    ignored_names = {"base", "loader", "registry"}

    def __init__(self) -> None:
        super().__init__()
        self.checkers = {}
        self.script_checkers = {}
        self.load_checkers()

    def load_checkers(self):
        for checker in self:
            checker = self.get_class(checker)
            if not checker:
                continue
            for c in checker.CHECKS:
                self.checkers[c] = checker.name
        self.script_checkers[IPing.check] = IPing

    def get_class(self, name):
        name = self.checkers.get(name, name)
        return super().get_class(name)

    def is_script(self, name) -> bool:
        """Return if checker is ScriptChecker"""
        return name in self.script_checkers

    def choices(self):
        return [(p, p) for p in chain(self.checkers, self.script_checkers)]


# Create singleton object
loader = CheckersLoader()
