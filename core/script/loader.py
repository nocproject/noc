# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Script loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import glob
import logging
import inspect
import os
import threading
## NOC modules
from base import BaseScript

logger = logging.getLogger(__name__)


class ScriptLoader(object):
    def __init__(self):
        self.scripts = {}  # Load scripts
        self.lock = threading.Lock()
        self.all_scripts = set()

    def get_script(self, name):
        """
        Load script and return BaseScript instance.
        Returns None when no script found or loading error occured
        """
        with self.lock:
            script = self.scripts.get(name)
            if not script:
                logger.info("Loading script %s", name)
                if not self.is_valid_name(name):
                    logger.error("Invalid script name")
                    return None
                module_name = "sa.profiles.%s" % name
                try:
                    sm = __import__(module_name, {}, {}, "*")
                    for n in dir(sm):
                        o = getattr(sm, n)
                        if (
                            inspect.isclass(o) and
                            issubclass(o, BaseScript) and
                            o.__module__ == sm.__name__
                        ):
                            script = o
                            break
                    if not script:
                        logger.error("Script not found: %s", name)
                except Exception, why:
                    logger.error("Failed to load script %s: %s", name, why)
                    script = None
                self.scripts[name] = script
            return script

    def reload(self):
        """
        Reset script cache and release all modules
        """
        with self.lock:
            logger.info("Reloading scripts")
            for s in self.scripts:
                logger.debug("Reload script %s", s.name)
                reload(sys.modules[s.__module__])
            self.scripts = {}
            self.all_scripts = set()

    def is_valid_name(self, name):
        return ".." not in name

    def find_scripts(self):
        """
        Scan all available scripts
        """
        ns = set()
        for path in glob.glob("sa/profiles/*/*/*.py"):
            vendor, system, name = path.split(os.sep)[-3:]
            name = name[:-3]
            if name != "__init__":
                ns.add("%s.%s.%s" % (vendor, system, name))
        with self.lock:
            self.all_scripts = ns

    def iter_scripts(self):
        """
        Returns all available script names
        """
        if not self.all_scripts:
            self.find_scripts()
        for s in sorted(self.all_scripts):
            yield s

    def has_script(self, name):
        """
        Check script is exists
        """
        if not self.all_scripts:
            self.find_scripts()
        return name in self.all_scripts

# Create singleton object
loader = ScriptLoader()
