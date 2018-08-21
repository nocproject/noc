# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Parser loader
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
from .base import BaseParser

logger = logging.getLogger(__name__)


class ParserLoader(object):
    def __init__(self):
        self.parsers = {}  # Load parsers
        self.lock = threading.Lock()
        self.all_parsers = set()
        self.path = os.path.join(*self.__module__.split(".")[1:-1])
        self.mn_template = "%s.%%s" % self.__module__[:-7]
        self._choices = None

    def get_parser(self, name):
        """
        Load parser and return BaseParser instance.
        Returns None when no parser found or loading error occured
        """
        with self.lock:
            parser = self.parsers.get(name)
            if not parser:
                logger.info("Loading parser %s", name)
                if not self.is_valid_name(name):
                    logger.error("Invalid parser name")
                    return None
                module_name = self.mn_template % name
                try:
                    sm = __import__(module_name, {}, {}, "*")
                    for n in dir(sm):
                        o = getattr(sm, n)
                        if (
                            inspect.isclass(o) and
                            issubclass(o, BaseParser) and
                            o.__module__ == sm.__name__
                        ):
                            parser = o
                            break
                    if not parser:
                        logger.error("Parser not found: %s", name)
                except Exception as e:
                    logger.error("Failed to load parser %s: %s", name, e)
                self.parsers[name] = parser
            return parser

    def is_valid_name(self, name):
        return ".." not in name

    def find_parsers(self):
        """
        Scan all available parsers
        """
        ns = set()
        for fn in os.listdir(self.path):
            if fn.startswith(".") or fn.startswith("_") or not fn.endswith(".py"):
                continue
            if fn in ("base.py", "loader.py"):
                continue
            ns.add(fn[:-3])
        with self.lock:
            self.all_parsers = ns

    def iter_parsers(self):
        """
        Returns all available profile names
        """
        if not self.all_parsers:
            self.find_parsers()
        for s in sorted(self.all_parsers):
            yield s

    @property
    def choices(self):
        if self._choices is None:
            self._choices = []
            for p in self.iter_parsers():
                pc = self.get_parser(p)
                if pc:
                    self._choices += [(p, pc.name)]
        return self._choices


# Create singleton object
loader = ParserLoader()
