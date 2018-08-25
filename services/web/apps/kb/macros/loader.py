# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Macro loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import inspect
import os
import threading
# NOC modules
from .base import BaseMacro

logger = logging.getLogger(__name__)


class MacroLoader(object):
    def __init__(self):
        self.macros = {}  # Load macros
        self.lock = threading.Lock()
        self.all_macros = set()
        self.path = os.path.join(*self.__module__.split(".")[1:-1])
        self.mn_template = "%s.%%s" % self.__module__[:-7]
        self._choices = None

    def get_macro(self, name):
        """
        Load macro and return BaseMacro instance.
        Returns None when no macro found or loading error occured
        """
        with self.lock:
            macro = self.macros.get(name)
            if not macro:
                logger.info("Loading macro %s", name)
                if not self.is_valid_name(name):
                    logger.error("Invalid macro name")
                    return None
                module_name = self.mn_template % name
                try:
                    sm = __import__(module_name, {}, {}, "*")
                    for n in dir(sm):
                        o = getattr(sm, n)
                        if (
                            inspect.isclass(o) and
                            issubclass(o, BaseMacro) and
                            o.__module__ == sm.__name__
                        ):
                            macro = o
                            break
                    if not macro:
                        logger.error("Macro not found: %s", name)
                except Exception as e:
                    logger.error("Failed to load macro %s: %s", name, e)
                self.macros[name] = macro
            return macro

    def is_valid_name(self, name):
        return ".." not in name

    def find_macros(self):
        """
        Scan all available macros
        """
        ns = set()
        for fn in os.listdir(self.path):
            if fn.startswith(".") or fn.startswith("_") or not fn.endswith(".py"):
                continue
            if fn in ("base.py", "loader.py"):
                continue
            ns.add(fn[:-3])
        with self.lock:
            self.all_macros = ns

    def iter_macros(self):
        """
        Returns all available profile names
        """
        if not self.all_macros:
            self.find_macros()
        for s in sorted(self.all_macros):
            yield s

    def choices(self):
        if self._choices is None:
            self._choices = []
            for p in self.iter_macros():
                pc = self.get_macro(p)
                if pc:
                    self._choices += [(p, pc.name)]
        return self._choices


# Create singleton object
loader = MacroLoader()
