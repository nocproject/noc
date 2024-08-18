# ----------------------------------------------------------------------
# Checkers loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import Checker


class CheckersLoader(BaseLoader):
    name = "checkers"
    base_cls = Checker
    base_path = ("services", "activator", "checkers")

    def __init__(self):
        super().__init__()
        self.checkers = {}
        self.load_checkers()

    def load_checkers(self):
        for checker in self:
            checker = self.get_class(checker)
            if not checker:
                continue
            for c in checker.CHECKS:
                self.checkers[c] = checker.name

    def get_class(self, name):
        name = self.checkers.get(name, name)
        return super().get_class(name)


# Create singleton object
loader = CheckersLoader()
