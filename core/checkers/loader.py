# ----------------------------------------------------------------------
# Checkers loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from itertools import chain

# NOC modules
from noc.core.loader.base import BaseLoader
from noc.core.interface.loader import loader as sa_interface_loader
from .base import Checker


class CheckersLoader(BaseLoader):
    name = "checkers"
    base_cls = Checker
    base_path = ("services", "activator", "checkers")

    def __init__(self):
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
        for iface in sa_interface_loader.iter_interfaces():
            iface = sa_interface_loader.get_interface(iface)
            if iface.check:
                self.script_checkers[iface.check] = iface

    def get_class(self, name):
        name = self.checkers.get(name, name)
        return super().get_class(name)

    def is_script(self, name) -> bool:
        """Return if checker is ScriptChecker"""
        return name in self.script_checkers

    def get_interface_by_check(self, name):
        return self.script_checkers[name]

    def choices(self):
        return [(p, p) for p in chain(self.checkers, self.script_checkers)]


# Create singleton object
loader = CheckersLoader()
